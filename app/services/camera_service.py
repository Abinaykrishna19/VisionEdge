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

    def start(self):

        previous_time = time.perf_counter()

        while True:

            success, frame = self.camera.read()

            if not success:
                print("Video Finished")
                break

            # Run YOLO detection
            results = self.model(frame)

            # Draw detections
            annotated_frame = results[0].plot()

            # FPS
            current_time = time.perf_counter()
            fps = 1 / (current_time - previous_time)
            previous_time = current_time

            cv2.putText(
                annotated_frame,
                f"FPS: {fps:.2f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("VisionEdge - YOLO Detection", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.camera.release()
        cv2.destroyAllWindows()