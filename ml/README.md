# ContextBrief ML Service

Python-сервис для автоматизированной аналитики по теме, введённой пользователем.

## Что делает сервис

- получает тему запроса;
- проверяет запрос модерационной моделью из `artifacts`;
- генерирует поисковые формулировки;
- ищет открытые источники через Serper.dev;
- синтезирует краткую аналитическую выжимку;
- возвращает summary, тезисы, рекомендации, источники и confidence.

## Endpoints

- `GET /health` — проверка доступности сервиса.
- `POST /evaluate` — запуск анализа темы.

## Запуск

```powershell
pip install -r requirements.txt
python app.py
```

По умолчанию сервис доступен на `http://localhost:5000`.

## Переменные окружения

- `SERPER_API_KEY` — ключ Serper.dev для поиска.
- `LOCAL_LLM_URL` — URL локальной LLM, по умолчанию `http://localhost:11434/v1/chat/completions`.
- `LOCAL_MODEL` — имя модели для локальной LLM, по умолчанию `qwen2.5:7b`.
- `FLASK_HOST` — host Flask-приложения.
- `FLASK_PORT` — port Flask-приложения.
- `FLASK_DEBUG` — включает debug-режим при значении `true`.

## Формат запроса

```json
{
  "text": "Применение CLTV в иностранных банках"
}
```

## Формат ответа

```json
{
  "status": "accepted",
  "message": "Анализ завершен",
  "response": "Полный текст результата",
  "analysis": {
    "topic": "Применение CLTV в иностранных банках",
    "summary": "Краткая выжимка",
    "keyPoints": ["Тезис 1", "Тезис 2"],
    "recommendations": ["Рекомендация 1"],
    "sources": ["Источник 1"],
    "confidence": "high"
  },
  "llm_meta": {
    "text_length": 38
  }
}
```
