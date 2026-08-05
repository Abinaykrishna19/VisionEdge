from fastapi import FastAPI

app = FastAPI(
    title="VisionEdge API",
    description="Hardware Accelerated Video Analytics Platform",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to VisionEdge!"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }