"""Supported dubbing languages and TTS voices.

Edge TTS voices are the free default; OpenAI TTS voices apply when
TTS_PROVIDER=openai.
"""

LANGUAGES: list[dict] = [
    {"code": "my", "name": "Myanmar (Burmese)", "voices": ["my-MM-NilarNeural", "my-MM-ThihaNeural"]},
    {"code": "th", "name": "Thai", "voices": ["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"]},
    {"code": "id", "name": "Indonesian", "voices": ["id-ID-GadisNeural", "id-ID-ArdiNeural"]},
    {"code": "vi", "name": "Vietnamese", "voices": ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"]},
    {"code": "en", "name": "English", "voices": ["en-US-AriaNeural", "en-US-GuyNeural"]},
    {"code": "es", "name": "Spanish", "voices": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"]},
    {"code": "fr", "name": "French", "voices": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"]},
    {"code": "de", "name": "German", "voices": ["de-DE-KatjaNeural", "de-DE-ConradNeural"]},
    {"code": "hi", "name": "Hindi", "voices": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"]},
    {"code": "ja", "name": "Japanese", "voices": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"]},
    {"code": "ko", "name": "Korean", "voices": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"]},
    {"code": "zh", "name": "Chinese (Mandarin)", "voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]},
    {"code": "ar", "name": "Arabic", "voices": ["ar-SA-ZariyahNeural", "ar-SA-HamedNeural"]},
    {"code": "pt", "name": "Portuguese", "voices": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"]},
    {"code": "ru", "name": "Russian", "voices": ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"]},
    {"code": "ms", "name": "Malay", "voices": ["ms-MY-YasminNeural", "ms-MY-OsmanNeural"]},
    {"code": "fil", "name": "Filipino", "voices": ["fil-PH-BlessicaNeural", "fil-PH-AngeloNeural"]},
    {"code": "km", "name": "Khmer", "voices": ["km-KH-SreymomNeural", "km-KH-PisethNeural"]},
    {"code": "lo", "name": "Lao", "voices": ["lo-LA-KeomanyNeural", "lo-LA-ChanthavongNeural"]},
    {"code": "bn", "name": "Bengali", "voices": ["bn-IN-TanishaaNeural", "bn-IN-BashkarNeural"]},
    {"code": "ta", "name": "Tamil", "voices": ["ta-IN-PallaviNeural", "ta-IN-ValluvarNeural"]},
]

BY_CODE = {entry["code"]: entry for entry in LANGUAGES}

OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


def resolve_voice(target_language: str, requested: str | None) -> str:
    """Return a valid voice id for the language, falling back to the default."""
    entry = BY_CODE.get(target_language)
    if entry is None:
        raise ValueError(f"Unsupported language: {target_language}")
    if requested and requested in entry["voices"]:
        return requested
    return entry["voices"][0]
