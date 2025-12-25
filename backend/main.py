import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .src.api.routes import auth, chat, upload


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http_logger = logging.getLogger("ragworks.http")


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    level = logging.INFO

    try:
        response = await call_next(request)
        status = response.status_code
        level = logging.INFO

    except Exception:
        level = logging.ERROR
        http_logger.exception(
            f"Unhandled exception in {request.method} {request.url.path}"
        )
        raise

    finally:
        duration = (time.perf_counter() - start) * 1000
        http_logger.log(
            level,
            f"Request: {request.method} {request.url.path} | "
            f"Status: {status} | Time taken: {duration:.2f} ms"
        )

    return response


# API Routes
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(upload.router)
