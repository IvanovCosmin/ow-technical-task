from typing import Sequence
import pytest
from src.repositories.usage_repo import MessageWithReport, UsageRepo, Report

@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "report_id,expected_result", [(5392, Report(
        id=5392,
        name="Tenant Obligations Report",
        credit_cost=79
    )), (99999, None) 
    ]
)
async def test_usage_repo_get_report(report_id: int, expected_result: Report | None):
    # this is a very bad test as it is based on the behaviour of an 
    # external api
    # it still helps me while I am developing
    # it be nice to have a mock server here

    report: Report | None = await UsageRepo.get_report(report_id)
    assert report == expected_result

@pytest.mark.asyncio()
async def test_usage_repo_get_current_period():
    messages = await UsageRepo.get_current_period()
    assert messages is not None, "Server responded unexpectedly, check logs"
    assert len(messages) > 0, "Expected to find at least a result"


    first_message = messages[0]
    assert first_message.text != ""
    assert first_message.timestamp != ""
    

@pytest.mark.asyncio()
async def test_usgae_repo_get_current_period_with_reports():
    messages: Sequence[MessageWithReport] | None = await UsageRepo.get_current_period_with_reports()
    assert messages is not None, "Server responded unexpectedly, check logs"
    assert len(messages) > 0, "Expected to find at least a result"


    first_message = messages[0]
    assert first_message.text != ""
    assert first_message.timestamp != ""

    for message in messages:
        if message.report_id is not None:
            assert message.report is not None
            # stoping after first because there are some messages with reports
            # but no report with that id exists
            # I would normally filter here
            break