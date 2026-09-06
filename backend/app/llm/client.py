from __future__ import annotations
import os

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from app.config import get_settings

settings = get_settings()


def get_api_key() -> str:
    return settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")


def complete(system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> str:
    if not HAS_GENAI:
        raise RuntimeError("google-generativeai is not installed.")

    api_key = get_api_key()
    if not api_key or api_key in (
        "your-gemini-api-key-here",
        "your_gemini_api_key_here",
        "test-key-not-used-in-this-test",
    ):
        raise RuntimeError("GEMINI_API_KEY setting is unset.")

    genai.configure(api_key=api_key)
    
    model_name = settings.llm_model or "gemini-2.5-flash"
    tokens = max_tokens or settings.llm_max_tokens

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=tokens,
            )
        )
        res = model.generate_content(user_prompt)
        if res and res.text:
            return res.text.strip()
    except Exception as ex:
        print(f"[Gemini Client] Model {model_name} failed: {ex}")
        raise ex
