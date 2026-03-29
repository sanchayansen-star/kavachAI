"""DFA behavioral model engine — track agent state transitions per session."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any


@dataclass
class DFAModel:
    model_id: str
    name: str
    states: list[dict[str, Any]]  # [{id, type, label}]
    transitions: list[dict[str, Any]]  # [{from, to, tool_pattern, guard}]

    @property
    def initial_state(self) -> str | None:
        for s in self.states:
            if s.get("state_type") == "initial":
                return s["name"]
        return self.states[0]["name"] if self.states else None

    @property
    def dangerous_states(self) -> set[str]:
        return {s["name"] for s in self.states if s.get("state_type") == "dangerous"}


@dataclass
class TransitionResult:
    valid: bool
    new_state: str | None
    is_dangerous: bool
    reason: str


class DFAEngine:
    """Load DFA models, track current state per session, validate transitions."""

    def __init__(self) -> None:
        self._models: dict[str, DFAModel] = {}
        # session_id -> (model_id, current_state)
        self._session_states: dict[str, tuple[str, str]] = {}
        # session_id -> list of tool calls for path analysis
        self._session_paths: dict[str, list[str]] = {}

    def load_model(self, model: DFAModel) -> None:
        self._models[model.model_id] = model

    def start_session(self, session_id: str, model_id: str) -> bool:
        model = self._models.get(model_id)
        if not model or not model.initial_state:
            return False
        self._session_states[session_id] = (model_id, model.initial_state)
        self._session_paths[session_id] = []
        return True

    def get_state(self, session_id: str) -> str | None:
        entry = self._session_states.get(session_id)
        return entry[1] if entry else None

    def validate_transition(self, session_id: str, tool_name: str) -> TransitionResult:
        """Validate a tool call against the DFA model for this session."""
        entry = self._session_states.get(session_id)
        if not entry:
            return TransitionResult(valid=True, new_state=None, is_dangerous=False, reason="No DFA model active")

        model_id, current_state = entry
        model = self._models.get(model_id)
        if not model:
            return TransitionResult(valid=True, new_state=None, is_dangerous=False, reason="Model not found")

        # Find valid transitions from current state
        for tr in model.transitions:
            if tr["from"] != current_state:
                continue
            patterns = tr["tool_pattern"]
            if isinstance(patterns, str):
                patterns = [patterns]
            for pat in patterns:
                if pat == "*" or fnmatch.fnmatch(tool_name, pat):
                    new_state = tr["to"]
                    is_dangerous = new_state in model.dangerous_states
                    self._session_states[session_id] = (model_id, new_state)
                    self._session_paths.setdefault(session_id, []).append(tool_name)
                    return TransitionResult(
                        valid=True,
                        new_state=new_state,
                        is_dangerous=is_dangerous,
                        reason=f"Transition {current_state} -> {new_state}",
                    )

        # No valid transition found
        self._session_paths.setdefault(session_id, []).append(tool_name)
        return TransitionResult(
            valid=False,
            new_state=current_state,
            is_dangerous=False,
            reason=f"No valid transition from '{current_state}' on '{tool_name}'",
        )

    def get_path_correctness(self, session_id: str) -> float:
        """Compute path correctness: ratio of valid transitions to total calls."""
        path = self._session_paths.get(session_id, [])
        if not path:
            return 1.0
        # Re-simulate to count valid transitions
        entry = self._session_states.get(session_id)
        if not entry:
            return 1.0
        model_id = entry[0]
        model = self._models.get(model_id)
        if not model or not model.initial_state:
            return 1.0

        state = model.initial_state
        valid_count = 0
        for tool in path:
            found = False
            for tr in model.transitions:
                if tr["from"] != state:
                    continue
                patterns = tr["tool_pattern"] if isinstance(tr["tool_pattern"], list) else [tr["tool_pattern"]]
                for pat in patterns:
                    if pat == "*" or fnmatch.fnmatch(tool, pat):
                        state = tr["to"]
                        valid_count += 1
                        found = True
                        break
                if found:
                    break

        return valid_count / len(path)
