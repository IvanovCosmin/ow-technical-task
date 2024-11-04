import asyncio
from collections import defaultdict
from typing import Any, Coroutine, Sequence
from pydantic import BaseModel, TypeAdapter, ValidationError
import httpx
from asyncio import Semaphore

import logging

# sharing the same client as HTTP session creation is costly
# I am aware the client stays open
_httpx_client = httpx.AsyncClient()

# Let's do up to x requests for report data at a time 
REPORT_GATHERING_CONCURRENCY_LIMIT = 25

ReportIdType = int
MessageIdType = int

class Message(BaseModel):
    text: str
    timestamp: str # could be a datetime, but no reason to overcomplicate
    report_id: ReportIdType | None = None
    id: MessageIdType

# It was supposed to be an iterator, but I have already found a bug in pydantic
# https://github.com/pydantic/pydantic/issues/9541
# it happens :/
message_iterable_type_adapter = TypeAdapter[Sequence[Message]](Sequence[Message])

class Report(BaseModel):
    id: MessageIdType
    name: str
    credit_cost: int

class MessageWithReport(Message):
    report: Report | None = None


class UsageRepo():
    @staticmethod
    async def get_current_period() -> Sequence[Message] | None:
        URL_GET_CURRENT_PERIOD = "https://owpublic.blob.core.windows.net/tech-task/messages/current-period"
        result = await _httpx_client.get(URL_GET_CURRENT_PERIOD)
        
        if result.status_code != 200:
            return None
        
        json_data = result.json()
        messages: Sequence[Message] | None = None

        try:
            if "messages" in json_data:
                messages = message_iterable_type_adapter.validate_python(json_data["messages"])
        except ValidationError as e:
            # not showing messages here because it is potentially very large
            logging.error(f"Validation error from get_report. Ignoring result. {e!r}")            
        return messages
    
    @classmethod
    async def get_current_period_with_reports(cls) -> Sequence[MessageWithReport] | None:
        messages = await cls.get_current_period()
        if messages is None:
            return None
        
        task_list: list[Coroutine[Any, Any, tuple[Report | None, int]]] = []
        report_reference_table: dict[ReportIdType, list[int]] = defaultdict(lambda : [])

        new_message_list: list[MessageWithReport] = []

        semaphore = Semaphore(REPORT_GATHERING_CONCURRENCY_LIMIT)
        
        async def _semaphored_get_report(report_id: int, message_id: int) -> tuple[Report | None, int]:
            async with semaphore:
                return (await cls.get_report(report_id=report_id), message_id)

        for idx, message in enumerate(messages):
            if message.report_id is not None:
                task_list.append(_semaphored_get_report(message.report_id, message.id))
                report_reference_table[message.report_id].append(idx)
            
            new_message_list.append(MessageWithReport(**message.model_dump()))

        reports = await asyncio.gather(*task_list)
        for report, message_id in reports:
            if report is None:
                # Here you would need to retry or have some sort of error case.
                # I chose to just continue without it
                logging.error(f"Unxpected None result on report for message_id {message_id=}")
                continue
            else:
                # modifying the list in line
                for idx in report_reference_table[report.id]:
                    item = new_message_list[idx]
                    item.report = report

        return new_message_list

    
    @staticmethod
    async def get_report(report_id: int) -> Report | None:
        URL_REPORTS = f"https://owpublic.blob.core.windows.net/tech-task/reports/{report_id}"
        result = await _httpx_client.get(URL_REPORTS.format_map({
            "id": report_id
        }))
        if result.status_code != 200:
            return None

        report_data = result.json()
        report: Report | None = None
        try:
            # check if the report we got has the right fields
            report = Report.model_validate(report_data)
        except ValidationError as e:
            logging.error(f"Validation error from get_report. Ignoring result. {report_data=} {e!r}")

        return report