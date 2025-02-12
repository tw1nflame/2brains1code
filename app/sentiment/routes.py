
from fastapi import APIRouter, Request
from sentiment.models import Comment
from fastapi.responses import JSONResponse
from templates import templates

router = APIRouter(prefix="")

@router.post("/api/sentiment")
def analyse_one_sentiment(request: Request, comment: Comment):
    json = {
        "sentiment": "Позитивный",
        "confidence": 0.95
        }
    return JSONResponse(content=json)


@router.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("main.html", {'request': request})

