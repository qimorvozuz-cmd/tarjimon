import asyncio
import io
import logging

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Tesseract 100+ tilni qo'llab-quvvatlaydi, lekin Railway/serverda til paketlari
# alohida o'rnatilishi kerak (README.md ga qarang). Eng ko'p ishlatiladigan tillar:
OCR_LANG_MAP = {
    "uz": "uzb",
    "ru": "rus",
    "en": "eng",
    "tr": "tur",
    "ar": "ara",
    "zh-CN": "chi_sim",
    "de": "deu",
    "fr": "fra",
    "es": "spa",
    "ja": "jpn",
    "ko": "kor",
}


async def extract_text_from_image(image_bytes: bytes, lang_hint: str = "eng") -> str:
    """
    Rasmdan matnni ajratib oladi (OCR). lang_hint - matn qaysi tilda deb taxmin
    qilinayotgani (Tesseract til kodi formatida, masalan 'eng+rus').
    """
    def _run():
        image = Image.open(io.BytesIO(image_bytes))
        # Ranglilikni normallashtirish OCR sifatini oshiradi
        if image.mode != "RGB":
            image = image.convert("RGB")
        try:
            text = pytesseract.image_to_string(image, lang=lang_hint)
        except pytesseract.TesseractError:
            # Til paketi topilmasa inglizchaga qaytamiz
            text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()

    try:
        return await asyncio.to_thread(_run)
    except Exception as e:
        logger.exception("OCR xatosi: %s", e)
        return ""


def guess_tesseract_lang(*app_lang_codes: str) -> str:
    """Bir nechta til kodini Tesseract formatiga o'giradi va birlashtiradi (masalan 'uzb+rus+eng')."""
    codes = []
    for code in app_lang_codes:
        mapped = OCR_LANG_MAP.get(code)
        if mapped and mapped not in codes:
            codes.append(mapped)
    if "eng" not in codes:
        codes.append("eng")
    return "+".join(codes)
