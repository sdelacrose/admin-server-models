from django.db import migrations


REMOVED_PROJECT_FIELDS = (
    "commercial_model",
    "configuration_visibility",
    "contract_type",
    "expense_types",
    "international_standard",
    "invoice_status",
    "major_project_model",
    "opportunity_sales_phase",
    "project_types",
    "supporting_agreement",
)


def remove_project_area_of_expertise(apps, schema_editor):
    ProjectConfigTemplate = apps.get_model("models", "ProjectConfigTemplate")
    for template in ProjectConfigTemplate.objects.iterator():
        nested = dict(template.nested_configurations or {})
        if nested.pop("area_of_expertise", None) is not None:
            template.nested_configurations = nested
            template.save(update_fields=["nested_configurations"])


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0118_remove_flat_area_of_expertise"),
    ]

    operations = [
        migrations.RunPython(
            remove_project_area_of_expertise,
            migrations.RunPython.noop,
        ),
        *[
            migrations.RemoveField(
                model_name="projectconfigtemplate",
                name=field_name,
            )
            for field_name in REMOVED_PROJECT_FIELDS
        ],
    ]
