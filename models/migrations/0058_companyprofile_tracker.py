# Generated manually to add tracker field to CompanyProfile

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0057_remove_companyconfig_calendar_event_status_options_and_more'),
    ]

    operations = [
        # No database operations needed - tracker is a Python attribute
        # This migration ensures the model changes are tracked
    ] 