# LOT RH 1B: backfill LeaveType rows from the existing GlobalConfig/CompanyConfig
# `leave_types` string arrays, so every company that already has leave type labels
# gets equivalent relational rows without losing any existing LeaveRequest compatibility
# (the string arrays themselves are left untouched; see sync_leave_types_array in
# human_resource_management for how new API writes keep both in sync going forward).
#
# Scope: company_profile-owned configs only (freelancer/user-owned GlobalConfig/CompanyConfig
# rows are not covered -- the 1B spec only describes Admin/Company(-entreprise) isolation).
#
# Defaults applied, chosen to exactly preserve current runtime behavior (see human_resource_
# management/utils.py calculate_leave_days and serializers/leave.py balance exclusion):
#   - deduction_mode = working_days (np.busday_count is the only counting logic today)
#   - allow_half_day = False, requires_supporting_document = False (neither exists today)
#   - consumes_balance = False only for labels matching "sick"/"unpaid" case-insensitively,
#     mirroring the existing hardcoded ecpmpapp.constants.LeaveType exclusion in the balance
#     calculation; True otherwise.
#   - cycle_start_date/cycle_end_date = Jan 1 - Dec 31 of the year the migration runs,
#     matching the existing START_YEAR/END_YEAR (= date.today().year) convention.
import re
from datetime import date

from django.db import migrations


def _slug_for(name, taken):
    candidate = re.sub(r"[^-a-zA-Z0-9_]+", "-", name.strip()).strip("-") or "type"
    key = candidate
    suffix = 1
    while key in taken:
        suffix += 1
        key = f"{candidate}-{suffix}"
    taken.add(key)
    return key


def _defaults_for(name):
    today = date.today()
    return dict(
        is_active=True,
        deduction_mode="working_days",
        cycle_start_date=date(today.year, 1, 1),
        cycle_end_date=date(today.year, 12, 31),
        allow_half_day=False,
        requires_supporting_document=False,
        consumes_balance=name.strip().lower() not in {"sick", "unpaid"},
    )


def backfill_leave_types(apps, schema_editor):
    GlobalConfig = apps.get_model("models", "GlobalConfig")
    CompanyConfig = apps.get_model("models", "CompanyConfig")
    LeaveType = apps.get_model("models", "LeaveType")

    admin_rows_by_company = {}

    for global_config in GlobalConfig.objects.filter(
        company_profile__isnull=False
    ).exclude(leave_types=[]):
        taken_keys = set()
        rows_by_name = admin_rows_by_company.setdefault(
            global_config.company_profile_id, {}
        )
        for name in global_config.leave_types:
            if not name or not name.strip():
                continue
            key = _slug_for(name, taken_keys)
            row, _ = LeaveType.objects.get_or_create(
                global_config=global_config,
                key=key,
                defaults=dict(name=name, **_defaults_for(name)),
            )
            rows_by_name[name.strip().lower()] = row

    for company_config in CompanyConfig.objects.filter(
        company_profile__isnull=False
    ).exclude(leave_types=[]):
        taken_keys = set()
        admin_rows = admin_rows_by_company.get(company_config.company_profile_id, {})
        for name in company_config.leave_types:
            if not name or not name.strip():
                continue
            key = _slug_for(name, taken_keys)
            parent = admin_rows.get(name.strip().lower())
            if parent is not None:
                LeaveType.objects.get_or_create(
                    company_config=company_config,
                    key=key,
                    defaults=dict(name=name, inherits_from=parent),
                )
            else:
                LeaveType.objects.get_or_create(
                    company_config=company_config,
                    key=key,
                    defaults=dict(name=name, **_defaults_for(name)),
                )


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0131_leave_type_configuration"),
    ]

    operations = [
        migrations.RunPython(backfill_leave_types, migrations.RunPython.noop),
    ]
