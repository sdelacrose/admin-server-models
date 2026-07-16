from django.db import migrations


CREATED_PERMISSION_KEYS = {
    "time_booking.delete_created",
    "time_booking.update_created",
    "expense_booking.delete_created",
    "expense_booking.update_created",
}

BROAD_PERMISSION_KEYS = {
    "time_booking.delete",
    "time_booking.update",
    "expense_booking.delete",
    "expense_booking.update",
}


def replace_permissions(apps, remove_keys, add_keys):
    Role = apps.get_model("models", "Role")
    Permission = apps.get_model("models", "Permission")
    RolePermission = apps.get_model("models", "RolePermission")

    roles = Role.objects.filter(
        name="HR Manager",
        type="solution",
        scope="company",
        is_default=True,
    )
    RolePermission.objects.filter(
        role__in=roles,
        permission__key__in=remove_keys,
    ).delete()

    permissions = list(Permission.objects.filter(key__in=add_keys))
    RolePermission.objects.bulk_create(
        [
            RolePermission(role_id=role_id, permission_id=permission.id)
            for role_id in roles.values_list("id", flat=True)
            for permission in permissions
        ],
        ignore_conflicts=True,
    )


def use_created_permissions(apps, schema_editor):
    replace_permissions(apps, BROAD_PERMISSION_KEYS, CREATED_PERMISSION_KEYS)


def use_broad_permissions(apps, schema_editor):
    replace_permissions(apps, CREATED_PERMISSION_KEYS, BROAD_PERMISSION_KEYS)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0078_supplierpaymentmethod_card_details"),
    ]

    operations = [
        migrations.RunPython(use_created_permissions, use_broad_permissions),
    ]
