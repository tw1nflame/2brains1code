from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sentiment.routes import router as sentiment_router
from data_analyze.routes import router as data_analyze_router


app = FastAPI()

app.mount("/static", StaticFiles(directory=r"D:\Work\AI Learning lab\2brains1code\app\static"), name="static")


app.include_router(
    sentiment_router,
    tags=["sentiment"],
)

app.include_router(
    data_analyze_router,
    tags=['data_analyze']
)
