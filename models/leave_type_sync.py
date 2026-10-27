# LOT RH 1B: keeps the legacy `leave_types` string array (GlobalConfig/CompanyConfig) in
# sync with the relational LeaveType rows introduced in LOT RH 1A, so every existing reader
# of that array (human_resource_management.serializers.leave.LeaveRequestSerializer via
# project_management.serializers.time_expense.get_valid_choices, and the Sync/Reset actions
# in companyprofileapis/views/company.py) keeps working unchanged.
#
# Shared by both Django projects that install this app (`backend` and `admin-server-backend`),
# since GlobalConfig and CompanyConfig both expose the same `leave_type_definitions` related
# manager and `leave_types` array field.


def sync_leave_types_array(config):
    """Recompute `config.leave_types` from the config's active LeaveType rows (effective
    `is_active`, resolving inheritance), and save only when it actually changed.
    LOT L04 (SST): a type marked `is_sst_managed` is never selectable from the
    classic leave request form -- excluded here too, so every reader of this
    legacy array (never only the dedicated `applicable`/`admin_applicable`
    endpoints) stays consistent."""
    names = [
        leave_type.name
        for leave_type in config.leave_type_definitions.all().order_by("id")
        if leave_type.effective_value("is_active") and not leave_type.is_sst_managed
    ]
    if config.leave_types != names:
        config.leave_types = names
        config.save(update_fields=["leave_types"])


def reset_leave_type_overrides(company_config):
    """"Reset Congés": clear LOCAL field overrides on every company-scope LeaveType --
    both ones that inherit from an Admin-scope type (revert to pure inheritance) AND
    complementary ones with no parent (revert to the Admin-configured organization
    defaults, read live by effective_value -- see LeaveType._organization_default).
    Sub-types and LeaveRequest history are never touched; this only clears overrides,
    it never deletes rows."""
    for leave_type in company_config.leave_type_definitions.all():
        for field_name in leave_type.INHERITABLE_FIELDS:
            setattr(leave_type, field_name, None)
        leave_type.save(update_fields=list(leave_type.INHERITABLE_FIELDS))
