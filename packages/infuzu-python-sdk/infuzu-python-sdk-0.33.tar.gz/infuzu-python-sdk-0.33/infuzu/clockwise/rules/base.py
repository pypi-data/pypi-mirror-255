from dataclasses import dataclass
from datetime import (timedelta, datetime, timezone)
from ...utils.enums.api_calls import HttpMethod


@dataclass
class Rule:
    name: str
    url: str
    rule_id: str | None = None
    interval: timedelta = timedelta(days=1)
    start_datetime: datetime = datetime.utcnow().replace(tzinfo=timezone.utc)
    end_datetime: datetime | None = None
    max_executions: int | None = None
    http_method: HttpMethod = HttpMethod.GET
    headers: dict | None = None
    body: dict | None = None
    max_retries: int = 0
    timeout: int = 30
    static: bool = False

    def to_create_rule_dict(self) -> dict[str, any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "interval": self.interval.total_seconds(),
            "start_datetime": self.start_datetime.isoformat(),
            "end_datetime": self.end_datetime.isoformat() if isinstance(self.end_datetime, datetime) else None,
            "max_executions": self.max_executions,
            "url": self.url,
            "http_method": self.http_method.name,
            "headers": self.headers,
            "body": self.body,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "static": self.static
        }


@dataclass
class CreatedRule:
    id: str
    key_pair_id: str
    public_key: str
