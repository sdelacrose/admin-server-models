from models.constants import GC_ROOMS


def effective_rooms_list(rooms):
    """Return stored rooms, falling back to GC_ROOMS when empty."""
    stored = [str(item).strip() for item in (rooms or []) if str(item).strip()]
    return stored if stored else list(GC_ROOMS)


def bootstrap_rooms_if_legacy_empty(instance_rooms, normalized):
    """Prepend default rooms for legacy configs that were never seeded."""
    if (instance_rooms or []) or len(normalized) >= len(GC_ROOMS):
        return normalized

    extras = [room for room in normalized if room not in GC_ROOMS]
    merged = list(GC_ROOMS) + extras
    seen = set()
    result = []
    for room in merged:
        if room not in seen:
            seen.add(room)
            result.append(room)
    return result
