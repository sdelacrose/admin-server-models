from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0073_user_open_to_new_challenges"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE models_user "
                        "ALTER COLUMN availability_from TYPE date USING NULL, "
                        "ALTER COLUMN availability_until TYPE date USING NULL"
                    ),
                    reverse_sql=(
                        "ALTER TABLE models_user "
                        "ALTER COLUMN availability_from TYPE time USING NULL, "
                        "ALTER COLUMN availability_until TYPE time USING NULL"
                    ),
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="user",
                    name="availability_from",
                    field=models.DateField(blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name="user",
                    name="availability_until",
                    field=models.DateField(blank=True, null=True),
                ),
            ],
        ),
    ]
