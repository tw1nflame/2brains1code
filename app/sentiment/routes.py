
from fastapi import APIRouter, Request
from sentiment.models import Comment
from fastapi.responses import JSONResponse
from templates import templates
import pandas as pd
from data_analyze.model_usage import process_with_model


router = APIRouter(prefix="")

@router.post("/api/sentiment")
async def analyse_one_sentiment(request: Request, comment: Comment):
    df = pd.DataFrame({"text": [comment.text]})
        
    result_df = await process_with_model(df)
    
    return JSONResponse({
        "text": comment.text,
        "sentiment": result_df["label"].iloc[0],
        "confidence": round(float(result_df["confidence"].iloc[0]), 4)
    })


@router.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("main.html", {'request': request})

