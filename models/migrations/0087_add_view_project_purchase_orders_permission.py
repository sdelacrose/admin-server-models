from django.db import migrations


PERMISSION_KEY = "purchase_order.view_project"


def add_permission_to_default_roles(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    Role = apps.get_model("models", "Role")
    RolePermission = apps.get_model("models", "RolePermission")

    permission, _ = Permission.objects.update_or_create(
        key=PERMISSION_KEY,
        defaults={
            "name": "View Project Purchase Orders",
            "description": (
                "Can view purchase orders linked to projects where the user "
                "is a team member"
            ),
            "module": "purchase_order",
        },
    )
    default_role_ids = Role.objects.filter(
        type="solution",
        scope="company",
        is_default=True,
    ).values_list("id", flat=True)
    RolePermission.objects.bulk_create(
        [
            RolePermission(role_id=role_id, permission_id=permission.id)
            for role_id in default_role_ids
        ],
        ignore_conflicts=True,
    )


def remove_permission(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    Permission.objects.filter(key=PERMISSION_KEY).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0086_merge_0085_display_configuration_and_invoice_status"),
    ]

    operations = [
        migrations.RunPython(add_permission_to_default_roles, remove_permission),
    ]
