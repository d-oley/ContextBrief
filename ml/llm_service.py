import json
import re
import requests
from typing import Dict, List, Optional
from config import LOCAL_LLM_URL, LOCAL_MODEL, SERPER_API_KEY

_search_context_cache = {}



def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def _parse_json_payload(text: str) -> Optional[Dict]:
    cleaned = _clean_json(text)
    if not cleaned:
        return None

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


def _strip_inline_markdown(text: str) -> str:
    value = str(text or "")
    value = value.replace("\u00a0", " ")
    value = value.replace("**", "")
    value = value.replace("__", "")
    value = value.replace("*", "")
    value = value.replace("_", "")
    value = value.replace("`", "")

    value = value.replace("[", "").replace("]", "")
    value = value.replace("(", "").replace(")", "")
    value = value.replace(">", "")
    value = value.replace("|", " ")
    value = value.replace("  ", " ")

    return value.strip()


def _sanitize_markdown_response(text: str) -> str:
    lines = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue

        heading_match = re.match(r"^(#{1,6})\s*(.+)$", line)
        if heading_match:
            heading_level = heading_match.group(1)
            heading_text = _strip_inline_markdown(heading_match.group(2))
            if heading_text.lower() in {"краткая выжимка", "резюме"}:
                continue
            lines.append(f"{heading_level} {heading_text}" if heading_text else heading_level)
            continue

        list_match = re.match(r"^([-*•])\s+(.+)$", line)
        if list_match:
            item_text = _strip_inline_markdown(list_match.group(2))
            lines.append(f"- {item_text}" if item_text else "-")
            continue

        line = line.lstrip("> ").strip()
        lines.append(_strip_inline_markdown(line))

    sanitized = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", sanitized).strip()


def _sanitize_field(value: str) -> str:
    return _strip_inline_markdown(value).replace("  ", " ").strip()


def _sanitize_field_list(values) -> List[str]:
    return [_sanitize_field(item) for item in values if _sanitize_field(item)]


def call_llm(messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
    """
    Call the LLM API with the provided messages
    
    Args:
        messages: Список словарей сообщений с 'role' и 'content'
        temperature: Температура сэмплирования (0.0 до 1.0)
    
    Returns:
        Текст ответа LLM или None при ошибке
    """
    try:
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": LOCAL_MODEL,
            "messages": messages,
            "temperature": temperature,
        }

        response = requests.post(
            url=LOCAL_LLM_URL,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"Local LLM API error: {response.status_code} - {response.text}")
            return None
        
        response_dict = response.json()
        content = response_dict.get("choices", [{}])[0].get("message", {}).get("content")
        return content
    
    except requests.exceptions.Timeout:
        print("Local LLM request timed out.")
        return None
    except Exception as e:
        print(f"Local LLM request exception: {e}")
        return None



def search_internet(query: str) -> Dict[str, List[str] | str]:
    """
    Поиск информации через Serper.dev (Google Search API)
    Бесплатно 2500 запросов/мес
    """
    if not SERPER_API_KEY:
        print("SERPER_API_KEY is not configured.")
        return {"context": "", "sources": []}

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "q": query,
                "gl": "ru",  # Россия
                "hl": "ru",  # Русский язык
                "num": 3      # Количество результатов
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Serper API error: {response.status_code}")
            return {"context": "", "sources": []}
        
        data = response.json()
        
        # Собираем информацию из разных источников
        snippets = []
        source_urls = []
        
        # Knowledge Graph (если есть)
        if data.get("knowledgeGraph"):
            kg = data["knowledgeGraph"]
            title = kg.get("title", "")
            desc = kg.get("description", "")
            if title or desc:
                snippets.append(f"{title}: {desc}")
            kg_link = kg.get("website") or kg.get("link")
            if kg_link:
                source_urls.append(str(kg_link).strip())
        
        # обычные результаты
        for result in data.get("organic", [])[:3]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            date = result.get("date", "")
            date_str = f" ({date})" if date else ""
            snippets.append(f"{title}{date_str}: {snippet}")
            link = result.get("link")
            if link:
                source_urls.append(str(link).strip())
        
        # избранный ответ
        if data.get("answerBox"):
            ab = data["answerBox"]
            if ab.get("snippet"):
                snippets.insert(0, f"{ab.get('title', '')}: {ab['snippet']}")
            ab_link = ab.get("link")
            if ab_link:
                source_urls.insert(0, str(ab_link).strip())
        
        return {
            "context": "\n".join(snippets) if snippets else "",
            "sources": source_urls,
        }
        
    except Exception as e:
        print(f"Search error: {e}")
        return {"context": "", "sources": []}



