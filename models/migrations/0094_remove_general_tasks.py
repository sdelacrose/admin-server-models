from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0093_replace_industrial_project_types"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="globalconfig",
                    name="general_tasks",
                ),
                migrations.RemoveField(
                    model_name="companyconfig",
                    name="general_tasks",
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE models_globalconfig DROP COLUMN IF EXISTS general_tasks;
                        ALTER TABLE models_companyconfig DROP COLUMN IF EXISTS general_tasks;
                    """,
                    reverse_sql="""
                        ALTER TABLE models_globalconfig
                        ADD COLUMN IF NOT EXISTS general_tasks varchar(255)[]
                        DEFAULT ARRAY[]::varchar(255)[];
                        ALTER TABLE models_companyconfig
                        ADD COLUMN IF NOT EXISTS general_tasks varchar(255)[]
                        DEFAULT ARRAY[]::varchar(255)[];
                    """,
                ),
            ],
        ),
    ]
