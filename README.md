# 🧠 AI Competitor Analyzer for Apartment Renovation

AI-powered tool for analyzing competitor ads in the apartment renovation market.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-web%20framework-green)
![OpenAI](https://img.shields.io/badge/OpenAI-AI-orange)
![Selenium](https://img.shields.io/badge/Selenium-browser%20automation-brightgreen)
![License](https://img.shields.io/badge/license-educational-lightgrey)

The service analyzes:

- advertisement text
- images from listings
- competitor website pages

and generates a structured marketing analysis.

## Возможности

### Анализ текста объявления

Сервис определяет:
- основную услугу
- дополнительные услуги
- ценовую модель
- преимущества
- маркетинговые триггеры
- слабые места объявления
- стиль текста
- целевую аудиторию
- итоговое резюме
- рекомендации по улучшению

### Анализ изображений

Модель анализирует фотографии объявления и определяет:
- что изображено
- стадию ремонта
- виды работ
- качество визуальной подачи
- сигналы доверия
- слабые стороны фотографий

## Для чего нужен проект

Проект помогает:
- анализировать конкурентов
- понимать маркетинговые стратегии объявлений
- выявлять слабые места
- улучшать собственные объявления

Особенно полезно для:
- ремонтных компаний
- маркетологов
- специалистов по продвижению услуг

## Архитектура проекта

```text
avito_analyzer/
├── config.py
├── main.py
├── requirements.txt
├── services/
│   ├── openai_analyzer.py
│   ├── selenium_parser.py
│   └── text_cleaner.py
├── static/
│   └── style.css
└── templates/
    ├── index.html
    └── result.html
```

## Технологии

- Python
- FastAPI
- OpenAI API
- Selenium
- HTML / CSS
- Jinja2 templates

## Как запустить проект

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Tata-Tiana/avito-analyzer.git
cd avito-analyzer
```

### 2. Создать виртуальное окружение

```bash
python3 -m venv .venv
```

Активировать:

Mac / Linux
```bash
source .venv/bin/activate
```

Windows
```bash
.venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env`

Скопировать шаблон:

```bash
cp .env.example .env
```

Добавить ключ:

```env
OPENAI_API_KEY=your_openai_api_key
```

При необходимости можно задать модель:

```env
OPENAI_MODEL=gpt-4o-mini
```

### 5. Запустить сервер

```bash
uvicorn main:app --reload
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:8000
```

## Как пользоваться

Можно передать данные тремя способами:

1. URL сайта конкурента
2. Текст объявления вручную
3. Фотографии или скриншоты объявления

После этого сервис:
- собирает данные
- анализирует текст
- анализирует изображения
- формирует отчет

## Особенности

- Открытые сайты можно анализировать по URL.
- Для Avito и похожих площадок надежнее использовать ручную вставку текста и загрузку скриншотов.
- Из-за антибот-защиты некоторые площадки могут отдавать мало текста или блокировать автоматический парсинг.

## Возможные улучшения

- анализ нескольких объявлений одновременно
- сравнение конкурентов между собой
- генерация улучшенного объявления
- рекомендации по SEO
- экспорт отчета

## Скриншоты

В проекте есть папка [`screenshots/`](/Users/tatanamedzidova/Desktop/Avito_analyzer/screenshots) с примерами интерфейса:
- `screenshots/main_page.png`
- `screenshots/analysis.png`

Главная страница:

![Главная страница](screenshots/main_page.png)

Результат анализа:

![Результат анализа](screenshots/analysis.png)

## Автор

Учебный проект по анализу конкурентов в сфере ремонта квартир.
