"""PII masker — regex-based detection and masking for multi-jurisdiction PII patterns.

Supports India, EU, and UK PII patterns. All patterns are applied simultaneously —
a single text can have Indian, EU, and UK PII detected and masked in one pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class MaskResult:
    masked_text: str
    pii_found: list[str]
    pii_count: int


# ---------------------------------------------------------------------------
# India PII patterns
# ---------------------------------------------------------------------------

# Aadhaar: 12 digits, optional spaces (XXXX XXXX 1234 — last 4 visible)
_AADHAAR = re.compile(r"\b(\d{4})\s?(\d{4})\s?(\d{4})\b")

# PAN: ABCDE1234F
_PAN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")

# Indian mobile: +91 or 0 prefix, 10 digits
_MOBILE = re.compile(r"(?:\+91[\s-]?|0)?([6-9]\d{9})\b")

# UPI ID: name@bank
_UPI = re.compile(r"\b[\w.]+@[a-zA-Z]{2,}\b")

# ---------------------------------------------------------------------------
# EU / UK PII patterns
# ---------------------------------------------------------------------------

# UK National Insurance Number: AB123456C (2 letters, 6 digits, 1 letter)
_UK_NINO = re.compile(
    r"\b([A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])\s?(\d{2})\s?(\d{2})\s?(\d{2})\s?([A-D])\b"
)

# IBAN: 2-letter country code + 2 check digits + up to 30 alphanumeric (total up to 34)
_IBAN = re.compile(r"\b([A-Z]{2})(\d{2})\s?([A-Z0-9]{4})\s?([A-Z0-9\s]{4,26})([A-Z0-9]{1,4})\b")

# UK Sort Code: 12-34-56
_UK_SORT_CODE = re.compile(r"\b(\d{2})-(\d{2})-(\d{2})\b")

# EU/UK phone numbers: +44, +33, +49, +34, +39, +31, +32, +353, +43, +48, etc.
_EU_UK_PHONE = re.compile(
    r"\+(?:44|33|49|34|39|31|32|353|43|48|46|47|45|358|30|351|36|40|420|421)"
    r"[\s-]?\d[\d\s-]{6,12}\d\b"
)

# Passport number: basic pattern — 1-2 letters followed by 6-9 digits
_PASSPORT = re.compile(r"\b([A-Z]{1,2})(\d{6,9})\b")

# ---------------------------------------------------------------------------
# Global PII patterns
# ---------------------------------------------------------------------------

# Email
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


class PIIMasker:
    """Detect and mask PII patterns across India, EU, and UK jurisdictions."""

    def mask(self, text: str) -> MaskResult:
        if not text:
            return MaskResult(masked_text=text, pii_found=[], pii_count=0)

        found: list[str] = []
        masked = text

        # --- India patterns ---

        # Aadhaar — keep last 4 digits
        for m in _AADHAAR.finditer(text):
            found.append("aadhaar")
            masked = masked.replace(m.group(), f"XXXX XXXX {m.group(3)}")

        # PAN
        for m in _PAN.finditer(masked):
            found.append("pan")
            masked = masked.replace(m.group(), "XXXXX0000X")

        # Indian Mobile
        for m in _MOBILE.finditer(masked):
            found.append("mobile")
            full = m.group()
            masked = masked.replace(full, re.sub(r"\d", "X", full))

        # UPI
        for m in _UPI.finditer(masked):
            if "@" in m.group() and "." not in m.group().split("@")[1]:
                found.append("upi")
                masked = masked.replace(m.group(), "XXXX@XXXX")

        # --- EU / UK patterns ---

        # UK National Insurance Number — keep last letter
        for m in _UK_NINO.finditer(masked):
            found.append("uk_nino")
            last_letter = m.group(5)
            masked = masked.replace(m.group(), f"XX XXXXXX {last_letter}")

        # IBAN — mask middle digits, keep country code and last 4
        for m in _IBAN.finditer(masked):
            found.append("iban")
            country = m.group(1)
            last4 = m.group(5)
            masked = masked.replace(m.group(), f"{country}XX XXXX XXXX {last4}")

        # UK Sort Code — keep last 2 digits
        for m in _UK_SORT_CODE.finditer(masked):
            found.append("uk_sort_code")
            masked = masked.replace(m.group(), f"XX-XX-{m.group(3)}")

        # EU/UK phone numbers
        for m in _EU_UK_PHONE.finditer(masked):
            found.append("eu_uk_phone")
            full = m.group()
            # Keep the country code prefix, mask the rest
            plus_idx = full.index("+")
            # Find end of country code (first space or dash after digits)
            rest = re.sub(r"\d", "X", full[plus_idx:])
            masked = masked.replace(full, rest)

        # Passport number — mask digits, keep letter prefix
        for m in _PASSPORT.finditer(masked):
            found.append("passport")
            prefix = m.group(1)
            masked = masked.replace(m.group(), f"{prefix}XXXXXXX")

        # --- Global patterns ---

        # Email
        for m in _EMAIL.finditer(masked):
            found.append("email")
            masked = masked.replace(m.group(), "[email]@[domain]")

        return MaskResult(masked_text=masked, pii_found=found, pii_count=len(found))
