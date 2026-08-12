import cv2
import time
import threading
from ultralytics import YOLO


class CameraService:

    def __init__(self, video_path: str):

        self.video_path = video_path

        # -----------------------------
        # YOLO
        # -----------------------------
        self.model = YOLO("yolov8n.pt")

        # -----------------------------
        # STATE
        # -----------------------------
        self.running = False
        self.stop_requested = False

        self.processing_thread = None

        # -----------------------------
        # VIDEO
        # -----------------------------
        self.camera = None

        # -----------------------------
        # LIVE DATA
        # -----------------------------
        self.fps = 0.0
        self.objects_detected = 0

        self.latest_frame = None

        self.frame_lock = threading.Lock()

        # -----------------------------
        # PERFORMANCE
        # -----------------------------
        self.inference_width = 640

        # Process every 2nd frame
        self.frame_skip = 2

    # =====================================================
    # START
    # =====================================================

    def start(self):

        # Already running
        if self.running:
            return

        # Open video fresh every time
        self.camera = cv2.VideoCapture(self.video_path)

        if not self.camera.isOpened():
            raise RuntimeError(
                f"Unable to open video: {self.video_path}"
            )

        self.stop_requested = False
        self.running = True

        self.fps = 0.0
        self.objects_detected = 0

        with self.frame_lock:
            self.latest_frame = None

        self.processing_thread = threading.Thread(
            target=self._process_video,
            daemon=True
        )

        self.processing_thread.start()

    # =====================================================
    # PROCESS VIDEO
    # =====================================================

    def _process_video(self):

        frame_counter = 0

        fps_start = time.perf_counter()
        processed_frames = 0

        try:

            while not self.stop_requested:

                # -----------------------------
                # READ FRAME
                # -----------------------------

                success, frame = self.camera.read()

                if not success:

                    # Restart video
                    self.camera.set(
                        cv2.CAP_PROP_POS_FRAMES,
                        0
                    )

                    continue

                frame_counter += 1

                # -----------------------------
                # FRAME SKIP
                # -----------------------------

                if frame_counter % self.frame_skip != 0:
                    continue

                # -----------------------------
                # RESIZE
                # -----------------------------

                height, width = frame.shape[:2]

                if width > self.inference_width:

                    scale = self.inference_width / width

                    new_width = self.inference_width
                    new_height = int(height * scale)

                    detection_frame = cv2.resize(
                        frame,
                        (new_width, new_height),
                        interpolation=cv2.INTER_AREA
                    )

                else:

                    detection_frame = frame

                # -----------------------------
                # YOLO
                # -----------------------------

                results = self.model.predict(
                    detection_frame,
                    imgsz=640,
                    conf=0.35,
                    verbose=False
                )

                result = results[0]

                # -----------------------------
                # OBJECT COUNT
                # -----------------------------

                self.objects_detected = (
                    len(result.boxes)
                    if result.boxes is not None
                    else 0
                )

                # -----------------------------
                # DRAW
                # -----------------------------

                annotated_frame = result.plot()

                # -----------------------------
                # FPS
                # -----------------------------

                processed_frames += 1

                now = time.perf_counter()

                elapsed = now - fps_start

                if elapsed >= 1.0:

                    self.fps = (
                        processed_frames / elapsed
                    )

                    processed_frames = 0
                    fps_start = now

                # -----------------------------
                # DISPLAY
                # -----------------------------

                cv2.putText(
                    annotated_frame,
                    f"FPS: {self.fps:.1f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

                cv2.putText(
                    annotated_frame,
                    f"Objects: {self.objects_detected}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

                # -----------------------------
                # SAVE LATEST FRAME
                # -----------------------------

                with self.frame_lock:

                    self.latest_frame = (
                        annotated_frame.copy()
                    )

        except Exception as error:

            print(
                f"Camera processing error: {error}"
            )

        finally:

            self.running = False

            if self.camera is not None:

                self.camera.release()

                self.camera = None

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.stop_requested = True

        if (
            self.processing_thread
            and self.processing_thread.is_alive()
        ):

            self.processing_thread.join(
                timeout=3
            )

        self.running = False

        self.fps = 0.0
        self.objects_detected = 0

        with self.frame_lock:

            self.latest_frame = None

        self.processing_thread = None

    # =====================================================
    # GET FRAME
    # =====================================================

    def get_latest_frame(self):

        with self.frame_lock:

            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

    # =====================================================
    # STATUS
    # =====================================================

    def get_status(self):

        return {
            "status": (
                "running"
                if self.running
                else "stopped"
            ),
            "fps": round(
                self.fps,
                2
            ),
            "objects_detected": (
                self.objects_detected
            )
        }