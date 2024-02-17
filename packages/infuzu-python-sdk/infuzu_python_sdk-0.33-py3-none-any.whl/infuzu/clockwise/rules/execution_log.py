from dataclasses import dataclass
from datetime import datetime


@dataclass
class Execution:
    task_id: str
    rule_id: str
    start_datetime: datetime
    end_datetime: datetime
    request_details: dict[str, any]
    response_details: dict[str, any]
    execution_details: dict[str, any]

    @classmethod
    def from_logs_api_call(cls, execution_log_list: list[dict[str, any]]) -> list['Execution']:
        executions_list: list['Execution'] = []
        for execution_log in execution_log_list:
            executions_list.append(
                cls(
                    task_id=execution_log["task_id"],
                    rule_id=execution_log["rule_id"],
                    start_datetime=datetime.fromisoformat(execution_log["start_datetime"]),
                    end_datetime=datetime.fromisoformat(execution_log["end_datetime"]),
                    request_details=execution_log["request_details"],
                    response_details=execution_log["response_details"],
                    execution_details=execution_log["execution_details"]
                )
            )
        return executions_list
