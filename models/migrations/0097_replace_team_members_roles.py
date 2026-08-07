from django.db import migrations

NEW_TEAM_MEMBERS_ROLES = [
    "consultant",
    "project manager",
    "customer",
    "supplier",
    "notified body",
]

LEGACY_DEFAULT_TEAM_MEMBERS_ROLES = {
    "architect",
    "structural engineer",
    "contractor",
    "project manager",
}

RENAME_TEAM_MEMBERS_ROLES = {
    "contractor": "consultant",
}


def _normalize_team_members_roles(current):
    values = [str(item).strip() for item in (current or []) if str(item).strip()]
    renamed = [RENAME_TEAM_MEMBERS_ROLES.get(item, item) for item in values]

    customs = []
    for item in renamed:
        if item in LEGACY_DEFAULT_TEAM_MEMBERS_ROLES:
            continue
        if item not in NEW_TEAM_MEMBERS_ROLES:
            customs.append(item)

    ordered = list(NEW_TEAM_MEMBERS_ROLES)
    seen = set(ordered)
    for custom in customs:
        if custom not in seen:
            ordered.append(custom)
            seen.add(custom)
    return ordered


def replace_team_members_roles(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        if "team_members_roles" not in field_names:
            continue

        to_update = []
        for obj in model.objects.all().only("id", "team_members_roles"):
            current = list(getattr(obj, "team_members_roles", []) or [])
            updated = _normalize_team_members_roles(current)
            if updated != current:
                obj.team_members_roles = updated
                to_update.append(obj)

        if to_update:
            model.objects.bulk_update(to_update, ["team_members_roles"])

    feedback_model = apps.get_model("models", "Feedback")
    field_names = {field.name for field in feedback_model._meta.get_fields()}
    if "project_team_role" in field_names:
        feedback_model.objects.filter(project_team_role="contractor").update(
            project_team_role="consultant"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0096_replace_expense_types"),
    ]

    operations = [
        migrations.RunPython(
            replace_team_members_roles,
            migrations.RunPython.noop,
        ),
    ]
