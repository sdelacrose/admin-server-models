# LOT 3B stabilization: Correspondence Type reference data on CompanyConfig.
#
# Written by hand rather than via `makemigrations`: this app already has unrelated,
# pre-existing migration drift (company_iban / iban field defaults) that `makemigrations`
# would otherwise fold into this migration. That drift is left untouched and reported
# separately -- this migration only adds the one field.

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0129_companyprofile_company_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyconfig',
            name='correspondence_types',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255), blank=True, default=list, size=None,
            ),
        ),
    ]
