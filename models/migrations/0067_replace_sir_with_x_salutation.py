from django.db import migrations


def replace_sir_with_x(apps, schema_editor):
    replacement_map = {"Sir": "X"}
    model_names = ["CompanyConfig", "GlobalConfig"]

    for model_name in model_names:
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        if "salutation" not in field_names:
            continue
        to_update = []
        for obj in model.objects.all().only("id", "salutation"):
            salutations = list(getattr(obj, "salutation", []) or [])
            if not salutations:
                continue

            updated_salutations = []
            changed = False
            for item in salutations:
                new_item = replacement_map.get(item, item)
                if new_item != item:
                    changed = True
                if new_item not in updated_salutations:
                    updated_salutations.append(new_item)

            if changed:
                obj.salutation = updated_salutations
                to_update.append(obj)

        if to_update:
            model.objects.bulk_update(to_update, ["salutation"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0066_companyconfig_salutation"),
    ]

    operations = [
        migrations.RunPython(replace_sir_with_x, migrations.RunPython.noop),
    ]
