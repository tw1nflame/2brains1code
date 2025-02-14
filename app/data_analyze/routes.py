
import os
import uuid
from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from templates import templates
import pandas as pd


router = APIRouter(prefix="")

@router.get("/inference", summary='return template')
def data_analyze(request: Request):
    return templates.TemplateResponse("data_analyze.html", {'request': request})


@router.get("/markup", summary='return template')
def data_analyze(request: Request):
    return templates.TemplateResponse("markup.html", {'request': request})

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def process_with_model(df: pd.DataFrame) -> pd.DataFrame:
    """Эмуляция обработки файла моделью: добавляем 'label' и 'confidence'."""
    df["label"] = ["positive" if i % 2 == 0 else "negative" for i in range(len(df))]
    df["confidence"] = [round(0.5 + 0.5 * (i % 2), 2) for i in range(len(df))]
    return df


# @roiter.post("")


@router.post("/upload/")
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
    results = process_with_model(df)

    file_id = str(uuid.uuid4()) + ".xlsx"
    file_path = os.path.join(RESULTS_DIR, file_id)
    results.to_excel(file_path, index=False)

    # Возвращаем JSON + ссылку на скачивание
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

