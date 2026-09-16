import re
from dataclasses import dataclass


MIN_OFFER_VALIDITY_DURATION = 1
MAX_OFFER_VALIDITY_DURATION = 999
OFFER_VALIDITY_PERIOD_UNITS = ("day", "week", "month", "year")

_UNIT_ALIASES = {
    "day": "day",
    "days": "day",
    "week": "week",
    "weeks": "week",
    "month": "month",
    "months": "month",
    "year": "year",
    "years": "year",
}
_OFFER_VALIDITY_PERIOD_PATTERN = re.compile(
    r"^(?P<duration>\d+)\s*(?::|\s)\s*(?P<unit>[a-zA-Z]+)$"
)


class OfferValidityPeriodError(ValueError):
    pass


@dataclass(frozen=True)
class OfferValidityPeriod:
    duration: int
    unit: str

    @property
    def canonical_value(self):
        return f"{self.duration}:{self.unit}"


def parse_offer_validity_period(value):
    if not isinstance(value, str):
        raise OfferValidityPeriodError(
            "Offer validity periods must be strings."
        )

    match = _OFFER_VALIDITY_PERIOD_PATTERN.fullmatch(value.strip())
    if not match:
        raise OfferValidityPeriodError(
            "Offer validity periods must use '<duration>:<unit>'."
        )

    duration = int(match.group("duration"))
    if not MIN_OFFER_VALIDITY_DURATION <= duration <= MAX_OFFER_VALIDITY_DURATION:
        raise OfferValidityPeriodError(
            "Offer validity duration must be between "
            f"{MIN_OFFER_VALIDITY_DURATION} and {MAX_OFFER_VALIDITY_DURATION}."
        )

    raw_unit = match.group("unit").casefold()
    unit = _UNIT_ALIASES.get(raw_unit)
    if unit is None:
        supported_units = ", ".join(OFFER_VALIDITY_PERIOD_UNITS)
        raise OfferValidityPeriodError(
            f"Offer validity unit must be one of: {supported_units}."
        )

    return OfferValidityPeriod(duration=duration, unit=unit)


def normalize_offer_validity_period(value):
    return parse_offer_validity_period(value).canonical_value


def normalize_offer_validity_periods(values):
    if values is None:
        return []
    if not isinstance(values, (list, tuple)):
        raise OfferValidityPeriodError(
            "Offer validity periods must be a list."
        )

    normalized_values = []
    seen = set()
    for value in values:
        normalized = normalize_offer_validity_period(value)
        if normalized in seen:
            raise OfferValidityPeriodError(
                f"Duplicate Offer validity period: {normalized}."
            )
        seen.add(normalized)
        normalized_values.append(normalized)

    return normalized_values
