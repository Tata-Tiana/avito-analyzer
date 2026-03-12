import base64
import json
import re
from typing import Any, Dict, List

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIAnalyzer:
    def __init__(self) -> None:
        self.model = OPENAI_MODEL
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def analyze_text_ad(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {}
        if self.client is None:
            raise RuntimeError("Не задан OPENAI_API_KEY в .env.")

        system_prompt = (
            "Ты — сильный маркетинговый аналитик и эксперт по конкурентному анализу "
            "в нише ремонта квартир."
        )
        user_prompt = (
            "Твоя задача — анализировать текст объявления конкурента и разбирать его "
            "с точки зрения продаж, маркетинга, доверия, оффера и целевой аудитории.\n\n"
            "Ты работаешь в контексте рынка ремонта квартир и понимаешь, как обычно продаются:\n"
            "- ремонт квартир под ключ\n"
            "- косметический ремонт\n"
            "- капитальный ремонт\n"
            "- ремонт санузлов\n"
            "- электромонтажные работы\n"
            "- сантехнические работы\n"
            "- отделочные работы\n"
            "- отдельные услуги и бригады\n\n"
            "Нужно анализировать текст не как литературный текст, а как коммерческое объявление.\n\n"
            "Определи и верни строго JSON со следующей структурой:\n\n"
            "{\n"
            "  \"main_service\": \"\",\n"
            "  \"additional_services\": [],\n"
            "  \"pricing\": {\n"
            "    \"has_price\": true,\n"
            "    \"price_text\": \"\",\n"
            "    \"pricing_model\": \"\"\n"
            "  },\n"
            "  \"advantages\": [],\n"
            "  \"marketing_triggers\": [],\n"
            "  \"weaknesses\": [],\n"
            "  \"style\": \"\",\n"
            "  \"target_audience\": [],\n"
            "  \"summary\": \"\",\n"
            "  \"recommendations\": []\n"
            "}\n\n"
            "Что означает каждое поле:\n\n"
            "1. \"main_service\"\n"
            "Главная услуга, которую продвигает конкурент.\n"
            "Например:\n"
            "- ремонт квартир под ключ\n"
            "- косметический ремонт\n"
            "- капитальный ремонт\n"
            "- ремонт ванной\n"
            "- отделка новостроек\n\n"
            "2. \"additional_services\"\n"
            "Дополнительные услуги, которые упомянуты в тексте.\n"
            "Например:\n"
            "- демонтаж\n"
            "- сантехника\n"
            "- электрика\n"
            "- закупка материалов\n"
            "- вывоз мусора\n"
            "- дизайн-проект\n"
            "- бесплатный замер\n\n"
            "3. \"pricing\"\n"
            "Вложенный объект:\n"
            "- \"has_price\" — true, если цена или формат цены есть\n"
            "- \"price_text\" — дословно или кратко передай, как указана цена\n"
            "- \"pricing_model\" — объясни модель цены:\n"
            "  например:\n"
            "  - \"от N рублей\"\n"
            "  - \"цена за м²\"\n"
            "  - \"бесплатный замер\"\n"
            "  - \"цена не указана\"\n\n"
            "4. \"advantages\"\n"
            "Сильные стороны объявления.\n"
            "Например:\n"
            "- гарантия\n"
            "- опыт работы\n"
            "- договор\n"
            "- сроки\n"
            "- фото работ\n"
            "- бесплатный замер\n"
            "- работа без предоплаты\n"
            "- закупка материалов\n"
            "- собственная бригада\n\n"
            "5. \"marketing_triggers\"\n"
            "Какие маркетинговые триггеры используются:\n"
            "- срочность\n"
            "- выгода\n"
            "- доверие\n"
            "- экспертность\n"
            "- социальное доказательство\n"
            "- конкретика\n"
            "- безопасность\n"
            "- гарантия\n"
            "- удобство\n"
            "- простота\n"
            "- экономия времени\n"
            "- экономия денег\n\n"
            "6. \"weaknesses\"\n"
            "Что плохо в объявлении:\n"
            "- нет конкретики\n"
            "- нет цены\n"
            "- нет сроков\n"
            "- нет отличия от конкурентов\n"
            "- слишком шаблонный текст\n"
            "- нет доказательств\n"
            "- мало доверия\n"
            "- слабый оффер\n"
            "- перегруженность\n"
            "- непонятно, для кого услуга\n\n"
            "7. \"style\"\n"
            "Кратко опиши стиль подачи текста.\n"
            "Например:\n"
            "- сухой\n"
            "- шаблонный\n"
            "- убедительный\n"
            "- разговорный\n"
            "- экспертный\n"
            "- агрессивно-продающий\n"
            "- деловой\n"
            "- слабый по подаче\n\n"
            "8. \"target_audience\"\n"
            "Для кого, скорее всего, написано объявление.\n"
            "Например:\n"
            "- владельцы квартир в новостройках\n"
            "- эконом-сегмент\n"
            "- средний сегмент\n"
            "- люди, которым нужен ремонт под ключ\n"
            "- срочный ремонт\n"
            "- владельцы вторички\n"
            "- инвесторы под сдачу\n\n"
            "9. \"summary\"\n"
            "Краткий аналитический вывод:\n"
            "насколько объявление сильное, в чём его реальная сила, "
            "в чём слабость, насколько оно может быть убедительным.\n\n"
            "10. \"recommendations\"\n"
            "Практические рекомендации, как это объявление можно сделать сильнее.\n"
            "Рекомендации должны быть конкретными и полезными.\n\n"
            "Правила:\n"
            "- Пиши только на русском языке.\n"
            "- Не выдумывай то, чего нет в тексте.\n"
            "- Если информации нет, укажи это честно.\n"
            "- Не добавляй никаких пояснений вне JSON.\n"
            "- Не пиши markdown.\n"
            "- Верни только валидный JSON.\n\n"
            "Текст объявления:\n"
            + text
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content or ""
        parsed = self._parse_json_response(content)
        return self._normalize_text_result(parsed)

    def analyze_images(self, image_bytes_list: List[bytes]) -> Dict[str, Any]:
        if not image_bytes_list:
            return {}
        if self.client is None:
            raise RuntimeError("Не задан OPENAI_API_KEY в .env.")

        content = [
            {
                "type": "text",
                "text": (
                    "Проанализируй изображения объявления конкурента в нише ремонта квартир. "
                    "Верни только JSON со структурой: "
                    "{"
                    "\"detected_objects\": [], "
                    "\"repair_stage\": \"\", "
                    "\"work_types\": [], "
                    "\"visual_quality\": \"\", "
                    "\"trust_signals\": [], "
                    "\"image_weaknesses\": [], "
                    "\"image_summary\": \"\""
                    "}."
                ),
            }
        ]

        for image_bytes in image_bytes_list:
            data_url = self._to_data_url(image_bytes)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                }
            )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Ты визуальный аналитик объявлений по ремонту квартир."},
                {"role": "user", "content": content},
            ],
        )

        message_content = response.choices[0].message.content or ""
        if isinstance(message_content, list):
            message_text = "".join([item.get("text", "") for item in message_content if isinstance(item, dict)])
        else:
            message_text = message_content

        parsed = self._parse_json_response(message_text)
        return self._normalize_image_result(parsed)

    def _to_data_url(self, image_bytes: bytes) -> str:
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return "data:image/jpeg;base64," + encoded

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        candidates = [content, self._strip_code_fence(content), self._extract_json_object(content)]
        for candidate in candidates:
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        raise RuntimeError("OpenAI вернул ответ, который не удалось разобрать как JSON.")

    def _strip_code_fence(self, content: str) -> str:
        text = content.strip()
        if text.startswith("```") and text.endswith("```"):
            lines = text.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        return text

    def _extract_json_object(self, content: str) -> str:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return match.group(0).strip()
        return ""

    def _normalize_text_result(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        pricing = parsed.get("pricing", {})
        if not isinstance(pricing, dict):
            pricing = {}

        return {
            "main_service": self._as_string(parsed.get("main_service", "")),
            "additional_services": self._as_list(parsed.get("additional_services", [])),
            "pricing": {
                "has_price": bool(pricing.get("has_price", False)),
                "price_text": self._as_string(pricing.get("price_text", "")),
                "pricing_model": self._as_string(pricing.get("pricing_model", "")),
            },
            "advantages": self._as_list(parsed.get("advantages", [])),
            "marketing_triggers": self._as_list(parsed.get("marketing_triggers", [])),
            "weaknesses": self._as_list(parsed.get("weaknesses", [])),
            "style": self._as_string(parsed.get("style", "")),
            "target_audience": self._as_list(parsed.get("target_audience", [])),
            "summary": self._as_string(parsed.get("summary", "")),
            "recommendations": self._as_list(parsed.get("recommendations", [])),
        }

    def _normalize_image_result(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "detected_objects": self._as_list(parsed.get("detected_objects", [])),
            "repair_stage": self._as_string(parsed.get("repair_stage", "")),
            "work_types": self._as_list(parsed.get("work_types", [])),
            "visual_quality": self._as_string(parsed.get("visual_quality", "")),
            "trust_signals": self._as_list(parsed.get("trust_signals", [])),
            "image_weaknesses": self._as_list(parsed.get("image_weaknesses", [])),
            "image_summary": self._as_string(parsed.get("image_summary", "")),
        }

    def _as_string(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return ", ".join([str(item).strip() for item in value if str(item).strip()])
        return str(value).strip()

    def _as_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            prepared = value.strip()
            if not prepared:
                return []
            return [prepared]
        return [str(value).strip()]
