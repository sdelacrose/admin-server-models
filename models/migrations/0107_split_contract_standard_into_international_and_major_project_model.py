from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


INTERNATIONAL_STANDARDS = {
    "FIDIC Red Book",
    "FIDIC Yellow Book",
    "FIDIC Silver Book",
    "FIDIC White Book",
    "NEC3",
    "NEC4",
}
MAJOR_PROJECT_MODELS = {
    "BOOT",
    "BOT",
    "PPP",
    "PFI",
}
DEFAULT_INTERNATIONAL_STANDARDS = [
    "FIDIC Red Book",
    "FIDIC Yellow Book",
    "FIDIC Silver Book",
    "FIDIC White Book",
    "NEC3",
    "NEC4",
]
DEFAULT_MAJOR_PROJECT_MODELS = [
    "BOOT",
    "BOT",
    "PPP",
    "PFI",
]


def _partition_values(values):
    current = list(values or [])
    international = [item for item in current if item in INTERNATIONAL_STANDARDS]
    major = [item for item in current if item in MAJOR_PROJECT_MODELS]
    # Preserve any custom values that are not in either default set by appending
    # them to international_standard so they are not dropped.
    known = INTERNATIONAL_STANDARDS | MAJOR_PROJECT_MODELS
    customs = [item for item in current if item not in known]
    international.extend(customs)
    return international, major


def _seed_list(current, defaults):
    existing = list(current or [])
    for item in defaults:
        if item not in existing:
            existing.append(item)
    return existing


def split_contract_standard(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        to_update = []
        for obj in model.objects.all().only(
            "id",
            "contract_standard",
            "international_standard",
            "major_project_model",
        ):
            international, major = _partition_values(getattr(obj, "contract_standard", []))
            obj.international_standard = _seed_list(
                international, DEFAULT_INTERNATIONAL_STANDARDS
            )
            obj.major_project_model = _seed_list(major, DEFAULT_MAJOR_PROJECT_MODELS)
            to_update.append(obj)
        if to_update:
            model.objects.bulk_update(
                to_update, ["international_standard", "major_project_model"]
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0106_remove_six_sigma_and_utilities"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="international_standard",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="globalconfig",
            name="major_project_model",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="international_standard",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="major_project_model",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.RunPython(split_contract_standard, noop_reverse),
        migrations.RemoveField(
            model_name="globalconfig",
            name="contract_standard",
        ),
        migrations.RemoveField(
            model_name="companyconfig",
            name="contract_standard",
        ),
    ]
