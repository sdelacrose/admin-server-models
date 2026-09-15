from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models
from django.db.migrations.exceptions import IrreversibleError


PROFILE_MODELS = ("User", "CompanyProfile")


def copy_single_values_to_arrays(apps, schema_editor):
    for model_name in PROFILE_MODELS:
        model = apps.get_model("models", model_name)
        for profile in model.objects.exclude(
            sub_area_of_expertise__isnull=True,
        ).exclude(sub_area_of_expertise="").iterator():
            profile.sub_area_of_expertise_values = [
                profile.sub_area_of_expertise,
            ]
            profile.save(update_fields=["sub_area_of_expertise_values"])


def copy_arrays_to_single_values(apps, schema_editor):
    models_to_restore = [
        apps.get_model("models", model_name)
        for model_name in PROFILE_MODELS
    ]
    if any(
        model.objects.filter(
            sub_area_of_expertise_values__len__gt=1,
        ).exists()
        for model in models_to_restore
    ):
        raise IrreversibleError(
            "Cannot reverse models.0126 while user or company profiles have "
            "multiple sub-areas of expertise. Remove the additional "
            "selections explicitly before retrying the rollback."
        )

    for model in models_to_restore:
        for profile in model.objects.exclude(
            sub_area_of_expertise_values=[],
        ).iterator():
            profile.sub_area_of_expertise = (
                profile.sub_area_of_expertise_values[0]
            )
            profile.save(update_fields=["sub_area_of_expertise"])


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0125_area_of_expertise_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="sub_area_of_expertise_values",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="sub_area_of_expertise_values",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.RunPython(
            copy_single_values_to_arrays,
            reverse_code=copy_arrays_to_single_values,
        ),
        migrations.RemoveField(
            model_name="user",
            name="sub_area_of_expertise",
        ),
        migrations.RemoveField(
            model_name="companyprofile",
            name="sub_area_of_expertise",
        ),
        migrations.RenameField(
            model_name="user",
            old_name="sub_area_of_expertise_values",
            new_name="sub_area_of_expertise",
        ),
        migrations.RenameField(
            model_name="companyprofile",
            old_name="sub_area_of_expertise_values",
            new_name="sub_area_of_expertise",
        ),
    ]
