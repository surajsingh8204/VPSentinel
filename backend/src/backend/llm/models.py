from langchain.chat_models import init_chat_model

from backend.config import settings


def get_groq_primary():
    """Return the primary Groq model."""

    return init_chat_model(
        model=f"groq:{settings.groq_model_primary}",
        api_key=settings.groq_api_key,
        temperature=0.1,
    )


def get_groq_fast():
    """Return the faster Groq model."""

    return init_chat_model(
        model=f"groq:{settings.groq_model_fast}",
        api_key=settings.groq_api_key,
    )


def get_gemini_primary():
    """Return the primary Gemini fallback model."""

    return init_chat_model(
        model=f"google_genai:{settings.gemini_model_primary}",
        api_key=settings.gemini_api_key,
        temperature=0.1,
    )


def get_gemini_fallback():
    """Return the secondary Gemini fallback model."""

    return init_chat_model(
        model=f"google_genai:{settings.gemini_model_fallback}",
        api_key=settings.gemini_api_key,
    )


def get_gemini_lite():
    """Return the lightweight Gemini model."""

    return init_chat_model(
        model=f"google_genai:{settings.gemini_model_lite}",
        api_key=settings.gemini_api_key,
    )


def get_agent_model():
    """
    Return the primary DevOps agent model with a Gemini fallback.

    Primary:
        Groq GPT-OSS 120B

    Fallback:
        Gemini 3.8 Flash
    """

    primary = get_groq_primary()
    fallback = get_gemini_primary()

    return primary.with_fallbacks(
        [fallback],
        exceptions_to_handle=(Exception,),
    )