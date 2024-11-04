from typing import cast
from pydantic import Field, BaseModel

from fastapi import APIRouter, Request

from src.services.usage_service import UsageService

# setting up a new router to keep app.py clean
router = APIRouter(
    prefix="/usage"
)

class UsageResult(BaseModel):
    message_id: int = Field(ge=0) # positive number
    timestamp: str
    report_name: str | None = None
    credits_used: float

class UsageResponse(BaseModel):
    usage: list[UsageResult]


@router.get("/", response_model=UsageResponse, response_model_exclude_none=True)
async def usage(request: Request):
    usage_service = cast(UsageService, request.app.state.service_usage)
    return UsageResponse(
        usage=[
            UsageResult(
                message_id=result.message_id,
                timestamp=result.timestamp,
                report_name=result.report_name,
                credits_used=result.credits_used
            ) for result in await usage_service.get_usage()
        ]
    )