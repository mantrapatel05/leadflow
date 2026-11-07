from fastapi import FastAPI

app = FastAPI(
    title="LeadFlow API",
    description="Real-time Meta Lead Ads processing system",
    version="0.1",
)


@app.get("/")
async def root():
    return {
        "message": "LeadFlow API",
        "project": "LeadFlow",
        "status": "running",
    }