from threading import Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.camera_service import CameraService


# ==========================================
# VisionEdge FastAPI Application
# ==========================================

app = FastAPI(
    title="VisionEdge API",
    description="Hardware Accelerated Video Analytics Platform",
    version="1.0.0"
)


# ==========================================
# CORS Configuration
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Home Endpoint
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to VisionEdge!"
    }


# ==========================================
# Health Endpoint
# ==========================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ==========================================
# Camera Basic Status
# ==========================================

@app.get("/camera/status")
def camera_status():
    return {
        "status": "ready",
        "video": "highway.mp4",
        "model": "yolov8n.pt"
    }


# ==========================================
# Login
# ==========================================

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest):

    if data.username == "admin" and data.password == "admin123":
        return {
            "success": True,
            "message": "Login successful"
        }

    return {
        "success": False,
        "message": "Invalid username or password"
    }


# ==========================================
# Camera Service Variables
# ==========================================

camera_service = None
camera_thread = None


# ==========================================
# Start Camera
# ==========================================

@app.post("/camera/start")
def start_camera():

    global camera_service
    global camera_thread

    # Check if camera is already running
    if camera_thread is not None and camera_thread.is_alive():

        return {
            "success": False,
            "message": "Camera is already running"
        }

    try:

        # Create camera service
        camera_service = CameraService()

        # Create background thread
        camera_thread = Thread(
            target=camera_service.start,
            daemon=True
        )

        # Start camera thread
        camera_thread.start()

        return {
            "success": True,
            "message": "Camera started"
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }


# ==========================================
# Stop Camera
# ==========================================

@app.post("/camera/stop")
def stop_camera():

    global camera_service

    # Camera service does not exist
    if camera_service is None:

        return {
            "success": False,
            "message": "Camera is not running"
        }

    # Camera already stopped
    if not camera_service.running:

        return {
            "success": False,
            "message": "Camera is already stopped"
        }

    # Request camera to stop
    camera_service.stop()

    return {
        "success": True,
        "message": "Camera stopping"
    }


# ==========================================
# Live Camera Status
# ==========================================

@app.get("/camera/live-status")
def camera_live_status():

    # Camera has never been started
    if camera_service is None:

        return {
            "status": "stopped",
            "fps": 0,
            "objects_detected": 0
        }

    return {
        "status": (
            "running"
            if camera_service.running
            else "stopped"
        ),
        "fps": round(camera_service.fps, 2),
        "objects_detected": camera_service.objects_detected
    }