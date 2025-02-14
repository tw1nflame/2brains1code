import numpy as np
import onnxruntime
import pandas as pd
from transformers import AutoTokenizer
from threading import local
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Конфигурация модели
label_mapping = {0: "negative", 1: "neutral", 2: "positive"}
model_path = 'data_analyze/finetuned_rubert_tiny'
onnx_model_path = "data_analyze/finetuned_rubert_tiny/model.onnx"

# Пул потоков для CPU-bound операций
MODEL_THREAD_POOL = ThreadPoolExecutor(max_workers=4)

# Потокобезопасное хранение объектов
thread_local = local()

def get_session():
    """Инициализация ONNX Runtime сессии для каждого потока"""
    if not hasattr(thread_local, "session"):
        thread_local.session = onnxruntime.InferenceSession(
            onnx_model_path,
            providers=["CPUExecutionProvider"]
        )
    return thread_local.session

def get_tokenizer():
    """Инициализация токенизатора для каждого потока"""
    if not hasattr(thread_local, "tokenizer"):
        thread_local.tokenizer = AutoTokenizer.from_pretrained(model_path)
    return thread_local.tokenizer

def softmax(x):
    """Вычисление softmax для массива"""
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / e_x.sum(axis=1, keepdims=True)

def predict_sentiment_batch(texts: list, batch_size=16):
    """Пакетное предсказание"""
    session = get_session()
    tokenizer = get_tokenizer()
    
    labels, confidences = [], []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        # Токенизация
        inputs = tokenizer(
            batch_texts,
            return_tensors="np",
            padding="max_length",
            truncation=True,
            max_length=512
        )

        # Подготовка входных данных
        input_ids = inputs["input_ids"].astype(np.int64)
        attention_mask = inputs["attention_mask"].astype(np.int64)

        # Выполнение предсказания
        outputs = session.run(["logits"], {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        })
        
        # Обработка результатов
        logits = outputs[0]
        probs = softmax(logits)
        batch_predicted_classes = np.argmax(probs, axis=1)
        batch_confidences = np.max(probs, axis=1)

        labels.extend([label_mapping[pred] for pred in batch_predicted_classes])
        confidences.extend(batch_confidences.tolist())

    return labels, confidences

async def process_with_model(df: pd.DataFrame):
    """Асинхронная обработка DataFrame"""
    texts = df["text"].tolist()
    
    loop = asyncio.get_event_loop()
    labels, confidences = await loop.run_in_executor(
        MODEL_THREAD_POOL,
        lambda: predict_sentiment_batch(texts, 16)
    )
    
    df["label"] = labels
    df["confidence"] = confidences
    return df