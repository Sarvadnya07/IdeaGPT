from enum import Enum
from typing import Optional, Dict, Set
from datetime import datetime

class EvaluationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class EvaluationProgress(str, Enum):
    PENDING = "PENDING"
    VALIDATION = "VALIDATION"
    RULE_EXECUTION = "RULE_EXECUTION"
    SCORING = "SCORING"
    INSIGHTS = "INSIGHTS"
    SAVING = "SAVING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

# Numeric progress mapping for API reporting
PROGRESS_PERCENTAGES: Dict[str, int] = {
    EvaluationProgress.PENDING: 0,
    EvaluationProgress.VALIDATION: 10,
    EvaluationProgress.RULE_EXECUTION: 30,
    EvaluationProgress.SCORING: 60,
    EvaluationProgress.INSIGHTS: 80,
    EvaluationProgress.SAVING: 95,
    EvaluationProgress.COMPLETED: 100,
    EvaluationProgress.FAILED: 0,
    EvaluationProgress.CANCELLED: 0,
}

# Authoritative State Machine Matrix
VALID_TRANSITIONS: Dict[EvaluationStatus, Set[EvaluationStatus]] = {
    EvaluationStatus.PENDING: {
        EvaluationStatus.RUNNING,
        EvaluationStatus.FAILED,
        EvaluationStatus.CANCELLED,
    },
    EvaluationStatus.RUNNING: {
        EvaluationStatus.COMPLETED,
        EvaluationStatus.FAILED,
        EvaluationStatus.CANCELLED,
    },
    EvaluationStatus.COMPLETED: set(),  # Terminal state
    EvaluationStatus.FAILED: {
        EvaluationStatus.PENDING,  # Retry transition
    },
    EvaluationStatus.CANCELLED: {
        EvaluationStatus.PENDING,  # Retry transition
    },
}

class InvalidStateTransitionError(Exception):
    def __init__(self, current_status: str, target_status: str, detail: Optional[str] = None):
        self.current_status = current_status
        self.target_status = target_status
        msg = f"Cannot transition evaluation from '{current_status}' to '{target_status}'."
        if detail:
            msg += f" {detail}"
        super().__init__(msg)
        self.detail = msg

class EvaluationConcurrencyConflictError(Exception):
    def __init__(self, evaluation_id: str, current_status: str):
        self.evaluation_id = evaluation_id
        self.current_status = current_status
        msg = f"Evaluation '{evaluation_id}' is currently locked or running in state '{current_status}'."
        super().__init__(msg)
        self.detail = msg

class EvaluationNotFoundError(Exception):
    def __init__(self, evaluation_id: str):
        self.evaluation_id = evaluation_id
        msg = f"Evaluation '{evaluation_id}' not found."
        super().__init__(msg)
        self.detail = msg

class EvaluationAccessDeniedError(Exception):
    def __init__(self, evaluation_id: str):
        self.evaluation_id = evaluation_id
        msg = f"Access denied for evaluation '{evaluation_id}'."
        super().__init__(msg)
        self.detail = msg


def can_transition(current: str, target: str) -> bool:
    """Check if state transition from current to target is allowed."""
    try:
        curr_enum = EvaluationStatus(current.upper())
        targ_enum = EvaluationStatus(target.upper())
    except ValueError:
        return False
    return targ_enum in VALID_TRANSITIONS.get(curr_enum, set())


def validate_transition(current: str, target: str, detail: Optional[str] = None) -> None:
    """Validate state transition or raise InvalidStateTransitionError."""
    if not can_transition(current, target):
        raise InvalidStateTransitionError(current, target, detail)
