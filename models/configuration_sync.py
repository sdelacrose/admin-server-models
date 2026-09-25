from copy import deepcopy

from .configuration_templates import (
    CODED_FIELD_KIND,
    NESTED_DERIVED_FIELDS,
    PROJECT_CONFIGURATION_FIELDS,
    STATUS_FIELD_KIND,
    configuration_field_kind,
)
from .configuration_visibility import (
    FLAT_VISIBILITY_KEYS,
    NESTED_VISIBILITY_KEYS,
    clean_configuration_visibility,
)
from .hierarchical_configurations import (
    NESTED_CONFIGURATION_DEFINITIONS,
    flatten_nested_configurations,
    normalize_nested_configuration,
    resolve_nested_configurations,
)


PRESERVE_LOCAL = "preserve_local"
REPLACE = "replace"
SYNC_STRATEGIES = (PRESERVE_LOCAL, REPLACE)


class ConfigurationSyncError(ValueError):
    pass


def validate_sync_strategy(strategy):
    if strategy not in SYNC_STRATEGIES:
        raise ConfigurationSyncError(
            f"Unsupported configuration sync strategy: {strategy}."
        )
    return strategy


def _text(value):
    return str(value or "").strip()


def _split_suffix(value):
    text = _text(value)
    if ":" not in text:
        return text, ""
    return tuple(part.strip() for part in text.rsplit(":", 1))


def configuration_value_identity(value, field_kind):
    label, suffix = _split_suffix(value)
    if field_kind == CODED_FIELD_KIND and suffix:
        return suffix.casefold()
    if field_kind == STATUS_FIELD_KIND:
        return label.casefold()
    return _text(value).casefold()


def _configuration_values(values, field_name):
    if values is None:
        return []
    if not isinstance(values, (list, tuple)):
        raise ConfigurationSyncError(f"{field_name} must be a list.")
    return values


def merge_list_values(local_values, template_values, *, field_kind):
    merged = []
    seen = set()
    local = _configuration_values(local_values, "Local configuration values")
    template = _configuration_values(
        template_values,
        "Template configuration values",
    )
    for value in [*local, *template]:
        normalized = _text(value)
        if not normalized:
            continue
        identity = configuration_value_identity(normalized, field_kind)
        if identity in seen:
            continue
        seen.add(identity)
        merged.append(normalized)
    return merged


def merge_nested_configuration(config_key, local_value, template_value):
    local = normalize_nested_configuration(config_key, local_value)
    template = normalize_nested_configuration(config_key, template_value)
    merged = deepcopy(local)
    groups_by_id = {group["id"]: group for group in merged["groups"]}
    existing_child_ids = {
        child["id"]
        for group in merged["groups"]
        for child in group["children"]
    }

    for template_group in template["groups"]:
        local_group = groups_by_id.get(template_group["id"])
        if local_group is None:
            appended_group = deepcopy(template_group)
            appended_group["children"] = [
                child
                for child in appended_group["children"]
                if child["id"] not in existing_child_ids
            ]
            merged["groups"].append(appended_group)
            groups_by_id[appended_group["id"]] = appended_group
            existing_child_ids.update(
                child["id"] for child in appended_group["children"]
            )
            continue

        for child in template_group["children"]:
            if child["id"] in existing_child_ids:
                continue
            local_group["children"].append(deepcopy(child))
            existing_child_ids.add(child["id"])

    return normalize_nested_configuration(
        config_key,
        merged,
        existing_configuration=local,
    )


def merge_nested_configurations_preserving_local(local_values, template_values):
    local = resolve_nested_configurations(local_values)
    template = resolve_nested_configurations(template_values)
    merged = deepcopy(local)
    for config_key, template_value in template.items():
        if config_key in NESTED_CONFIGURATION_DEFINITIONS:
            merged[config_key] = merge_nested_configuration(
                config_key,
                local[config_key],
                template_value,
            )
        elif config_key not in merged:
            merged[config_key] = deepcopy(template_value)
    return merged


def _disabled_flat_values(visibility, field_name):
    entry = visibility.get(field_name, {}) if isinstance(visibility, dict) else {}
    if not isinstance(entry, dict):
        return []
    values = entry.get("disabled_values", [])
    return values if isinstance(values, list) else []


def _merge_flat_visibility(
    field_name,
    merged_values,
    local_values,
    local_visibility,
    template_visibility,
):
    field_kind = configuration_field_kind(field_name)
    local_by_identity = {
        configuration_value_identity(value, field_kind): value
        for value in local_values or []
    }
    local_disabled = {
        configuration_value_identity(value, field_kind)
        for value in _disabled_flat_values(local_visibility, field_name)
    }
    template_disabled = {
        configuration_value_identity(value, field_kind)
        for value in _disabled_flat_values(template_visibility, field_name)
    }
    disabled = []
    for value in merged_values:
        identity = configuration_value_identity(value, field_kind)
        is_disabled = (
            identity in local_disabled
            if identity in local_by_identity
            else identity in template_disabled
        )
        if is_disabled:
            disabled.append(value)
    return {"disabled_values": disabled} if disabled else {}


