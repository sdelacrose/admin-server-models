from django.db import migrations


RENAMES = (
    ("company_solution_space", "company_assembly_catalog"),
    ("project_solution_space", "project_assembly_catalog"),
)
ACTIONS = ("create", "update", "view", "delete", "full_access")

PERMISSION_META = {
    "company_assembly_catalog.create": (
        "Create Company Assembly Catalogs",
        "Can create company Assembly Catalogs items",
    ),
    "company_assembly_catalog.update": (
        "Update Company Assembly Catalogs",
        "Can update company Assembly Catalogs items",
    ),
    "company_assembly_catalog.view": (
        "View Company Assembly Catalogs",
        "Can view company Assembly Catalogs items",
    ),
    "company_assembly_catalog.delete": (
        "Delete Company Assembly Catalogs",
        "Can delete company Assembly Catalogs items",
    ),
    "company_assembly_catalog.full_access": (
        "Company Assembly Catalogs Full Access",
        "Full access to company Assembly Catalogs",
    ),
    "project_assembly_catalog.create": (
        "Create Project Assembly Catalogs",
        "Can create project Assembly Catalogs items",
    ),
    "project_assembly_catalog.update": (
        "Update Project Assembly Catalogs",
        "Can update project Assembly Catalogs items",
    ),
    "project_assembly_catalog.view": (
        "View Project Assembly Catalogs",
        "Can view project Assembly Catalogs items",
    ),
    "project_assembly_catalog.delete": (
        "Delete Project Assembly Catalogs",
        "Can delete project Assembly Catalogs items",
    ),
    "project_assembly_catalog.full_access": (
        "Project Assembly Catalogs Full Access",
        "Full access to project Assembly Catalogs",
    ),
}


def rename_permission_modules(apps, schema_editor):
    """
    In-place rename of Permission.key/module.

    RolePermission rows keep the same permission_id, so existing roles and users
    retain create/update/view/delete/full_access access automatically.
    """
    Permission = apps.get_model("models", "Permission")
    RolePermission = apps.get_model("models", "RolePermission")

    for old_module, new_module in RENAMES:
        for action in ACTIONS:
            old_key = f"{old_module}.{action}"
            new_key = f"{new_module}.{action}"
            permission = Permission.objects.filter(key=old_key).first()
            if not permission:
                continue

            name, description = PERMISSION_META[new_key]
            existing_new = (
                Permission.objects.filter(key=new_key).exclude(pk=permission.pk).first()
            )
            if existing_new:
                for link in RolePermission.objects.filter(permission_id=permission.id):
                    RolePermission.objects.get_or_create(
                        role_id=link.role_id,
                        permission_id=existing_new.id,
                    )
                RolePermission.objects.filter(permission_id=permission.id).delete()
                permission.delete()
                existing_new.module = new_module
                existing_new.name = name
                existing_new.description = description
                existing_new.save(update_fields=["module", "name", "description"])
                continue

            permission.key = new_key
            permission.module = new_module
            permission.name = name
            permission.description = description
            permission.save(update_fields=["key", "module", "name", "description"])



def restore_permission_modules(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    reverse_meta = {
        "company_solution_space.create": (
            "Create Company Solution Space",
            "Can create company Solution Space items",
        ),
        "company_solution_space.update": (
            "Update Company Solution Space",
            "Can update company Solution Space items",
        ),
        "company_solution_space.view": (
            "View Company Solution Space",
            "Can view company Solution Space items",
        ),
        "company_solution_space.delete": (
            "Delete Company Solution Space",
            "Can delete company Solution Space items",
        ),
        "company_solution_space.full_access": (
            "Company Solution Space Full Access",
            "Full access to company Solution Space",
        ),
        "project_solution_space.create": (
            "Create Project Solution Space",
            "Can create project Solution Space items",
        ),
        "project_solution_space.update": (
            "Update Project Solution Space",
            "Can update project Solution Space items",
        ),
        "project_solution_space.view": (
            "View Project Solution Space",
            "Can view project Solution Space items",
        ),
        "project_solution_space.delete": (
            "Delete Project Solution Space",
            "Can delete project Solution Space items",
        ),
        "project_solution_space.full_access": (
            "Project Solution Space Full Access",
            "Full access to project Solution Space",
        ),
    }

    for old_module, new_module in RENAMES:
        for action in ACTIONS:
            old_key = f"{old_module}.{action}"
            new_key = f"{new_module}.{action}"
            permission = Permission.objects.filter(key=new_key).first()
            if not permission:
                continue
            name, description = reverse_meta[old_key]
            permission.key = old_key
            permission.module = old_module
            permission.name = name
            permission.description = description
            permission.save(update_fields=["key", "module", "name", "description"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0091_rename_solution_space_to_assembly_catalog"),
    ]

    operations = [
        migrations.RunPython(
            rename_permission_modules,
            reverse_code=restore_permission_modules,
        ),
    ]
