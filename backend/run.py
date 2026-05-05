"""
Run the backend with 2 worker processes so status polls stay live
while the pipeline is downloading/processing video in another worker.
Usage: python3 run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        workers=4,
        log_level="info",
    )
