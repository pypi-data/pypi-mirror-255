from requests import Response
from .execution_log import Execution
from ... import constants
from .base import (Rule, CreatedRule)
from ...http_requests import signed_requests


def create_rule(rule_instance: Rule) -> CreatedRule:
    api_response: Response = signed_requests.post(
        url=f"{constants.CLOCKWISE_BASE_URL}{constants.CLOCKWISE_CREATE_RULE_ENDPOINT}",
        json=rule_instance.to_create_rule_dict()
    )

    if api_response.status_code == 200:
        created_rule: CreatedRule = CreatedRule(**api_response.json())
        rule_instance.rule_id = created_rule.id
        return created_rule


def delete_rule(rule: str | Rule | CreatedRule) -> bool:
    if isinstance(rule, str):
        rule_id: str = rule
    elif isinstance(rule, Rule):
        rule_id: str = rule.rule_id
    elif isinstance(rule, CreatedRule):
        rule_id: str = rule.id
    else:
        raise TypeError("rule must be a string, Rule or CreatedRule")
    api_response: Response = signed_requests.delete(
        url=f'{constants.CLOCKWISE_BASE_URL}'
            f'{constants.CLOCKWISE_DELETE_RULE_ENDPOINT.replace("<str:rule_id>", rule_id)}'
    )

    if api_response.status_code == 200:
        return True
    else:
        return False


def get_rule_logs(rule: str | Rule | CreatedRule) -> list[Execution]:
    if isinstance(rule, str):
        rule_id: str = rule
    elif isinstance(rule, Rule):
        rule_id: str = rule.rule_id
    elif isinstance(rule, CreatedRule):
        rule_id: str = rule.id
    else:
        raise TypeError("rule must be a string, Rule or CreatedRule")
    api_response: Response = signed_requests.get(
        url=f'{constants.CLOCKWISE_BASE_URL}'
            f'{constants.CLOCKWISE_RULE_LOGS_ENDPOINT.replace("<str:rule_id>", rule_id)}'
    )

    if api_response.status_code == 200:
        return Execution.from_logs_api_call(api_response.json())
