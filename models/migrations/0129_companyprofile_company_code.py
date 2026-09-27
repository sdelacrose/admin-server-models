# LOT 2D-12: Company Code (COMPANY_CODE-DISCIPLINE_CODE-DOCUMENT_TYPE_CODE-SEQUENCE).
#
# Written by hand rather than via `makemigrations`: this app already has unrelated,
# pre-existing model/migration drift on other fields (company_iban / iban `default`), which
# `makemigrations` would otherwise fold into this migration. Per LOT 2D-12 instructions, that
# drift is left untouched and reported separately -- this migration adds only the one field.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0128_document_control_configuration'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyprofile',
            name='company_code',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]
