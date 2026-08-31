from django.db import migrations


CUSTOMER_DEMAND_DOCUMENT_TYPE = "Customer Demand:CDE"
CUSTOMER_DEMAND_LABEL = "Customer Demand"
OTHER_LABEL = "Other"


def _label(document_type):
    return str(document_type or "").split(":", 1)[0].strip()


def ensure_customer_demand_document_type(document_types):
    values = list(document_types or [])
    if any(_label(item) == CUSTOMER_DEMAND_LABEL for item in values):
        return values

    other_index = next(
        (
            index
            for index, item in enumerate(values)
            if _label(item) == OTHER_LABEL
        ),
        len(values),
    )
    values.insert(other_index, CUSTOMER_DEMAND_DOCUMENT_TYPE)
    return values


def add_customer_demand_company_document_type(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        configs_to_update = []

        for config in model.objects.all().only("id", "document_types").iterator():
            current = list(config.document_types or [])
            updated = ensure_customer_demand_document_type(current)
            if updated == current:
                continue

            config.document_types = updated
            configs_to_update.append(config)

        if configs_to_update:
            model.objects.bulk_update(configs_to_update, ["document_types"])


def remove_customer_demand_company_document_type(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        configs_to_update = []

        for config in model.objects.all().only("id", "document_types").iterator():
            current = list(config.document_types or [])
            updated = [
                item
                for item in current
                if item != CUSTOMER_DEMAND_DOCUMENT_TYPE
            ]
            if updated == current:
                continue

            config.document_types = updated
            configs_to_update.append(config)

        if configs_to_update:
            model.objects.bulk_update(configs_to_update, ["document_types"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0120_merge_project_content_and_project_config"),
    ]

    operations = [
        migrations.RunPython(
            add_customer_demand_company_document_type,
            reverse_code=remove_customer_demand_company_document_type,
        ),
    ]
