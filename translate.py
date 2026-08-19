import asyncio
import logging

from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, LANG_NAMES_EN

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (
    "You are a professional translator. Translate the user's text into the requested "
    "target language. Rules:\n"
    "1. Output ONLY the translation itself — no explanations, no notes, no quotation marks, "
    "no 'Translation:' prefix.\n"
    "2. Preserve the original meaning, tone, and formatting (line breaks, punctuation, emojis).\n"
    "3. If the text contains names, numbers, or technical terms, keep them accurate.\n"
    "4. If the source text is already in the target language, return it unchanged.\n"
    "5. Never add commentary, apologies, or meta-text of any kind."
)


def _lang_name(code: str) -> str:
    return LANG_NAMES_EN.get(code, code)


async def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """
    Matnni Claude API orqali target_lang tiliga tarjima qiladi.
    source_lang berilsa promptga qo'shiladi (aniqlikni oshiradi), 'auto' bo'lsa Claude o'zi aniqlaydi.
    """
    if not text or not text.strip():
        return ""

    target_name = _lang_name(target_lang)

    if source_lang and source_lang != "auto":
        source_name = _lang_name(source_lang)
        user_prompt = (
            f"Translate the following text from {source_name} to {target_name}.\n\n"
            f"Text:\n{text}"
        )
    else:
        user_prompt = (
            f"Detect the language of the following text and translate it to {target_name}.\n\n"
            f"Text:\n{text}"
        )

    def _run():
        response = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        parts = [block.text for block in response.content if block.type == "text"]
        return "".join(parts).strip()

    try:
        result = await asyncio.to_thread(_run)
        return result or "⚠️ Tarjima natijasi bo'sh qaytdi."
    except RateLimitError:
        logger.warning("Anthropic rate limit ga tegildi.")
        return "⚠️ Hozir so'rovlar juda ko'p. Birozdan so'ng qayta urinib ko'ring."
    except APIConnectionError:
        logger.exception("Anthropic API bilan bog'lanishda xatolik.")
        return "⚠️ Internet yoki API bilan bog'lanishda muammo yuz berdi."
    except APIError as e:
        logger.exception("Anthropic API xatosi: %s", e)
        return "⚠️ Tarjima xizmatida xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring."
    except Exception as e:
        logger.exception("Kutilmagan tarjima xatosi: %s", e)
        return "⚠️ Tarjima qilishda xatolik yuz berdi."


async def detect_and_translate(text: str, target_lang: str) -> tuple[str, str]:
    """
    Manba tilni Claude'ga avtomatik aniqlatib, target_lang ga tarjima qiladi.
    Qaytaradi: (tarjima_matni, aniqlangan_til_nomi_ingilizcha)
    """
    target_name = _lang_name(target_lang)

    user_prompt = (
        f"Translate the following text to {target_name}. "
        f"First line of your response must be exactly: LANG: <detected source language in English>\n"
        f"From the second line onward, write ONLY the translation, nothing else.\n\n"
        f"Text:\n{text}"
    )

    def _run():
        response = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        parts = [block.text for block in response.content if block.type == "text"]
        return "".join(parts).strip()

    try:
        raw = await asyncio.to_thread(_run)
        if raw.startswith("LANG:"):
            first_line, _, rest = raw.partition("\n")
            detected = first_line.replace("LANG:", "").strip()
            return rest.strip(), detected
        return raw, "auto"
    except Exception as e:
        logger.exception("Auto-tarjima xatosi: %s", e)
        return "⚠️ Tarjima qilishda xatolik yuz berdi.", "auto"
