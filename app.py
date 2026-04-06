import json
import random
from pathlib import Path
from collections import deque
from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import FastAPI, Query, Request, Path as FPath
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError


WORDS_FILE = Path("words.json")
MAX_WORD_ID = 1000000


class WordItem(BaseModel):
    id: int
    word: str
    definition: str
    pronunciation: str


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class WordService:
    words: List[WordItem] = []
    words_by_id: Dict[int, WordItem] = {}
    random_queue: deque = deque()

    @classmethod
    def load_words(cls):
        if not WORDS_FILE.exists():
            raise APIError(500, "words.json file not found")

        try:
            with open(WORDS_FILE, "r", encoding="utf-8") as file:
                raw_data = json.load(file)

            if not isinstance(raw_data, list):
                raise APIError(500, "words.json must contain array data")

            validated_words = []
            id_index = {}

            for item in raw_data:
                word = WordItem(**item)

                if word.id in id_index:
                    raise APIError(
                        500,
                        f"duplicate id found: {word.id}"
                    )

                validated_words.append(word)
                id_index[word.id] = word

            cls.words = validated_words
            cls.words_by_id = id_index
            cls.refresh_random_queue()

        except json.JSONDecodeError:
            raise APIError(500, "invalid json format")

        except ValidationError:
            raise APIError(500, "invalid word data structure")

    @classmethod
    def clear_cache(cls):
        cls.words.clear()
        cls.words_by_id.clear()
        cls.random_queue.clear()

    @classmethod
    def refresh_random_queue(cls):
        shuffled = cls.words[:]
        random.shuffle(shuffled)
        cls.random_queue = deque(shuffled)

    @classmethod
    def get_unique_random_word(cls):
        if not cls.random_queue:
            cls.refresh_random_queue()

        return cls.random_queue.popleft()

    @classmethod
    def get_word_by_id(cls, word_id: int):
        word = cls.words_by_id.get(word_id)

        if not word:
            raise APIError(404, "word id not found")

        return word

    @staticmethod
    def format_tree(word: WordItem) -> str:
        return (
            "📘 Word Details\n"
            "│\n"
            f"├── ID             : {word.id}\n"
            f"├── Word           : {word.word}\n"
            f"├── Definition     : {word.definition}\n"
            f"└── Pronunciation  : {word.pronunciation}"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    WordService.load_words()
    try:
        yield
    finally:
        WordService.clear_cache()


app = FastAPI(
    title="Random Words API",
    version="1.0.0",
    description="10k random words API",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000"
    )

    # Legacy support (optional)
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Modern XSS protection
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' https: data:; "
        "connect-src 'self' https://cdn.jsdelivr.net; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    return response


@app.get("/")
async def home():
    return {
        "status": "success",
        "api": "Random Words API",
        "version": app.version,
        "total_words": len(WordService.words),
        "routes": {
            "home": "/",
            "random_word": "/random",
            "random_word_text": "/random?text=true",
            "word_by_id": "/word/{word_id}",
            "word_by_id_text": "/word/{word_id}?text=true",
            "full_data": "/data",
            "docs": "/docs"
        },
        "usage_examples": {
            "get_random": "/random",
            "get_random_text": "/random?text=true",
            "get_word_by_id": "/word/1",
            "get_word_by_id_text": "/word/1?text=true",
            "get_all_data": "/data"
        }
    }


@app.get("/data", include_in_schema=False)
async def get_all_words():
    return {
        "status": "success",
        "count": len(WordService.words),
        "data": WordService.words
    }


@app.get("/random")
async def random_word(text: bool = Query(False)):
    word = WordService.get_unique_random_word()

    if text:
        return PlainTextResponse(
            WordService.format_tree(word)
        )

    return {
        "status": "success",
        "data": word
    }


@app.get("/word/{word_id}")
async def get_word(
    word_id: int = FPath(
        ...,
        gt=0,
        le=MAX_WORD_ID,
        description="Word ID must be positive"
    ),
    text: bool = Query(False)
):
    word = WordService.get_word_by_id(word_id)

    if text:
        return PlainTextResponse(
            WordService.format_tree(word)
        )

    return {
        "status": "success",
        "data": word
    }


@app.get("/docs", include_in_schema=False)
async def custom_swagger_docs():
    try:
        html = get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title="Random Words API",
            swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
        )

        content = html.body.decode("utf-8")

        if "</head>" not in content:
            raise ValueError("Invalid Swagger HTML")

        custom_style = """
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1">
        <style>
            html, body {
                margin: 0;
                padding: 0;
                width: 100%;
                overflow-x: hidden;
                -webkit-text-size-adjust: 100%;
            }

            .swagger-ui {
                width: 100%;
                overflow-x: hidden;
            }

            .swagger-ui .wrapper {
                width: 100%;
                max-width: 100% !important;
                padding: 10px !important;
                box-sizing: border-box;
            }

            .swagger-ui .opblock-summary {
                flex-wrap: wrap !important;
                gap: 6px;
            }

            .swagger-ui .opblock-summary-path {
                white-space: normal !important;
                word-break: break-word !important;
                overflow-wrap: anywhere !important;
                font-size: 14px !important;
                line-height: 1.4;
            }

            .swagger-ui pre,
            .swagger-ui code,
            .swagger-ui .microlight,
            .swagger-ui .highlight-code {
                white-space: pre-wrap !important;
                word-break: break-word !important;
                overflow-wrap: anywhere !important;
                overflow-x: auto !important;
                max-width: 100% !important;
                max-height: 220px !important;
                overflow-y: auto !important;
                box-sizing: border-box;
                font-size: 12px !important;
                line-height: 1.5 !important;
                border-radius: 8px;
            }

            .swagger-ui table {
                display: block;
                width: 100%;
                overflow-x: auto;
            }

            .swagger-ui textarea,
            .swagger-ui input,
            .swagger-ui select {
                width: 100% !important;
                box-sizing: border-box;
                font-size: 16px !important;
            }

            .swagger-ui .btn {
                min-height: 42px !important;
                white-space: normal !important;
            }

            @media (max-width: 768px) {
                .swagger-ui .wrapper {
                    padding: 8px !important;
                }

                .swagger-ui pre,
                .swagger-ui code {
                    max-height: 180px !important;
                    font-size: 11px !important;
                }
            }
        </style>
        """

        content = content.replace(
            "</head>",
            custom_style + "</head>"
        )

        response = HTMLResponse(content=content)

        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"

        return response

    except Exception:
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Docs Error</title>
                </head>
                <body style="font-family:sans-serif;padding:20px;">
                    <h2>Unable to load Swagger docs</h2>
                </body>
            </html>
            """,
            status_code=500
        )


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "message": exc.message
        }
    )


@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": 500,
            "message": "internal server error"
        }
    )