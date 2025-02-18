from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sentiment.routes import router as sentiment_router
from data_analyze.routes import router as data_analyze_router
from markup.routes import router as markup_router
from training.routes import router as training_router
from training.tasks import lifespan

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(
    sentiment_router,
    tags=["sentiment"],
)

app.include_router(
    data_analyze_router,
    tags=['data_analyze']
)

app.include_router(
    markup_router,
    tags=['markup_router']
)

app.include_router(
    training_router,
    tags=['training_router']
)