def get_info(user_request: str) -> Dict:


    extraction_prompt = f"""You are a research assistant. Generate search queries to gather information relevant to the user's request.

Request: {user_request}

Generate 1 to 5 specific, varied search queries. Cover different angles: definitions, data and statistics, recent events, expert opinions, comparisons, and practical use cases.

All final answer text must be in Russian.

Return JSON: {{"queries": ["query1", "query2", "..."]}}"""

    extraction_response = call_llm(
        [{"role": "user", "content": extraction_prompt}],
        temperature=0.2
    )


    internet_context = ""
    source_urls = []
    try:
        if extraction_response:
            extraction_payload = _parse_json_payload(extraction_response) or {}
            queries = extraction_payload.get("queries", [])
            for query in queries[:5]:
                result = search_internet(query)
                if result.get("context"):
                    internet_context += f"\n--- Query: {query} ---\n{result['context']}\n"
                for link in result.get("sources", []):
                    if link and link not in source_urls:
                        source_urls.append(link)
    except Exception:
        fallback = search_internet(user_request[:300])
        if fallback.get("context"):
            internet_context = f"\n--- Query: {user_request[:100]} ---\n{fallback['context']}\n"
        for link in fallback.get("sources", []):
            if link and link not in source_urls:
                source_urls.append(link)

    _search_context_cache[user_request] = internet_context
    synthesis_prompt = f"""You are an expert research assistant. Synthesize the search results into a clear, well-structured answer.

User Request: {user_request}

Web Search Results:
{internet_context or "No search data available"}

Instructions:
- Provide a thorough answer based on the search results.
- Include relevant facts, figures, dates, names, and context.
- Note conflicting or uncertain information.
- Structure the response clearly and keep it concise.
- Add 3 to 7 short key points.
- Suggest 1 to 3 practical recommendations for the business team.
- All prose in the final answer must be in Russian.
- If search results are insufficient, state what was found and what is missing.

Return JSON:
{{
  "summary": "short synthesized answer",
  "key_points": ["point 1", "point 2"],
  "recommendations": ["recommendation 1"],
  "sources": ["source 1", "source 2"],
  "confidence": "high|medium|low"
}}"""

    response = call_llm(
        [{"role": "user", "content": synthesis_prompt}],
        temperature=0.3
    )

    if not response:
        return {
            "summary": "Не удалось собрать информацию: пустой ответ от модели.",
            "keyPoints": [],
            "recommendations": [],
            "sources": [],
            "confidence": "low",
        }

    try:
        result = _parse_json_payload(response)
        if result is None:
            raise ValueError("LLM returned non-JSON synthesis payload")
        summary = result.get("summary", "").strip()
        key_points = result.get("key_points", []) or result.get("keyPoints", [])
        recommendations = result.get("recommendations", [])
        confidence = result.get("confidence", "unknown")

        return {
            "summary": _sanitize_field(summary) or "Информация не найдена.",
            "keyPoints": _sanitize_field_list(key_points),
            "recommendations": _sanitize_field_list(recommendations),
            "sources": _sanitize_field_list(source_urls),
            "confidence": confidence or "unknown",
        }

    except Exception:
        fallback_text = response.strip() if response else "Не удалось обработать результаты поиска."
        bullets = [
            line.lstrip("-• ").strip()
            for line in fallback_text.splitlines()
            if line.lstrip().startswith(("-", "•"))
        ]
        return {
            "summary": _sanitize_field(fallback_text),
            "keyPoints": _sanitize_field_list(bullets),
            "recommendations": [],
            "sources": _sanitize_field_list(source_urls),
            "confidence": "unknown",
        }


def compose_final_answer(original_request: str, info_result: Dict) -> str:
    """Formats the final answer in Russian markdown."""
    search_context = _search_context_cache.get(original_request, "")
    info_text = json.dumps(info_result, ensure_ascii=False, indent=2)

    prompt = (
        "You are a senior research analyst.\n"
        f"Original request: {original_request}\n"
        f"Structured research data: {info_text}\n"
        f"Search context: {search_context or 'None'}\n\n"
        "Write a polished full answer in Russian using markdown.\n"
        "The answer must be in Russian.\n"
        "Do not repeat the short summary from the previous step.\n"
        "Do not include a separate 'Краткая выжимка' or 'Резюме' section.\n"
        "Start directly with the deeper analysis and conclusions.\n"
        "Use only simple markdown that we render safely: section headings and plain bullet lists.\n"
        "Do not use bold, italics, tables, code blocks, blockquotes, links, or any other markdown elements.\n"
        "Use these sections when relevant:\n"
        "## Основные выводы\n"
        "## Подробный анализ\n"
        "## Ключевые тезисы\n"
        "## Рекомендации\n"
        "## Источники\n\n"
        "Keep the answer concise, informative, and decision-friendly.\n"
        "Do not mention that this is an intermediate analysis."
    )
    final_eval = call_llm([{"role": "user", "content": prompt}], temperature=0.2)

    final_text = final_eval.strip() if final_eval else "Не удалось сформировать итоговый ответ."
    return _sanitize_markdown_response(final_text)





def analyze_topic(user_request: str) -> Dict:
    """Runs web search, synthesis, and completeness checks for an analytics topic."""

    results = {
        "status": "analyzed",
        "request": user_request,
        "response": "",
        "summary": "",
        "keyPoints": [],
        "recommendations": [],
        "sources": [],
        "confidence": "",
        "message" : "",
    }
    
    try:
        initial = get_info(user_request)
        final = compose_final_answer(user_request, initial)
        results["response"] = final
        results["summary"] = _sanitize_field(initial.get("summary", ""))
        results["keyPoints"] = _sanitize_field_list(initial.get("keyPoints", []))
        results["recommendations"] = _sanitize_field_list(initial.get("recommendations", []))
        results["sources"] = _sanitize_field_list(initial.get("sources", []))
        results["confidence"] = initial.get("confidence", "")
        results["message"] = "Анализ завершен"
        results["meta"] = {
            "text_length": len(user_request),
            "search_context_present": bool(_search_context_cache.get(user_request)),
        }
    except Exception as e:
        print(f"Analysis error: {e}")
        results["status"] = "error"
        results["message"] = "Произошла ошибка при анализе. Попробуйте ещё раз."
    
    return results
