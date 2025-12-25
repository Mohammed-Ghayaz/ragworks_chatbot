import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http_logger = logging.getLogger("ragworks.http")

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.perf_counter()

    try:
        response = await call_next(request)
        level = logging.INFO
        status = response.status_code

    except Exception:
        status=500
        level = logging.ERROR
        duration = (time.perf_counter() - start) * 1000
        http_logger.exception(f"Unhandled exception in {request.method} {request.url.path}")
        raise

    finally:
        duration = (time.perf_counter() - start) * 1000
        http_logger.log(level, f"Request: {request.method} {request.url.path} | Status: {status} | Time taken: {duration} ms")

    return response
