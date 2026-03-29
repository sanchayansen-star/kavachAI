"""PII masker — regex-based detection and masking for Indian PII patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class MaskResult:
    masked_text: str
    pii_found: list[str]
    pii_count: int


# Aadhaar: 12 digits, optional spaces (XXXX XXXX 1234 — last 4 visible)
_AADHAAR = re.compile(r"\b(\d{4})\s?(\d{4})\s?(\d{4})\b")

# PAN: ABCDE1234F
_PAN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")

# Indian mobile: +91 or 0 prefix, 10 digits
_MOBILE = re.compile(r"(?:\+91[\s-]?|0)?([6-9]\d{9})\b")

# UPI ID: name@bank
_UPI = re.compile(r"\b[\w.]+@[a-zA-Z]{2,}\b")

# Email
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


class PIIMasker:
    """Detect and mask Indian PII patterns in text."""

    def mask(self, text: str) -> MaskResult:
        if not text:
            return MaskResult(masked_text=text, pii_found=[], pii_count=0)

        found: list[str] = []
        masked = text

        # Aadhaar — keep last 4 digits
        for m in _AADHAAR.finditer(text):
            found.append("aadhaar")
            masked = masked.replace(m.group(), f"XXXX XXXX {m.group(3)}")

        # PAN
        for m in _PAN.finditer(masked):
            found.append("pan")
            masked = masked.replace(m.group(), "XXXXX0000X")

        # Mobile
        for m in _MOBILE.finditer(masked):
            found.append("mobile")
            full = m.group()
            masked = masked.replace(full, re.sub(r"\d", "X", full))

        # UPI
        for m in _UPI.finditer(masked):
            if "@" in m.group() and "." not in m.group().split("@")[1]:
                found.append("upi")
                masked = masked.replace(m.group(), "XXXX@XXXX")

        # Email
        for m in _EMAIL.finditer(masked):
            found.append("email")
            masked = masked.replace(m.group(), "[email]@[domain]")

        return MaskResult(masked_text=masked, pii_found=found, pii_count=len(found))
