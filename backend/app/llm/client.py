from __future__ import annotations
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

try:
    import google.generativeai as legacy_genai
    HAS_LEGACY_GENAI = True
except ImportError:
    HAS_LEGACY_GENAI = False

from app.config import get_settings

settings = get_settings()


def get_api_key() -> str:
    return settings.gemini_api_key or settings.anthropic_api_key or ""


def complete(system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> str:
    api_key = get_api_key()

    # If no API key set or placeholder key, use RAG context fallback safely
    if not api_key or api_key in ("test-key-not-used-in-this-test", "your_gemini_api_key_here", "your_anthropic_api_key_here"):
        context_str = ""
        if "RETRIEVED CONTEXT:\n" in system_prompt:
            context_str = system_prompt.split("RETRIEVED CONTEXT:\n")[1].strip()
        if context_str and context_str != "(no relevant sources found)":
            return f"Relevant Legal Information (RAG Retrieved Context):\n\n{context_str}\n\n[Note: Configure GEMINI_API_KEY in backend/.env for AI-synthesized responses.]"
        return "I am Nyāya Sahāyak, your AI Legal Information Assistant. Please set a valid GEMINI_API_KEY in backend/.env to generate AI responses."

    tokens = max_tokens or settings.llm_max_tokens
    model_candidates = [settings.llm_model, "gemini-flash-latest", "gemini-1.5-flash", "gemini-2.5-flash"]
    # De-duplicate while preserving order
    models_to_try = list(dict.fromkeys([m for m in model_candidates if m]))

    # 1. Try official google-genai SDK first
    if HAS_GENAI_SDK:
        client = genai.Client(api_key=api_key)
        for m_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=tokens,
                    ),
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue

    # 2. Try legacy google-generativeai SDK if available
    if HAS_LEGACY_GENAI:
        try:
            legacy_genai.configure(api_key=api_key)
            for m_name in models_to_try:
                try:
                    model = legacy_genai.GenerativeModel(
                        model_name=m_name,
                        system_instruction=system_prompt
                    )
                    res = model.generate_content(user_prompt)
                    if res and res.text:
                        return res.text.strip()
                except Exception:
                    continue
        except Exception:
            pass

    # 3. Fallback response with retrieved RAG context if LLM call fails
    context_str = ""
    if "RETRIEVED CONTEXT:\n" in system_prompt:
        context_str = system_prompt.split("RETRIEVED CONTEXT:\n")[1].strip()
    if context_str and context_str != "(no relevant sources found)":
        return f"Relevant Legal Information (RAG Retrieved Context):\n\n{context_str}"
    return "Unable to generate AI response. Please verify your GEMINI_API_KEY in backend/.env."
