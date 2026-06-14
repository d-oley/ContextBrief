import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from censor_service import is_request_allowed
from llm_service import analyze_topic


app = Flask(__name__)

CORS(
    app,
    origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ],
    supports_credentials=False,
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
    automatic_options=True,
)


def error_resp(code, msg, details=None):
    return {"status": "error", "code": code, "message": msg, "details": details or {}}


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/evaluate")
def evaluate():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify(error_resp("INVALID_INPUT", "Требуется поле text")), 400

    allowed, probability, threshold = is_request_allowed(text.strip())
    if not allowed:
        return jsonify(error_resp(
            "REQUEST_BLOCKED",
            "Запрос отклонён модерационной проверкой. Попробуйте сформулировать тему иначе.",
            {
                "censor_score": round(probability, 4),
                "censor_threshold": round(threshold, 4),
            },
        )), 400

    result = analyze_topic(text.strip())
    response_text = (result.get("response") or "").strip()

    if result.get("status") == "error" or not response_text:
        return jsonify(error_resp(
            "ANALYSIS_FAILED",
            result.get("message", "Не удалось выполнить анализ"),
            {"llm_meta": result.get("meta", {})}
        )), 502

    return jsonify({
        "status": "accepted",
        "message": result.get("message", "Анализ завершен"),
        "response": response_text,
        "analysis": {
            "topic": text.strip(),
            "summary": result.get("summary", ""),
            "keyPoints": result.get("keyPoints", []),
            "recommendations": result.get("recommendations", []),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", ""),
        },
        "llm_meta": result.get("meta", {}),
    })


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
