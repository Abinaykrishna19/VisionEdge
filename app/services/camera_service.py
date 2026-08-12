import cv2
import time
import threading
from ultralytics import YOLO


class CameraService:

    def __init__(self, video_path):

        self.video_path = video_path

        # --------------------------------------------------
        # YOLO MODEL
        # --------------------------------------------------

        self.model = YOLO("yolov8n.pt")

        # --------------------------------------------------
        # VIDEO
        # --------------------------------------------------

        self.camera = cv2.VideoCapture(self.video_path)

        if not self.camera.isOpened():
            raise Exception(
                f"Unable to open video: {self.video_path}"
            )

        # --------------------------------------------------
        # PROCESSING STATE
        # --------------------------------------------------

        self.running = False
        self.stop_requested = False

        # Background processing thread
        self.processing_thread = None

        # --------------------------------------------------
        # LIVE STATISTICS
        # --------------------------------------------------

        self.fps = 0.0
        self.objects_detected = 0

        # --------------------------------------------------
        # LATEST PROCESSED FRAME
        # --------------------------------------------------

        self.latest_frame = None

        # Lock prevents simultaneous access to frame
        self.frame_lock = threading.Lock()

        # --------------------------------------------------
        # PERFORMANCE SETTINGS
        # --------------------------------------------------

        # YOLO processes a smaller image.
        # This greatly improves CPU performance.
        self.inference_width = 640

        # Process every Nth frame.
        #
        # 1 = every frame
        # 2 = every second frame
        # 3 = every third frame
        #
        # We start with 2.
        self.frame_skip = 2

    # ======================================================
    # START
    # ======================================================

    def start(self):
        """
        Start video analysis in a background thread.
        """

        # Prevent starting multiple threads
        if self.running:
            return

        self.stop_requested = False
        self.running = True

        self.processing_thread = threading.Thread(
            target=self._process_video,
            daemon=True
        )

        self.processing_thread.start()

    # ======================================================
    # VIDEO PROCESSING
    # ======================================================

    def _process_video(self):

        frame_counter = 0

        # FPS measurement
        fps_start_time = time.perf_counter()
        processed_frames = 0

        try:

            while not self.stop_requested:

                # --------------------------------------------------
                # READ FRAME
                # --------------------------------------------------

                success, frame = self.camera.read()

                # Restart video when it reaches the end
                if not success:

                    self.camera.set(
                        cv2.CAP_PROP_POS_FRAMES,
                        0
                    )

                    continue

                frame_counter += 1

                # --------------------------------------------------
                # FRAME SKIPPING
                # --------------------------------------------------

                if frame_counter % self.frame_skip != 0:

                    continue

                # --------------------------------------------------
                # RESIZE FRAME
                # --------------------------------------------------

                height, width = frame.shape[:2]

                if width > self.inference_width:

                    scale = (
                        self.inference_width / width
                    )

                    new_width = self.inference_width

                    new_height = int(
                        height * scale
                    )

                    frame_for_detection = cv2.resize(
                        frame,
                        (
                            new_width,
                            new_height
                        )
                    )

                else:

                    frame_for_detection = frame

                # --------------------------------------------------
                # YOLO DETECTION
                # --------------------------------------------------

                results = self.model(
                    frame_for_detection,
                    verbose=False
                )

                # --------------------------------------------------
                # OBJECT COUNT
                # --------------------------------------------------

                self.objects_detected = len(
                    results[0].boxes
                )

                # --------------------------------------------------
                # DRAW DETECTIONS
                # --------------------------------------------------

                annotated_frame = results[0].plot()

                # --------------------------------------------------
                # FPS CALCULATION
                # --------------------------------------------------

                processed_frames += 1

                current_time = time.perf_counter()

                elapsed = (
                    current_time - fps_start_time
                )

                if elapsed >= 1.0:

                    self.fps = (
                        processed_frames / elapsed
                    )

                    processed_frames = 0

                    fps_start_time = current_time

                # --------------------------------------------------
                # DISPLAY FPS
                # --------------------------------------------------

                cv2.putText(
                    annotated_frame,
                    f"FPS: {self.fps:.1f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                # --------------------------------------------------
                # DISPLAY OBJECT COUNT
                # --------------------------------------------------

                cv2.putText(
                    annotated_frame,
                    f"Objects: {self.objects_detected}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                # --------------------------------------------------
                # STORE ONLY THE LATEST FRAME
                # --------------------------------------------------

                with self.frame_lock:

                    self.latest_frame = annotated_frame.copy()

        except Exception as error:

            print(
                f"Camera processing error: {error}"
            )

        finally:

            self.running = False

            self.fps = 0.0

            self.objects_detected = 0

    # ======================================================
    # STOP
    # ======================================================

    def stop(self):

        self.stop_requested = True

        if (
            self.processing_thread
            and self.processing_thread.is_alive()
        ):

            self.processing_thread.join(
                timeout=2
            )

        self.running = False

        self.fps = 0.0

        self.objects_detected = 0

        with self.frame_lock:

            self.latest_frame = None

        # Reset video to beginning
        self.camera.set(
            cv2.CAP_PROP_POS_FRAMES,
            0
        )

    # ======================================================
    # GET LATEST FRAME
    # ======================================================

    def get_latest_frame(self):

        with self.frame_lock:

            if self.latest_frame is None:

                return None

            return self.latest_frame.copy()

    # ======================================================
    # STATUS
    # ======================================================

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