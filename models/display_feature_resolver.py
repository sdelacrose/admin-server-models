"""Resolve sparse display overrides into configured and effective visibility."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .display_feature_registry import (
    DISPLAY_FEATURE_BY_KEY,
    DISPLAY_FEATURES,
    DisplayFeature,
    SolutionId,
    normalize_solution_id,
)


class VisibilityReason(str, Enum):
    SELF_HIDDEN = "self_hidden"
    PARENT_HIDDEN = "parent_hidden"
    DEPENDENCY_HIDDEN = "dependency_hidden"
    NOT_AVAILABLE_FOR_SOLUTION = "not_available_for_solution"


@dataclass(frozen=True)
class ResolvedDisplayFeature:
    feature: DisplayFeature
    configured_visible: bool
    effective_visible: bool
    reason: VisibilityReason | None = None
    blocked_by: str | None = None

    @property
    def key(self) -> str:
        return self.feature.key


class DisplayFeatureOverrideError(ValueError):
    """Raised when display overrides cannot be accepted for a solution."""


def _validate_override_mapping(overrides: Mapping[str, object] | None) -> None:
    if overrides is not None and not isinstance(overrides, Mapping):
        raise DisplayFeatureOverrideError("Display overrides must be an object.")


def validate_display_overrides(
    solution: SolutionId | str,
    overrides: Mapping[str, object] | None,
    *,
    allow_null: bool = False,
) -> None:
    solution_id = normalize_solution_id(solution)
    _validate_override_mapping(overrides)

    errors: list[str] = []
    for key, value in (overrides or {}).items():
        feature = DISPLAY_FEATURE_BY_KEY.get(key)
        if not feature:
            errors.append(f"Unknown display feature key: {key}")
            continue
        if solution_id not in feature.available_in:
            errors.append(
                f"Display feature {key} is not available for {solution_id.value}"
            )
        if not isinstance(value, bool) and not (allow_null and value is None):
            errors.append(f"Display override for {key} must be boolean")

    if errors:
        raise DisplayFeatureOverrideError("\n".join(errors))


def normalize_display_overrides(
    solution: SolutionId | str,
    overrides: Mapping[str, object] | None,
) -> dict[str, bool]:
    """Validate overrides and retain only values differing from registry defaults."""

    validate_display_overrides(solution, overrides)
    return {
        key: value
        for key, value in (overrides or {}).items()
        if value != DISPLAY_FEATURE_BY_KEY[key].default_visible
    }


def sanitize_stored_display_overrides(
    solution: SolutionId | str,
    overrides: Mapping[str, object] | None,
) -> dict[str, bool]:
    """Ignore stale or malformed stored keys while retaining valid overrides."""

    solution_id = normalize_solution_id(solution)
    if not isinstance(overrides, Mapping):
        return {}

    sanitized: dict[str, bool] = {}
    for key, value in overrides.items():
        feature = DISPLAY_FEATURE_BY_KEY.get(key)
        if (
            feature
            and solution_id in feature.available_in
            and isinstance(value, bool)
            and value != feature.default_visible
        ):
            sanitized[key] = value
    return sanitized


def merge_display_override_changes(
    solution: SolutionId | str,
    current_overrides: Mapping[str, object] | None,
    changes: Mapping[str, object] | None,
) -> dict[str, bool]:
    """Apply PATCH-like changes; null removes a key and restores its default."""

    normalized_current = sanitize_stored_display_overrides(
        solution,
        current_overrides,
    )
    validate_display_overrides(solution, changes, allow_null=True)

    merged: dict[str, object] = dict(normalized_current)
    for key, value in (changes or {}).items():
        if value is None:
            merged.pop(key, None)
        else:
            merged[key] = value
    return normalize_display_overrides(solution, merged)


def resolve_display_features(
    solution: SolutionId | str,
    overrides: Mapping[str, object] | None = None,
    *,
    include_unavailable: bool = False,
) -> tuple[ResolvedDisplayFeature, ...]:
    solution_id = normalize_solution_id(solution)
    normalized_overrides = sanitize_stored_display_overrides(
        solution_id,
        overrides,
    )
    resolved_by_key: dict[str, ResolvedDisplayFeature] = {}
    resolving: set[str] = set()

    def resolve(feature: DisplayFeature) -> ResolvedDisplayFeature:
        existing = resolved_by_key.get(feature.key)
        if existing:
            return existing
        if feature.key in resolving:
            raise RuntimeError(f"Circular display feature relationship: {feature.key}")

        resolving.add(feature.key)
        configured_visible = normalized_overrides.get(
            feature.key,
            feature.default_visible,
        )
        result: ResolvedDisplayFeature

        if solution_id not in feature.available_in:
            result = ResolvedDisplayFeature(
                feature=feature,
                configured_visible=configured_visible,
                effective_visible=False,
                reason=VisibilityReason.NOT_AVAILABLE_FOR_SOLUTION,
            )
        else:
            parent = (
                resolve(DISPLAY_FEATURE_BY_KEY[feature.parent_key])
                if feature.parent_key
                else None
            )
            hidden_dependency = next(
                (
                    dependency
                    for dependency in feature.dependencies
                    if not resolve(DISPLAY_FEATURE_BY_KEY[dependency]).effective_visible
                ),
                None,
            )

            if parent and not parent.effective_visible:
                result = ResolvedDisplayFeature(
                    feature=feature,
                    configured_visible=configured_visible,
                    effective_visible=False,
                    reason=VisibilityReason.PARENT_HIDDEN,
                    blocked_by=parent.key,
                )
            elif hidden_dependency:
                result = ResolvedDisplayFeature(
                    feature=feature,
                    configured_visible=configured_visible,
                    effective_visible=False,
                    reason=VisibilityReason.DEPENDENCY_HIDDEN,
                    blocked_by=hidden_dependency,
                )
            elif not configured_visible:
                result = ResolvedDisplayFeature(
                    feature=feature,
                    configured_visible=False,
                    effective_visible=False,
                    reason=VisibilityReason.SELF_HIDDEN,
                )
            else:
                result = ResolvedDisplayFeature(
                    feature=feature,
                    configured_visible=True,
                    effective_visible=True,
                )

        resolving.remove(feature.key)
        resolved_by_key[feature.key] = result
        return result

    resolved = tuple(resolve(feature) for feature in DISPLAY_FEATURES)
    if include_unavailable:
        return resolved
    return tuple(
        item
        for item in resolved
        if item.reason is not VisibilityReason.NOT_AVAILABLE_FOR_SOLUTION
    )


def get_effective_visibility_map(
    solution: SolutionId | str,
    overrides: Mapping[str, object] | None = None,
) -> dict[str, bool]:
    return {
        item.key: item.effective_visible
        for item in resolve_display_features(solution, overrides)
    }
