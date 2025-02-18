from typing import List
import uuid
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from templates import templates
import pandas as pd
from training.tasks import training_manager


router = APIRouter(prefix="")


@router.get('/training')
def training_page(request: Request):
    return templates.TemplateResponse("training.html", {'request': request})


@router.post("/start-training/")
async def start_training(
    request: Request,
    file: UploadFile = File(...),
    batch_size: int = Form(...),
    n_epochs: int = Form(...),
    test_size: float = Form(...),
    metrics: List[str] | None = Form(None)
):

    form_data = await request.form()
    print("Полученные данные формы:", form_data)

    if metrics is None:
        metrics=[]

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["csv", "xlsx"]:
        return JSONResponse(
            {"error": "Only CSV and Excel files allowed"}, 
            status_code=400
        )

    with file.file as f:
        if ext == "csv":
            df = pd.read_csv(f)
        else:
            df = pd.read_excel(f)

    res = training_manager.start_training(df, batch_size, n_epochs, test_size, metrics)

    if isinstance(res, HTTPException):
        raise res
    return {"task_id": res}

@router.get("/training-status/{task_id}")
async def get_training_status(task_id: str):
    task_info = training_manager.get_task_info(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "status": task_info["status"],
        "progress": task_info['progress'],
        "eta": task_info["eta"],
        "start_time": task_info["start_time"].isoformat(),
        "metrics": task_info.get('metrics', '')
    }

@router.delete("/cancel-training/{task_id}")
async def cancel_training(task_id: str):
    if not training_manager.cancel_training(task_id):
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    return {"status": "cancellation_requested"}