"""LLM evaluation, safety benchmarks, and red-team models."""

from datetime import datetime

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    prompt: str
    expected_safe: bool
    category: str


class TestSuite(BaseModel):
    suite_type: str  # prompt_injection | toxicity | bias | hallucination | accuracy | domain_specific
    test_cases: list[TestCase] = Field(default_factory=list)
    weight: float = 1.0


class SafetyBenchmark(BaseModel):
    benchmark_id: str
    name: str
    test_suites: list[TestSuite] = Field(default_factory=list)
    threshold: int = 70
    tenant_id: str = "default"


class ModelSafetyScore(BaseModel):
    model_name: str
    model_version: str
    overall_score: int = 0
    sub_scores: dict[str, int] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    benchmark_id: str = ""
    passed: bool = False


class RedTeamResult(BaseModel):
    run_id: str
    model_name: str
    adversarial_cases_run: int = 0
    vulnerabilities_found: int = 0
    safety_score_delta: float = 0.0
    degraded: bool = False
    run_at: datetime = Field(default_factory=datetime.utcnow)
