import os
import threading
import time

import cv2

from fastapi import (
    FastAPI,
    UploadFile,
    File,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.responses import (
    StreamingResponse,
)

from pydantic import BaseModel

from app.services.camera_service import (
    CameraService,
)


# ================================================================
# FASTAPI APPLICATION
# ================================================================

app = FastAPI(
    title="VisionEdge API",
    description=(
        "Hardware Accelerated "
        "Video Analytics Platform"
    ),
    version="1.0.0",
)


# ================================================================
# CORS
# ================================================================

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


# ================================================================
# VIDEO DIRECTORY
# ================================================================

VIDEO_DIR = "videos"

os.makedirs(
    VIDEO_DIR,
    exist_ok=True
)


# ================================================================
# GLOBAL CAMERA STATE
# ================================================================

camera_service = None
camera_thread = None

current_video_path = None


# ================================================================
# HOME
# ================================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to VisionEdge!"
    }


# ================================================================
# HEALTH
# ================================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ================================================================
# CAMERA STATUS
# ================================================================

@app.get("/camera/status")
def camera_status():

    return {
        "status": "ready",
        "video": (
            current_video_path
            if current_video_path
            else "No video selected"
        ),
        "model": "yolov8n.pt",
    }


# ================================================================
# LOGIN
# ================================================================

class LoginRequest(BaseModel):

    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest):

    if (
        data.username == "admin"
        and data.password == "admin123"
    ):

        return {
            "success": True,
            "message": "Login successful",
        }

    return {
        "success": False,
        "message": (
            "Invalid username or password"
        ),
    }


# ================================================================
# VIDEO UPLOAD
# ================================================================

@app.post("/video/upload")
async def upload_video(
    file: UploadFile = File(...)
):

    global current_video_path

    try:

        if not file.filename:

            return {
                "success": False,
                "message": (
                    "No video file selected."
                ),
            }

        # --------------------------------------------------------
        # File extension
        # --------------------------------------------------------

        filename = os.path.basename(
            file.filename
        )

        extension = (
            os.path.splitext(filename)[1]
            .lower()
        )

        allowed_extensions = [
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".webm",
        ]

        if extension not in allowed_extensions:

            return {
                "success": False,
                "message": (
                    "Unsupported video format."
                ),
            }

        # --------------------------------------------------------
        # Save path
        # --------------------------------------------------------

        file_path = os.path.join(
            VIDEO_DIR,
            filename
        )

        # --------------------------------------------------------
        # Save file
        # --------------------------------------------------------

        contents = await file.read()

        with open(
            file_path,
            "wb"
        ) as video_file:

            video_file.write(
                contents
            )

        # --------------------------------------------------------
        # Store current video
        # --------------------------------------------------------

        current_video_path = file_path

        print(
            f"Video uploaded: {file_path}"
        )

        return {
            "success": True,
            "message": (
                "Video uploaded successfully"
            ),
            "filename": filename,
            "path": file_path,
        }

    except Exception as error:

        print(
            f"Upload error: {error}"
        )

        return {
            "success": False,
            "message": str(error),
        }


# ================================================================
# START CAMERA / ANALYSIS
# ================================================================

@app.post("/camera/start")
def start_camera():

    global camera_service
    global camera_thread

    # ------------------------------------------------------------
    # Check video
    # ------------------------------------------------------------

    if not current_video_path:

        return {
            "success": False,
            "message": (
                "Please upload a video first."
            ),
        }

    # ------------------------------------------------------------
    # Check existing camera
    # ------------------------------------------------------------

    if (
        camera_thread is not None
        and camera_thread.is_alive()
    ):

        return {
            "success": False,
            "message": (
                "Camera is already running."
            ),
        }

    # ------------------------------------------------------------
    # Create camera service
    # ------------------------------------------------------------

    try:

        camera_service = CameraService(
            current_video_path
        )

    except Exception as error:

        print(
            f"Camera initialization error: "
            f"{error}"
        )

        return {
            "success": False,
            "message": str(error),
        }

    # ------------------------------------------------------------
    # Start processing thread
    # ------------------------------------------------------------

    camera_thread = threading.Thread(
        target=camera_service.start,
        daemon=True,
    )

    camera_thread.start()

    # ------------------------------------------------------------
    # Give the processing thread a moment
    # ------------------------------------------------------------

    time.sleep(0.2)

    return {
        "success": True,
        "message": (
            "Camera analysis started."
        ),
        "video": current_video_path,
    }


# ================================================================
# STOP CAMERA
# ================================================================

@app.post("/camera/stop")
def stop_camera():

    global camera_service

    if camera_service is None:

        return {
            "success": False,
            "message": (
                "Camera is not running."
            ),
        }

    camera_service.stop()

    return {
        "success": True,
        "message": (
            "Camera stopping."
        ),
    }


# ================================================================
# LIVE CAMERA STATUS
# ================================================================

@app.get("/camera/live-status")
def camera_live_status():

    if camera_service is None:

        return {
            "status": "stopped",
            "fps": 0,
            "objects_detected": 0,
        }

    return camera_service.get_status()


# ================================================================
# VIDEO STREAM
# ================================================================

def generate_video_stream():

    while True:

        # --------------------------------------------------------
        # Camera service doesn't exist
        # --------------------------------------------------------

        if camera_service is None:

            time.sleep(0.1)
            continue

        # --------------------------------------------------------
        # Get latest processed frame
        # --------------------------------------------------------

        frame = (
            camera_service.get_latest_frame()
        )

        # --------------------------------------------------------
        # No frame available yet
        # --------------------------------------------------------

        if frame is None:

            time.sleep(0.03)
            continue

        # --------------------------------------------------------
        # Encode frame as JPEG
        # --------------------------------------------------------

        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [
                int(
                    cv2.IMWRITE_JPEG_QUALITY
                ),
                80,
            ],
        )

        if not success:

            continue

        frame_bytes = buffer.tobytes()

        # --------------------------------------------------------
        # MJPEG frame
        # --------------------------------------------------------

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: "
            + str(
                len(frame_bytes)
            ).encode()
            + b"\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

        # --------------------------------------------------------
        # Control stream rate
        # --------------------------------------------------------

        time.sleep(0.03)


# ================================================================
# VIDEO STREAM ENDPOINT
# ================================================================

@app.get("/video/stream")
def video_stream():

    return StreamingResponse(
        generate_video_stream(),
        media_type=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )