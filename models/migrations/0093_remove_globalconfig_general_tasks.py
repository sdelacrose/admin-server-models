from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0092_rename_solution_space_permission_modules"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="globalconfig",
                    name="general_tasks",
                ),
            ],
            database_operations=[
                # Safe for DBs that already lack the column
                migrations.RunSQL(
                    sql="ALTER TABLE models_globalconfig DROP COLUMN IF EXISTS general_tasks;",
                    reverse_sql="""
                        ALTER TABLE models_globalconfig
                        ADD COLUMN IF NOT EXISTS general_tasks varchar(255)[]
                        DEFAULT ARRAY[]::varchar(255)[];
                    """,
                ),
            ],
        ),
    ]