def _nested_ids(configuration):
    group_ids = []
    child_ids = []
    if not isinstance(configuration, dict):
        return group_ids, child_ids

    for group in configuration.get("groups", []):
        group_ids.append(group["id"])
        child_ids.extend(child["id"] for child in group.get("children", []))
    return group_ids, child_ids


def _disabled_nested_ids(visibility, config_key, key):
    entry = visibility.get(config_key, {}) if isinstance(visibility, dict) else {}
    if not isinstance(entry, dict):
        return set()
    values = entry.get(key, [])
    return set(values) if isinstance(values, list) else set()


def merge_configuration_visibility(
    *,
    local_visibility,
    template_visibility,
    local_values,
    merged_values,
    local_nested,
    merged_nested,
):
    visibility = {}
    for field_name in FLAT_VISIBILITY_KEYS:
        values = merged_values.get(field_name, [])
        entry = _merge_flat_visibility(
            field_name,
            values,
            local_values.get(field_name, []),
            local_visibility,
            template_visibility,
        )
        if entry:
            visibility[field_name] = entry

    for config_key in NESTED_VISIBILITY_KEYS:
        local_group_ids, local_child_ids = _nested_ids(
            local_nested.get(config_key, {})
        )
        merged_group_ids, merged_child_ids = _nested_ids(
            merged_nested.get(config_key, {})
        )
        local_group_ids = set(local_group_ids)
        local_child_ids = set(local_child_ids)
        local_disabled_groups = _disabled_nested_ids(
            local_visibility, config_key, "disabled_group_ids"
        )
        template_disabled_groups = _disabled_nested_ids(
            template_visibility, config_key, "disabled_group_ids"
        )
        local_disabled_children = _disabled_nested_ids(
            local_visibility, config_key, "disabled_child_ids"
        )
        template_disabled_children = _disabled_nested_ids(
            template_visibility, config_key, "disabled_child_ids"
        )
        disabled_groups = [
            group_id
            for group_id in merged_group_ids
            if (
                group_id in local_disabled_groups
                if group_id in local_group_ids
                else group_id in template_disabled_groups
            )
        ]
        disabled_children = [
            child_id
            for child_id in merged_child_ids
            if (
                child_id in local_disabled_children
                if child_id in local_child_ids
                else child_id in template_disabled_children
            )
        ]
        entry = {}
        if disabled_groups:
            entry["disabled_group_ids"] = disabled_groups
        if disabled_children:
            entry["disabled_child_ids"] = disabled_children
        if entry:
            visibility[config_key] = entry

    return clean_configuration_visibility(
        visibility,
        configured_values=merged_values,
        nested_configurations=merged_nested,
    )


def preserve_local_configuration(
    local_configuration,
    template_configuration,
    *,
    field_names=PROJECT_CONFIGURATION_FIELDS,
):
    local = local_configuration or {}
    template = template_configuration or {}
    result = {}
    local_list_values = {}
    merged_list_values = {}

    for field_name in field_names:
        if field_name == "document_control_configuration":
            # Structured object (not a list): the local setting wins when present.
            result[field_name] = deepcopy(
                local.get(field_name) or template.get(field_name) or {}
            )
            continue
        if field_name in {
            "nested_configurations",
            "configuration_visibility",
            *NESTED_DERIVED_FIELDS.values(),
        }:
            continue
        field_kind = configuration_field_kind(field_name)
        local_values = local.get(field_name, [])
        merged_values = merge_list_values(
            local_values,
            template.get(field_name, []),
            field_kind=field_kind,
        )
        local_list_values[field_name] = local_values
        merged_list_values[field_name] = merged_values
        result[field_name] = merged_values

    local_nested = resolve_nested_configurations(
        local.get("nested_configurations", {})
    )
    merged_nested = merge_nested_configurations_preserving_local(
        local_nested,
        template.get("nested_configurations", {}),
    )
    flattened = flatten_nested_configurations(merged_nested)
    result["nested_configurations"] = merged_nested
    for config_key, field_name in NESTED_DERIVED_FIELDS.items():
        result[field_name] = flattened[config_key]

    if "configuration_visibility" in field_names:
        result["configuration_visibility"] = merge_configuration_visibility(
            local_visibility=local.get("configuration_visibility", {}),
            template_visibility=template.get("configuration_visibility", {}),
            local_values=local_list_values,
            merged_values=merged_list_values,
            local_nested=local_nested,
            merged_nested=merged_nested,
        )
    return result


def replace_configuration(
    template_configuration,
    *,
    field_names=PROJECT_CONFIGURATION_FIELDS,
):
    return {
        field_name: deepcopy(template_configuration.get(field_name))
        for field_name in field_names
        if field_name in template_configuration
    }


def configuration_values_from_instance(instance, field_names):
    return {
        field_name: deepcopy(getattr(instance, field_name))
        for field_name in field_names
        if hasattr(instance, field_name)
    }
