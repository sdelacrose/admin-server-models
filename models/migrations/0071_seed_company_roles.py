from django.db import migrations


DEFAULT_COMPANY_ROLES = [
    "Company Role #1",
    "Company Role #2",
    "Company Role #3",
]


def seed_company_roles(apps, schema_editor):
    GlobalConfig = apps.get_model("models", "GlobalConfig")
    CompanyConfig = apps.get_model("models", "CompanyConfig")

    GlobalConfig.objects.filter(company_roles=[]).update(
        company_roles=DEFAULT_COMPANY_ROLES
    )

    global_config_by_user_id = {
        config.user_id: list(config.company_roles or DEFAULT_COMPANY_ROLES)
        for config in GlobalConfig.objects.exclude(user_id=None).only(
            "user_id", "company_roles"
        )
    }
    global_config_by_company_id = {
        config.company_profile_id: list(config.company_roles or DEFAULT_COMPANY_ROLES)
        for config in GlobalConfig.objects.exclude(company_profile_id=None).only(
            "company_profile_id", "company_roles"
        )
    }

    configs_to_update = []
    queryset = CompanyConfig.objects.filter(company_roles=[]).only(
        "id", "user_id", "company_profile_id", "company_roles"
    )
    for config in queryset:
        if config.user_id:
            config.company_roles = global_config_by_user_id.get(
                config.user_id, DEFAULT_COMPANY_ROLES
            )
        elif config.company_profile_id:
            config.company_roles = global_config_by_company_id.get(
                config.company_profile_id, DEFAULT_COMPANY_ROLES
            )
        else:
            config.company_roles = DEFAULT_COMPANY_ROLES
        configs_to_update.append(config)

    if configs_to_update:
        CompanyConfig.objects.bulk_update(configs_to_update, ["company_roles"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0070_globalconfig_companyconfig_company_roles"),
    ]

    operations = [
        migrations.RunPython(seed_company_roles, migrations.RunPython.noop),
    ]
