# Generated manually for data cleanup before rollback

from django.db import migrations

def cleanup_roles_with_null_company(apps, schema_editor):
    """
    Clean up roles that have NULL company values before rolling back migration 0058.
    This function handles the data cleanup to prevent NOT NULL constraint violations.
    """
    Role = apps.get_model('models', 'Role')
    UserRole = apps.get_model('models', 'UserRole')
    RolePermission = apps.get_model('models', 'RolePermission')
    
    # Find all roles with NULL company values
    roles_with_null_company = Role.objects.filter(company__isnull=True)
    
    print(f"Found {roles_with_null_company.count()} roles with NULL company values")
    
    for role in roles_with_null_company:
        print(f"Processing role: {role.name} (ID: {role.id})")
        
        # Option 1: Delete the role and all related data
        # This is the safest approach for rollback
        related_user_roles = UserRole.objects.filter(role=role)
        related_role_permissions = RolePermission.objects.filter(role=role)
        
        print(f"  - Deleting {related_user_roles.count()} user role assignments")
        print(f"  - Deleting {related_role_permissions.count()} role permissions")
        
        # Delete related records first (due to foreign key constraints)
        related_user_roles.delete()
        related_role_permissions.delete()
        
        # Delete the role itself
        role.delete()
        print(f"  - Deleted role: {role.name}")

def reverse_cleanup_roles_with_null_company(apps, schema_editor):
    """
    Reverse function - this won't be called during rollback, but Django requires it.
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('models', '0060_role_freelancer_alter_role_company'),
    ]

    operations = [
        migrations.RunPython(
            cleanup_roles_with_null_company,
            reverse_cleanup_roles_with_null_company,
        ),
    ] 