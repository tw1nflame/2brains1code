
import os
import uuid
from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from templates import templates
import pandas as pd

router = APIRouter(prefix="")

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@router.post("/kek/")
async def upload_file(file: UploadFile = File(...)):
    """Загрузка файла, обработка моделью, генерация XLS и JSON ответа."""
    # Определяем расширение
    ext = file.filename.split(".")[-1]
    if ext not in ["csv", "xls", "xlsx"]:
        return {"error": "Файл должен быть CSV или Excel"}

    # Читаем файл
    if ext == "csv":
        df = pd.read_csv(file.file)
    else:
        df = pd.read_excel(file.file)

    # Обрабатываем модель
    results = df

    file_id = str(uuid.uuid4()) + ".xlsx"
    file_path = os.path.join(RESULTS_DIR, file_id)
    results.to_excel(file_path, index=False)

    # Возвращаем JSON + ссылку на скачивание
    return {
        "data": results.to_dict(orient="records"),
        "download_url": f"/download/{file_id}"
    }