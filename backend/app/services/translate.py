"""Segment translation via the OpenAI API."""

from __future__ import annotations

import json

from app.core import config
from app.services.languages import BY_CODE


def translate_segments(segments: list[dict], target_language: str) -> list[dict]:
    """Translate segment texts, preserving timestamps. Raises RuntimeError on failure."""
    if target_language not in BY_CODE:
        raise ValueError(f"Unsupported language: {target_language}")
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set; translation requires it")
    if not segments:
        return []

    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    language_name = BY_CODE[target_language]["name"]
    payload = [{"id": i, "text": s["text"]} for i, s in enumerate(segments)]

    response = client.chat.completions.create(
        model=config.TRANSLATION_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You translate video subtitles into {language_name}. "
                    "Return a JSON array of objects with keys 'id' and 'text'. "
                    "Translate naturally for spoken dubbing; keep each line roughly the "
                    "same length as the original. Do not add or remove entries."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    raw = response.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("translations", data.get("items", []))
        translated = {int(i["id"]): str(i["text"]) for i in items}
    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(f"Translation response was not valid JSON: {exc}") from exc

    out = []
    for i, segment in enumerate(segments):
        text = translated.get(i)
        if not text:
            raise RuntimeError(f"Translation missing segment {i}")
        out.append({"start": segment["start"], "end": segment["end"], "text": text})
    return out
