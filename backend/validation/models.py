from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ValidationStatus(StrEnum):
    READY = "ready"
    WARNING = "warning"
    UNSAFE = "unsafe"


class CheckStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class ValidationIssue(BaseModel):
    code: str
    message: str
    category: str
    waypoint: int | None = None


class ValidationCheck(BaseModel):
    name: str
    category: str
    status: CheckStatus
    message: str


class ValidationSummary(BaseModel):
    errors: int
    warnings: int
    passed: bool
    passed_checks: int
    failed_checks: int


class MissionValidationResponse(BaseModel):
    status: ValidationStatus
    score: int = Field(ge=0, le=100)
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    checks: list[ValidationCheck]
    summary: ValidationSummary
