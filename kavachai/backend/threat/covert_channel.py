"""Covert channel detection — steganographic encoding, base64 payloads, unusual characters."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass


@dataclass
class CovertChannelResult:
    detected: bool
    score: float
    indicators: list[str]


_ZERO_WIDTH_PATTERN = re.compile(r"[\u200b\u200c\u200d\ufeff\u2060]")
_HIGH_ENTROPY_THRESHOLD = 4.5  # bits per character


class CovertChannelDetector:
    """Detect covert data exfiltration channels."""

    def detect(self, text: str) -> CovertChannelResult:
        if not text:
            return CovertChannelResult(detected=False, score=0.0, indicators=[])

        indicators: list[str] = []
        score = 0.0

        # Zero-width character steganography
        zw_matches = _ZERO_WIDTH_PATTERN.findall(text)
        if len(zw_matches) > 3:
            indicators.append(f"zero_width_chars: {len(zw_matches)}")
            score = max(score, 0.8)

        # Base64-encoded payloads
        b64_candidates = re.findall(r"[A-Za-z0-9+/]{40,}={0,2}", text)
        for candidate in b64_candidates:
            try:
                decoded = base64.b64decode(candidate)
                if len(decoded) > 10:
                    indicators.append("base64_payload")
                    score = max(score, 0.7)
                    break
            except Exception:
                pass

        # Unusual Unicode encoding (homoglyph attacks)
        non_ascii = sum(1 for c in text if ord(c) > 127)
        if non_ascii > len(text) * 0.3 and len(text) > 20:
            indicators.append(f"high_non_ascii_ratio: {non_ascii}/{len(text)}")
            score = max(score, 0.6)

        # Hex-encoded data
        hex_matches = re.findall(r"(?:0x)?[0-9a-fA-F]{20,}", text)
        if hex_matches:
            indicators.append(f"hex_encoded_data: {len(hex_matches)} segments")
            score = max(score, 0.5)

        return CovertChannelResult(detected=len(indicators) > 0, score=score, indicators=indicators)
