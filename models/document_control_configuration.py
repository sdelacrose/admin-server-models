"""Document Control configuration: canonical defaults, resolver and validator.

Stored as one structured JSON object (`document_control_configuration`) on the existing
configuration models (GlobalConfig, CompanyConfig, ProjectConfigTemplate, ECPMPConfig).
A missing or partial object resolves to the canonical defaults, so no data migration is
needed just to read it. Inheritance stays the existing one: template -> copy/sync -> project.
"""

import re
from copy import deepcopy

REFERENCE_SEGMENTS = (
    "PROJECT",
    "COMPANY",
    "DISCIPLINE",
    "DOCUMENT_TYPE",
    "CATEGORY",
    "SEQUENCE",
)
SEQUENCE_SCOPES = ("COMPANY", "PROJECT", "DISCIPLINE", "DOCUMENT_TYPE")
REVISION_SCHEMES = ("ALPHABETIC", "NUMERIC")
WORKFLOW_DEFAULTS = ("TWO_STEP", "THREE_STEP")
SAFE_SEPARATORS = "-_./"
MAX_SEQUENCE_WIDTH = 10

DEFAULT_DOCUMENT_CONTROL_CONFIGURATION = {
    "reference": {
        "segments": ["PROJECT", "DISCIPLINE", "DOCUMENT_TYPE", "SEQUENCE"],
        "separator": "-",
        "sequence_width": 5,
        "sequence_scope": "PROJECT",
    },
    "revision": {"scheme": "ALPHABETIC", "start": "A"},
    "workflow": {"default": "THREE_STEP"},
}

_ALPHABETIC_START = re.compile(r"^[A-Z]{1,3}$")
_NUMERIC_START = re.compile(r"^\d{1,4}$")


class DocumentControlConfigurationError(ValueError):
    pass


def default_document_control_configuration():
    return deepcopy(DEFAULT_DOCUMENT_CONTROL_CONFIGURATION)


def _section(raw, name):
    value = raw.get(name, {})
    if value in (None, ""):
        return {}
    if not isinstance(value, dict):
        raise DocumentControlConfigurationError(f"{name} must be an object.")
    allowed = set(DEFAULT_DOCUMENT_CONTROL_CONFIGURATION[name])
    unknown = set(value) - allowed
    if unknown:
        raise DocumentControlConfigurationError(
            f"Unknown {name} setting(s): {', '.join(sorted(unknown))}."
        )
    return value


def resolve_document_control_configuration(raw):
    """Merge a stored (possibly empty/partial) object over the canonical defaults."""
    if raw in (None, ""):
        raw = {}
    if not isinstance(raw, dict):
        raise DocumentControlConfigurationError(
            "document_control_configuration must be an object."
        )
    unknown = set(raw) - set(DEFAULT_DOCUMENT_CONTROL_CONFIGURATION)
    if unknown:
        raise DocumentControlConfigurationError(
            f"Unknown section(s): {', '.join(sorted(unknown))}."
        )
    resolved = default_document_control_configuration()
    for name in resolved:
        resolved[name].update(deepcopy(_section(raw, name)))
    return resolved


def validate_document_control_configuration(raw):
    """Return the resolved configuration or raise DocumentControlConfigurationError."""
    resolved = resolve_document_control_configuration(raw)

    reference = resolved["reference"]
    segments = reference["segments"]
    if not isinstance(segments, list) or not segments:
        raise DocumentControlConfigurationError("reference.segments must be a non-empty list.")
    invalid = [s for s in segments if s not in REFERENCE_SEGMENTS]
    if invalid:
        raise DocumentControlConfigurationError(
            f"Invalid reference segment(s): {', '.join(map(str, invalid))}."
        )
    if len(segments) != len(set(segments)):
        raise DocumentControlConfigurationError("reference.segments cannot contain duplicates.")
    if segments.count("SEQUENCE") != 1:
        raise DocumentControlConfigurationError(
            "reference.segments must contain SEQUENCE exactly once."
        )

    separator = reference["separator"]
    if (
        not isinstance(separator, str)
        or not 1 <= len(separator) <= 2
        or any(char not in SAFE_SEPARATORS for char in separator)
    ):
        raise DocumentControlConfigurationError(
            f"reference.separator must be 1-2 characters among '{SAFE_SEPARATORS}'."
        )

    width = reference["sequence_width"]
    if isinstance(width, bool) or not isinstance(width, int) or not 1 <= width <= MAX_SEQUENCE_WIDTH:
        raise DocumentControlConfigurationError(
            f"reference.sequence_width must be an integer between 1 and {MAX_SEQUENCE_WIDTH}."
        )

    if reference["sequence_scope"] not in SEQUENCE_SCOPES:
        raise DocumentControlConfigurationError(
            f"reference.sequence_scope must be one of: {', '.join(SEQUENCE_SCOPES)}."
        )

    revision = resolved["revision"]
    if revision["scheme"] not in REVISION_SCHEMES:
        raise DocumentControlConfigurationError(
            f"revision.scheme must be one of: {', '.join(REVISION_SCHEMES)}."
        )
    start = revision["start"]
    pattern = _ALPHABETIC_START if revision["scheme"] == "ALPHABETIC" else _NUMERIC_START
    if not isinstance(start, str) or not pattern.match(start):
        raise DocumentControlConfigurationError(
            "revision.start is not compatible with revision.scheme "
            "(ALPHABETIC: A-Z letters, NUMERIC: digits)."
        )

    if resolved["workflow"]["default"] not in WORKFLOW_DEFAULTS:
        raise DocumentControlConfigurationError(
            f"workflow.default must be one of: {', '.join(WORKFLOW_DEFAULTS)}."
        )
    return resolved


def get_document_control_configuration(config):
    """Resolved configuration of a config row (CompanyConfig / ECPMPConfig / None)."""
    raw = getattr(config, "document_control_configuration", None) if config else None
    try:
        return validate_document_control_configuration(raw)
    except DocumentControlConfigurationError:
        # A stored invalid object must never break document creation: use the defaults.
        return default_document_control_configuration()
