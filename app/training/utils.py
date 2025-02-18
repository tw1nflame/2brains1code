from datetime import datetime
from sklearn.metrics import f1_score, accuracy_score, recall_score
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from transformers import DataCollatorWithPadding, TrainerCallback


def load_dataset(df, test_size, tokenizer):
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Перемешивание
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        df['text'], df['sentiment'], test_size=test_size, random_state=42
    )
    return SentimentDataset(train_texts.tolist(), train_labels.tolist(), tokenizer), SentimentDataset(test_texts.tolist(), test_labels.tolist(), tokenizer)

class ProgressCallback(TrainerCallback):
    """ Коллбэк для обновления прогресса обучения в TrainingManager """
    
    def __init__(self, task_id, training_manager, update_steps=10):
        self.task_id = task_id
        self.training_manager = training_manager
        self.update_steps = update_steps  # Как часто обновлять прогресс
    
    def on_step_end(self, args, state, control, **kwargs):
        """ Вызывается после каждого шага """
        if state.global_step % self.update_steps == 0:  # Обновляем каждые N шагов
            progress = state.global_step / state.max_steps
            elapsed = (datetime.now() - self.training_manager.tasks[self.task_id]["start_time"]).total_seconds()
            eta = (elapsed / state.global_step) * (state.max_steps - state.global_step) if state.global_step > 0 else None
            metrics = {}
            if not state.log_history:
                pass
            elif 'loss' in state.log_history[-1]:
                metrics = state.log_history[-2]
                metrics['loss'] = state.log_history[-1]['loss']
    
            else:
                metrics = state.log_history[-1]
                metrics['loss'] = state.log_history[-2]['loss']
            metrics = state.log_history[-1] if state.log_history else {}
            self.training_manager.update_progress(self.task_id, progress, eta, metrics)

            print(f"Task {self.task_id} progress: {progress:.2%}, ETA: {eta:.1f} sec")


class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        encoding = self.tokenizer(self.texts[idx], padding='max_length', truncation=True, max_length=512, return_tensors="pt")
        return {"input_ids": encoding["input_ids"].squeeze(0),
                "attention_mask": encoding["attention_mask"].squeeze(0),
                "label": torch.tensor(self.labels[idx], dtype=torch.long)}


def compute_metrics(pred, selected_metrics):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    results = {}

    if "accuracy" in selected_metrics:
        results["accuracy"] = accuracy_score(labels, preds)
    if "f1" in selected_metrics:
        results["f1"] = f1_score(labels, preds, average='weighted')
    if "recall" in selected_metrics:
        results["recall"] = recall_score(labels, preds, average='weighted')

    return results



def training(task_id, training_manager, df, batch_size=16, n_epochs=1, test_size=0.2, metrics=["accuracy", "f1", "recall"]):
    model_name = "data_analyze/finetuned_rubert_tiny"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

    train_dataset, test_dataset = load_dataset(df, test_size, tokenizer)

    training_args = TrainingArguments(
        output_dir=f"data_analyze/training_results/{task_id}",
        eval_strategy="steps",
        eval_steps=10,
        save_strategy="steps",
        save_steps=10,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=n_epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
        logging_steps=10,
        disable_tqdm=True
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=lambda pred: compute_metrics(pred, metrics),
        callbacks=[ProgressCallback(task_id, training_manager)]
    )

    trainer.train()

    # Сохраняем PyTorch-модель
    save_path = "app/data_analyze/finetuned_rubert_tiny"
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)

    # Экспорт в ONNX
    onnx_model_path = f"{save_path}/model.onnx"
    dummy_text = "Пример текста для теста"
    inputs = tokenizer(dummy_text, return_tensors="pt", padding="max_length", truncation=True, max_length=512)

    model.eval()  # Включаем eval-режим перед экспортом
    torch.onnx.export(
        model,
        (inputs["input_ids"], inputs["attention_mask"]), 
        onnx_model_path,
        input_names=["input_ids", "attention_mask"], 
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size"},
            "attention_mask": {0: "batch_size"},
            "logits": {0: "batch_size"}
        },
        opset_version=14
    )

    print(f"✅ Model training complete. ONNX model saved at {onnx_model_path}")
