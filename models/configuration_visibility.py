from copy import deepcopy

from models.hierarchical_configurations import AREA_OF_EXPERTISE_KEY


FLAT_VISIBILITY_KEYS = (
    "contract_type",
    "international_standard",
    "major_project_model",
    "commercial_model",
    "supporting_agreement",
)
NESTED_VISIBILITY_KEYS = (AREA_OF_EXPERTISE_KEY,)
SUPPORTED_VISIBILITY_KEYS = (*FLAT_VISIBILITY_KEYS, *NESTED_VISIBILITY_KEYS)


class ConfigurationVisibilityError(ValueError):
    pass


def _unique_strings(values, field_name):
    if not isinstance(values, list):
        raise ConfigurationVisibilityError(f"{field_name} must be a list.")

    normalized = []
    seen = set()
    for value in values:
        item = str(value or "").strip()
        if not item:
            raise ConfigurationVisibilityError(
                f"{field_name} cannot contain empty values."
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _nested_ids(configuration):
    group_ids = set()
    child_ids = set()
    if not isinstance(configuration, dict):
        return group_ids, child_ids

    for group in configuration.get("groups", []):
        if not isinstance(group, dict):
            continue
        group_id = str(group.get("id") or "").strip()
        if group_id:
            group_ids.add(group_id)
        for child in group.get("children", []):
            if not isinstance(child, dict):
                continue
            child_id = str(child.get("id") or "").strip()
            if child_id:
                child_ids.add(child_id)
    return group_ids, child_ids


def _normalize_flat_entry(config_key, entry, configured_values):
    if not isinstance(entry, dict):
        raise ConfigurationVisibilityError(
            f"Visibility for {config_key} must be an object."
        )
    unknown_fields = set(entry) - {"disabled_values"}
    if unknown_fields:
        raise ConfigurationVisibilityError(
            f"Unsupported visibility fields for {config_key}: "
            f"{', '.join(sorted(unknown_fields))}."
        )

    disabled_values = _unique_strings(
        entry.get("disabled_values", []),
        f"{config_key}.disabled_values",
    )
    available_values = set(configured_values or [])
    unknown_values = [value for value in disabled_values if value not in available_values]
    if unknown_values:
        raise ConfigurationVisibilityError(
            f"Unknown disabled values for {config_key}: {', '.join(unknown_values)}."
        )
    return {"disabled_values": disabled_values} if disabled_values else {}


def _normalize_nested_entry(config_key, entry, nested_configuration):
    if not isinstance(entry, dict):
        raise ConfigurationVisibilityError(
            f"Visibility for {config_key} must be an object."
        )
    allowed_fields = {"disabled_group_ids", "disabled_child_ids"}
    unknown_fields = set(entry) - allowed_fields
    if unknown_fields:
        raise ConfigurationVisibilityError(
            f"Unsupported visibility fields for {config_key}: "
            f"{', '.join(sorted(unknown_fields))}."
        )

    disabled_group_ids = _unique_strings(
        entry.get("disabled_group_ids", []),
        f"{config_key}.disabled_group_ids",
    )
    disabled_child_ids = _unique_strings(
        entry.get("disabled_child_ids", []),
        f"{config_key}.disabled_child_ids",
    )
    group_ids, child_ids = _nested_ids(nested_configuration)
    unknown_group_ids = [item for item in disabled_group_ids if item not in group_ids]
    unknown_child_ids = [item for item in disabled_child_ids if item not in child_ids]
    if unknown_group_ids:
        raise ConfigurationVisibilityError(
            f"Unknown disabled groups for {config_key}: "
            f"{', '.join(unknown_group_ids)}."
        )
    if unknown_child_ids:
        raise ConfigurationVisibilityError(
            f"Unknown disabled options for {config_key}: "
            f"{', '.join(unknown_child_ids)}."
        )

    normalized = {}
    if disabled_group_ids:
        normalized["disabled_group_ids"] = disabled_group_ids
    if disabled_child_ids:
        normalized["disabled_child_ids"] = disabled_child_ids
    return normalized


def prepare_configuration_visibility_update(
    current,
    updates,
    *,
    configured_values,
    nested_configurations,
):
    if not isinstance(updates, dict):
        raise ConfigurationVisibilityError(
            "Configuration visibility updates must be an object."
        )

    merged = deepcopy(current) if isinstance(current, dict) else {}
    for config_key, entry in updates.items():
        if config_key not in SUPPORTED_VISIBILITY_KEYS:
            raise ConfigurationVisibilityError(
                f"Unsupported visibility configuration: {config_key}."
            )
        if config_key in FLAT_VISIBILITY_KEYS:
            normalized = _normalize_flat_entry(
                config_key,
                entry,
                configured_values.get(config_key, []),
            )
        else:
            normalized = _normalize_nested_entry(
                config_key,
                entry,
                nested_configurations.get(config_key, {}),
            )

        if normalized:
            merged[config_key] = normalized
        else:
            merged.pop(config_key, None)
    return merged


def clean_configuration_visibility(
    visibility,
    *,
    configured_values,
    nested_configurations,
):
    cleaned = {}
    source = visibility if isinstance(visibility, dict) else {}
    for config_key in SUPPORTED_VISIBILITY_KEYS:
        if config_key not in source:
            continue
        try:
            cleaned = prepare_configuration_visibility_update(
                cleaned,
                {config_key: source[config_key]},
                configured_values=configured_values,
                nested_configurations=nested_configurations,
            )
        except ConfigurationVisibilityError:
            if config_key in FLAT_VISIBILITY_KEYS:
                entry = source[config_key] if isinstance(source[config_key], dict) else {}
                disabled_values = entry.get("disabled_values", [])
                if not isinstance(disabled_values, list):
                    disabled_values = []
                available_values = set(configured_values.get(config_key, []))
                valid_values = [
                    value for value in disabled_values if value in available_values
                ]
                if valid_values:
                    cleaned[config_key] = {"disabled_values": valid_values}
            else:
                group_ids, child_ids = _nested_ids(
                    nested_configurations.get(config_key, {})
                )
                entry = source[config_key] if isinstance(source[config_key], dict) else {}
                valid_groups = [
                    item
                    for item in entry.get("disabled_group_ids", [])
                    if item in group_ids
                ]
                valid_children = [
                    item
                    for item in entry.get("disabled_child_ids", [])
                    if item in child_ids
                ]
                normalized = {}
                if valid_groups:
                    normalized["disabled_group_ids"] = valid_groups
                if valid_children:
                    normalized["disabled_child_ids"] = valid_children
                if normalized:
                    cleaned[config_key] = normalized
    return cleaned


def disabled_flat_values(visibility, config_key):
    source = visibility if isinstance(visibility, dict) else {}
    entry = source.get(config_key, {})
    if not isinstance(entry, dict):
        return set()
    return set(entry.get("disabled_values", []))


def filter_enabled_flat_values(values, visibility, config_key):
    disabled = disabled_flat_values(visibility, config_key)
    return [value for value in values or [] if value not in disabled]


def annotate_flat_values(values, default_values, visibility, config_key):
    disabled = disabled_flat_values(visibility, config_key)
    defaults = set(default_values or [])
    return [
        {
            "value": value,
            "is_default": value in defaults,
            "is_enabled": value not in disabled,
        }
        for value in values or []
    ]


def annotate_nested_visibility(configurations, visibility):
    annotated = deepcopy(configurations) if isinstance(configurations, dict) else {}
    source = visibility if isinstance(visibility, dict) else {}
    for config_key in NESTED_VISIBILITY_KEYS:
        configuration = annotated.get(config_key)
        if not isinstance(configuration, dict):
            continue

        entry = source.get(config_key, {})
        disabled_groups = (
            set(entry.get("disabled_group_ids", []))
            if isinstance(entry, dict)
            else set()
        )
        disabled_children = (
            set(entry.get("disabled_child_ids", []))
            if isinstance(entry, dict)
            else set()
        )
        for group in configuration.get("groups", []):
            group["is_enabled"] = group.get("id") not in disabled_groups
            for child in group.get("children", []):
                child["is_enabled"] = child.get("id") not in disabled_children
    return annotated


def filter_enabled_nested_configurations(configurations, visibility):
    filtered = deepcopy(configurations) if isinstance(configurations, dict) else {}
    source = visibility if isinstance(visibility, dict) else {}
    for config_key in NESTED_VISIBILITY_KEYS:
        configuration = filtered.get(config_key)
        if not isinstance(configuration, dict):
            continue

        entry = source.get(config_key, {})
        disabled_groups = (
            set(entry.get("disabled_group_ids", []))
            if isinstance(entry, dict)
            else set()
        )
        disabled_children = (
            set(entry.get("disabled_child_ids", []))
            if isinstance(entry, dict)
            else set()
        )
        groups = []
        for group in configuration.get("groups", []):
            if group.get("id") in disabled_groups:
                continue
            enabled_children = [
                child
                for child in group.get("children", [])
                if child.get("id") not in disabled_children
            ]
            if enabled_children:
                group["children"] = enabled_children
                groups.append(group)
        configuration["groups"] = groups
    return filtered
