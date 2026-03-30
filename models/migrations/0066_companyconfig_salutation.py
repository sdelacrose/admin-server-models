import django.contrib.postgres.fields
from django.db import migrations, models


DEFAULT_SALUTATIONS = ["Mr", "Mrs", "Sir", "Miss"]


def seed_salutations(apps, schema_editor):
    CompanyConfig = apps.get_model('models', 'CompanyConfig')
    CompanyConfig.objects.filter(salutation=[]).update(salutation=DEFAULT_SALUTATIONS)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0065_alter_bankdetail_company_iban_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name='companyconfig',
            name='salutation',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.RunPython(seed_salutations, migrations.RunPython.noop),
    ]
