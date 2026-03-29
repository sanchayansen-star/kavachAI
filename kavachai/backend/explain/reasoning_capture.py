"""LLM reasoning capture — extract chain-of-thought from LLM responses."""

from __future__ import annotations

from typing import Any


class LLMReasoningCapture:
    """Capture chain-of-thought reasoning from LLM interactions."""

    REASONING_INSTRUCTION = (
        "Before answering, explain your reasoning step by step in a <reasoning> block. "
        "Then provide your final answer."
    )

    @staticmethod
    def inject_reasoning_prompt(messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """Inject reasoning capture instruction into system prompt."""
        if not messages:
            return [{"role": "system", "content": LLMReasoningCapture.REASONING_INSTRUCTION}]

        result = list(messages)
        if result[0].get("role") == "system":
            result[0] = {
                "role": "system",
                "content": result[0]["content"] + "\n\n" + LLMReasoningCapture.REASONING_INSTRUCTION,
            }
        else:
            result.insert(0, {"role": "system", "content": LLMReasoningCapture.REASONING_INSTRUCTION})
        return result

    @staticmethod
    def extract_reasoning(response_text: str) -> tuple[str | None, str]:
        """Extract reasoning block from LLM response.

        Returns (reasoning, clean_response).
        """
        import re
        match = re.search(r"<reasoning>(.*?)</reasoning>", response_text, re.DOTALL)
        if match:
            reasoning = match.group(1).strip()
            clean = response_text[:match.start()] + response_text[match.end():]
            return reasoning, clean.strip()
        return None, response_text
