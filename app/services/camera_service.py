import cv2
import time
from ultralytics import YOLO


class CameraService:

    def __init__(self):
        # Load YOLO model
        self.model = YOLO("yolov8n.pt")

        # Open video
        self.camera = cv2.VideoCapture("videos/highway.mp4")

        if not self.camera.isOpened():
            raise Exception("Unable to open video.")

        # Camera state
        self.running = False
        self.stop_requested = False

        # Live statistics
        self.fps = 0.0
        self.objects_detected = 0

    def start(self):
        """Start video processing and YOLO detection."""

        self.running = True
        self.stop_requested = False

        previous_time = time.perf_counter()

        try:
            while not self.stop_requested:

                # Read video frame
                success, frame = self.camera.read()

                if not success:
                    print("Video Finished")
                    break

                # Run YOLO detection
                results = self.model(frame)

                # Count detected objects
                self.objects_detected = len(results[0].boxes)

                # Draw detections
                annotated_frame = results[0].plot()

                # Calculate FPS
                current_time = time.perf_counter()
                elapsed_time = current_time - previous_time

                if elapsed_time > 0:
                    self.fps = 1 / elapsed_time

                previous_time = current_time

                # Display FPS
                cv2.putText(
                    annotated_frame,
                    f"FPS: {self.fps:.2f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                # Display object count
                cv2.putText(
                    annotated_frame,
                    f"Objects: {self.objects_detected}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                # Display video
                cv2.imshow(
                    "VisionEdge - YOLO Detection",
                    annotated_frame
                )

                # Press Q to stop
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            # Clean up camera
            self.running = False
            self.stop_requested = False

            self.camera.release()
            cv2.destroyAllWindows()

            self.fps = 0.0
            self.objects_detected = 0

    def stop(self):
        """Request the camera processing loop to stop."""

        self.stop_requested = True