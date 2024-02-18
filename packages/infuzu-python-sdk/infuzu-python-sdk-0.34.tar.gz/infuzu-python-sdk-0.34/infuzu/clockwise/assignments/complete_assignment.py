from dataclasses import dataclass
from datetime import (datetime, timezone)
from ... import constants
from ...http_requests import signed_requests
from ...utils.api_calls.base import APIResponse
from .retrieve_assignment import Assignment


@dataclass
class CompleteAssignment:
    assignment: Assignment
    start_datetime: datetime
    end_datetime: datetime
    response: APIResponse

    def to_assignment_completion_dict(self) -> dict[str, any]:
        return {
            "rule_id": self.assignment.rule_id,
            "start_datetime": self.start_datetime.isoformat(),
            "end_datetime": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "request_details": self.assignment.to_dict(),
            "response_details": self.response.response_dict,
            "execution_details": self.response.execution_dict
        }


def assignment_complete(complete_assignment: CompleteAssignment) -> None:
    signed_requests.post(
        url=f"{constants.CLOCKWISE_BASE_URL}{constants.CLOCKWISE_ASSIGNMENT_COMPLETE_ENDPOINT}",
        json=complete_assignment.to_assignment_completion_dict()
    )
