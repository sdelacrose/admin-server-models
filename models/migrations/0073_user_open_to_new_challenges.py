from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0072_user_spoken_languages"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="open_to_new_challenges",
            field=models.BooleanField(default=False),
        ),
    ]
