from contextlib import asynccontextmanager
import time
import uuid
import signal
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException

from training.utils import training


class TrainingManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    def start_training(self, training_data, batch_size, n_epochs, test_size, metrics):
        if any(task.get('status') == 'running' for task in self.tasks.values()):
            return HTTPException(status_code=400, detail="The model is already training")
        
        task_id = str(uuid.uuid4())
        future = self.executor.submit(self._train_model, task_id, training_data, batch_size, n_epochs, test_size, metrics)
        
        self.tasks[task_id] = {
            "start_time": datetime.now(),
            "status": "pending",
            "progress": 0.0,
            "eta": None,
            "future": future
        }
        return task_id
    
    def _train_model(self, task_id, df, batch_size, n_epochs, test_size, metrics):
        try:
            print(f"Task {task_id} started!")
            task = self.tasks[task_id]
            task["status"] = "running"

            training(task_id, self, df, batch_size=batch_size, n_epochs=n_epochs, test_size=test_size, metrics=metrics)

            task["status"] = "completed"
            task["progress"] = 1.0
            task["eta"] = 0

            print(f"Task {task_id} finished successfully!")
        except Exception as e:
            print(f"Error in task {task_id}: {e}")
            task["status"] = "failed"


    def update_progress(self, task_id, progress, eta, metrics=None):
        """ Обновляет прогресс обучения """
        if task_id in self.tasks:
            self.tasks[task_id]["progress"] = progress
            self.tasks[task_id]["eta"] = eta
            if metrics:
                self.tasks[task_id]["metrics"] = metrics

    def get_task_info(self, task_id):
        return self.tasks.get(task_id)

    def cancel_training(self, task_id):
        task = self.tasks.get(task_id)
        if task and task["status"] == "running":
            task["status"] = "cancelled"
            return True
        return False

    def shutdown(self):
        """Останавливает все запущенные задачи и завершает executor"""
        print("Shutting down training manager...")

        # Отменяем все активные задачи
        for task_id, task in self.tasks.items():
            if task["status"] == "running":
                task["status"] = "cancelled"
                print(f"Task {task_id} marked as cancelled")

        # Завершаем executor, ждем завершения задач
        self.executor.shutdown(wait=True)
        print("Training manager shut down complete.")


training_manager = TrainingManager()

@asynccontextmanager
async def lifespan(app):
    yield  
    training_manager.shutdown()