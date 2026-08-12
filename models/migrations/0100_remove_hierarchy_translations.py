from django.db import migrations


def remove_node_translations(configuration):
    if not isinstance(configuration, dict):
        return configuration, False

    changed = False
    cleaned = dict(configuration)
    for config_key, hierarchy in cleaned.items():
        if not isinstance(hierarchy, dict):
            continue
        raw_groups = hierarchy.get("groups")
        if not isinstance(raw_groups, list):
            continue

        groups = []
        for raw_group in raw_groups:
            if not isinstance(raw_group, dict):
                groups.append(raw_group)
                continue

            group = dict(raw_group)
            changed = group.pop("translations", None) is not None or changed
            children = []
            for raw_child in group.get("children", []):
                if not isinstance(raw_child, dict):
                    children.append(raw_child)
                    continue
                child = dict(raw_child)
                changed = child.pop("translations", None) is not None or changed
                children.append(child)
            group["children"] = children
            groups.append(group)

        cleaned[config_key] = {**hierarchy, "groups": groups}

    return cleaned, changed


def remove_stored_translations(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        for instance in model.objects.only("id", "nested_configurations").iterator():
            cleaned, changed = remove_node_translations(
                instance.nested_configurations
            )
            if changed:
                model.objects.filter(pk=instance.pk).update(
                    nested_configurations=cleaned
                )


class Migration(migrations.Migration):
    dependencies = [("models", "0099_globalconfig_companyconfig_nested_configurations")]

    operations = [
        migrations.RunPython(
            remove_stored_translations,
            migrations.RunPython.noop,
        )
    ]
