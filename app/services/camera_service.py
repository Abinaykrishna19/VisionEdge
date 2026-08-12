import cv2
import time
import threading
from ultralytics import YOLO


class CameraService:

    def __init__(self, video_path: str):
        self.video_path = video_path

        # ---------------------------------------------------------
        # YOLO MODEL
        # ---------------------------------------------------------

        self.model = YOLO("yolov8n.pt")

        # ---------------------------------------------------------
        # VIDEO
        # ---------------------------------------------------------

        self.camera = cv2.VideoCapture(self.video_path)

        if not self.camera.isOpened():
            raise Exception(
                f"Unable to open video: {self.video_path}"
            )

        # ---------------------------------------------------------
        # PROCESSING STATE
        # ---------------------------------------------------------

        self.running = False
        self.stop_requested = False

        # ---------------------------------------------------------
        # LIVE STATISTICS
        # ---------------------------------------------------------

        self.fps = 0.0
        self.objects_detected = 0

        # ---------------------------------------------------------
        # LATEST PROCESSED FRAME
        # ---------------------------------------------------------

        self.latest_frame = None

        # ---------------------------------------------------------
        # THREAD SAFETY
        # ---------------------------------------------------------

        self.lock = threading.Lock()

    # =============================================================
    # START ANALYSIS
    # =============================================================

    def start(self):
        """
        Process the selected video using YOLO.
        """

        self.running = True
        self.stop_requested = False

        previous_time = time.perf_counter()

        try:

            while not self.stop_requested:

                success, frame = self.camera.read()

                # -------------------------------------------------
                # VIDEO REACHED END
                # -------------------------------------------------

                if not success:

                    # Restart video from beginning
                    self.camera.set(
                        cv2.CAP_PROP_POS_FRAMES,
                        0
                    )

                    continue

                # -------------------------------------------------
                # YOLO DETECTION
                # -------------------------------------------------

                results = self.model(
                    frame,
                    verbose=False
                )

                result = results[0]

                # -------------------------------------------------
                # OBJECT COUNT
                # -------------------------------------------------

                object_count = 0

                if result.boxes is not None:
                    object_count = len(
                        result.boxes
                    )

                # -------------------------------------------------
                # ANNOTATED FRAME
                # -------------------------------------------------

                annotated_frame = result.plot()

                # -------------------------------------------------
                # FPS
                # -------------------------------------------------

                current_time = time.perf_counter()

                elapsed_time = (
                    current_time - previous_time
                )

                if elapsed_time > 0:

                    current_fps = (
                        1.0 / elapsed_time
                    )

                else:

                    current_fps = 0.0

                previous_time = current_time

                # -------------------------------------------------
                # SMOOTH FPS
                # -------------------------------------------------

                with self.lock:

                    if self.fps == 0:

                        self.fps = current_fps

                    else:

                        self.fps = (
                            self.fps * 0.8
                            + current_fps * 0.2
                        )

                    self.objects_detected = (
                        object_count
                    )

                # -------------------------------------------------
                # DRAW FPS
                # -------------------------------------------------

                cv2.putText(
                    annotated_frame,
                    f"FPS: {self.fps:.2f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

                # -------------------------------------------------
                # DRAW OBJECT COUNT
                # -------------------------------------------------

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

                # -------------------------------------------------
                # STORE LATEST FRAME
                # -------------------------------------------------

                with self.lock:

                    self.latest_frame = (
                        annotated_frame.copy()
                    )

                # -------------------------------------------------
                # SMALL DELAY
                # -------------------------------------------------

                time.sleep(0.001)

        except Exception as error:

            print(
                f"Camera processing error: {error}"
            )

        finally:

            self.running = False

            self.camera.release()

            print(
                "Camera processing stopped."
            )

    # =============================================================
    # STOP ANALYSIS
    # =============================================================

    def stop(self):

        self.stop_requested = True

    # =============================================================
    # GET LATEST FRAME
    # =============================================================

    def get_latest_frame(self):

        with self.lock:

            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

    # =============================================================
    # GET LIVE STATISTICS
    # =============================================================

    def get_status(self):

        with self.lock:

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