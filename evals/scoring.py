# evals/scoring.py
from dataclasses import dataclass, field


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class TestCaseResult:
    case_id: str
    task: str
    checks: list = field(default_factory=list)

    @property
    def score(self) -> float:
        if not self.checks:
            return 0.0
        return sum(c.passed for c in self.checks) / len(self.checks)

    @property
    def passed(self) -> bool:
        return self.score >= 0.7

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "task": self.task,
            "score": round(self.score, 2),
            "passed": self.passed,
            "checks": [{"name": c.name, "passed": c.passed, "detail": c.detail} for c in self.checks],
        }