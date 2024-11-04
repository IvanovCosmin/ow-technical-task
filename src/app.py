from fastapi import FastAPI
from src.routers.usage import router as usage_router
from src.repositories.usage_repo import UsageRepo
from src.services.usage_service import UsageService

app = FastAPI()

app.include_router(usage_router)
# this is very useful because it is only initialised once and can
# be rewritten by the unit test testclient with a mock repo
app.state.service_usage = UsageService(UsageRepo())


@app.get("/")
async def root():
    return {"message": "Please visit /usage"}
