"""LOT 2D-12: Company Code -- the permanent short code used in COMPANY-scope Document
references (COMPANY_CODE-DISCIPLINE_CODE-DOCUMENT_TYPE_CODE-SEQUENCE).

Deliberately mirrors ``project_management.services.project_codes`` (the ``backend`` repository)
as closely as possible: same derivation principle, same uniqueness-then-lock lifecycle. This
module only holds the pure, CompanyProfile-only half of that lifecycle (derive / propose /
format-and-uniqueness validation); it must not depend on ``project_management`` (Document lives
in the separate `backend` repository, which is the one that depends on this package, never the
other way round). The Document-aware half (the *lock* check, and the change-refusal it drives)
therefore lives in ``backend/project_management/services/company_codes.py`` instead.
"""

import re

from django.core.exceptions import ValidationError

MAX_LENGTH = 10
FALLBACK_CODE = "CMP"
_CODE_RE = re.compile(r"^[A-Z0-9]{1,%d}$" % MAX_LENGTH)


def derive_company_code(company_name):
    """Simple deterministic proposal: initials of the words (2-4 words), else the first 3
    letters. Identical convention to project_codes.derive_project_code.

    "Sharemundo Links" -> SL, "Acme Engineering" -> AE, "Acme" -> ACM.
    """
    words = re.findall(r"[A-Za-z0-9]+", str(company_name or ""))
    if len(words) >= 2:
        return "".join(word[0] for word in words[:4]).upper()
    if words:
        return words[0][:3].upper()
    return FALLBACK_CODE


def normalize_company_code(value):
    return re.sub(r"[^A-Za-z0-9]", "", str(value or "")).upper()


def is_company_code_taken(company, code):
    """Company codes are unique platform-wide: there is no owner scope above a company."""
    from models.models import CompanyProfile

    others = CompanyProfile.objects.filter(company_code=code)
    if company.pk:
        others = others.exclude(pk=company.pk)
    return others.exists()


def propose_unique_company_code(company):
    base = derive_company_code(company.company_name)
    candidate, number = base, 1
    while is_company_code_taken(company, candidate):
        number += 1
        suffix = str(number)
        candidate = f"{base[: MAX_LENGTH - len(suffix)]}{suffix}"
    return candidate


def validate_company_code_value(company, code):
    if not _CODE_RE.match(code):
        raise ValidationError(
            f"The company code must be 1-{MAX_LENGTH} letters or digits."
        )
    if is_company_code_taken(company, code):
        raise ValidationError("This company code is already used by another company.")
