from typing import List, Optional

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import STATIC_DIR, TEMPLATES_DIR
from services.openai_analyzer import OpenAIAnalyzer
from services.selenium_parser import SeleniumParser
from services.text_cleaner import clean_text


app = FastAPI(title="Avito Analyzer")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

selenium_parser = SeleniumParser()
openai_analyzer = OpenAIAnalyzer()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    url: Optional[str] = Form(None),
    raw_text: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
) -> HTMLResponse:
    source_url = (url or "").strip()
    manual_text = (raw_text or "").strip()
    uploaded_images = [image for image in (images or []) if image.filename]

    parsed_data = {"title": "", "price": "", "description": ""}
    final_text = ""
    text_analysis = {}
    image_analysis = {}
    warning_messages = []
    error_message = None

    try:
        if not source_url and not manual_text and not uploaded_images:
            raise ValueError("Укажите ссылку, вставьте текст или загрузите хотя бы одно изображение.")
    except Exception as exc:
        error_message = str(exc)

    text_parts = []

    if source_url:
        try:
            parsed_data = selenium_parser.extract_listing_data(source_url)
            page_text = _join_text_parts(
                [parsed_data.get("title", ""), parsed_data.get("price", ""), parsed_data.get("description", "")]
            )
            if page_text:
                text_parts.append(page_text)
            else:
                warning_messages.append("По ссылке удалось получить минимум данных.")
        except Exception:
            warning_messages.append("Не удалось извлечь данные по URL. Продолжаем анализ по остальным источникам.")

    if manual_text:
        text_parts.append(manual_text)

    final_text = clean_text("\n\n".join(text_parts))

    if final_text:
        try:
            text_analysis = openai_analyzer.analyze_text_ad(final_text)
        except Exception:
            warning_messages.append("Не удалось получить анализ текста от OpenAI.")

    if uploaded_images:
        image_bytes_list = []
        for image in uploaded_images:
            image_bytes = await image.read()
            if image_bytes:
                image_bytes_list.append(image_bytes)
        if image_bytes_list:
            try:
                image_analysis = openai_analyzer.analyze_images(image_bytes_list)
            except Exception:
                warning_messages.append("Не удалось получить анализ изображений от OpenAI.")

    if source_url and not parsed_data.get("description") and not manual_text:
        warning_messages.append(
            "Страница по ссылке дала мало текста. Для объявлений на маркетплейсах надежнее вставлять текст вручную."
        )
    if uploaded_images and not image_analysis:
        warning_messages.append("Изображения были загружены, но анализ по ним не удалось построить.")
    if not final_text and not image_analysis and not error_message:
        error_message = "Не удалось собрать достаточно данных для анализа."

    if text_analysis or image_analysis:
        error_message = None

    result = {
        "source_url": source_url,
        "parsed_title": parsed_data.get("title", ""),
        "parsed_price": parsed_data.get("price", ""),
        "final_text": final_text,
        "text_analysis": text_analysis,
        "image_analysis": image_analysis,
    }

    context = {
        "request": request,
        "result": result,
        "warning_messages": warning_messages,
        "error_message": error_message,
        "submitted_url": source_url,
        "submitted_raw_text": manual_text,
        "uploaded_files": [image.filename for image in uploaded_images],
    }
    return templates.TemplateResponse("result.html", context)


def _join_text_parts(parts: List[str]) -> str:
    prepared_parts = [part.strip() for part in parts if part and part.strip()]
    return "\n".join(prepared_parts)
