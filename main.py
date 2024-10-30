import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import router as api_router
from app.core.config import settings
import asyncio
from collections import deque
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Model processing times (in seconds)
MODEL_PROCESSING_TIMES = {
    "fast_model": 1,
    "medium_model": 3,
    "slow_model": 5,
}

# Request queue and settings
MAX_QUEUE_SIZE = 100
request_queue = deque()

@app.middleware("http")
async def queue_middleware(request: Request, call_next):
    if len(request_queue) >= MAX_QUEUE_SIZE:
        return JSONResponse(
            status_code=503,
            content={"message": "Server is overloaded. Please try again later."}
        )

    # Extract the model name from the request
    model_name = request.query_params.get("model", "medium_model")
    processing_time = MODEL_PROCESSING_TIMES.get(model_name, MODEL_PROCESSING_TIMES["medium_model"])

    queue_position = len(request_queue)
    estimated_wait_time = sum(item[1] for item in request_queue) + processing_time

    request_queue.append((time.time(), processing_time))

    if queue_position > 0:
        return JSONResponse(
            status_code=202,
            content={
                "message": "You are in the queue.",
                "queue_position": queue_position,
                "estimated_wait_time": f"{estimated_wait_time:.2f} seconds"
            }
        )

    try:
        start_time = time.time()
        response = await call_next(request)
        actual_process_time = time.time() - start_time

        response.headers["X-Process-Time"] = str(actual_process_time)
        return response
    finally:
        request_queue.popleft()

app.include_router(api_router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
