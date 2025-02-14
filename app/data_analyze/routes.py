import asyncio
import os
import uuid
from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from templates import templates
import pandas as pd
from data_analyze.model_usage import process_with_model

router = APIRouter(prefix="")

@router.get("/inference", summary='return template')
def data_analyze(request: Request):
    return templates.TemplateResponse("data_analyze.html", {'request': request})


RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загрузка файла с обработкой ошибок"""
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["csv", "xlsx"]:
        return JSONResponse(
            {"error": "Only CSV and Excel files allowed"}, 
            status_code=400
        )

    # Чтение файла с контекстным менеджером
    with file.file as f:
        if ext == "csv":
            df = pd.read_csv(f)
        else:
            df = pd.read_excel(f)

    if "text" not in df.columns:
        return JSONResponse(
            {"error": "File must contain 'text' column"},
            status_code=400
        )

    # Обработка модели
    results = await process_with_model(df)

    # Сохранение результатов
    file_id = f"{uuid.uuid4()}.xlsx"
    file_path = os.path.join(RESULTS_DIR, file_id)
    results.to_excel(file_path, index=False)

    return {
        "data": results.to_dict(orient="records"),
        "download_url": f"/download/{file_id}"
    }


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Скачивание XLS-файла."""
    file_path = os.path.join(RESULTS_DIR, file_id)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename="results.xlsx")
    return {"error": "Файл не найден"}

