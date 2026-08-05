import cv2
import time


class CameraService:
    def __init__(self):
        # Open the video file
        self.camera = cv2.VideoCapture("videos/traffic.mp4")

        # To use webcam instead, uncomment the next line
        # self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise Exception("Unable to open video file.")

    def start(self):
        previous_time = time.perf_counter()

        while True:
            success, frame = self.camera.read()

            if not success:
                print("Video finished.")
                break

            current_time = time.perf_counter()
            elapsed = current_time - previous_time
            previous_time = current_time

            # Safe FPS calculation
            fps = 0
            if elapsed > 0:
                fps = 1.0 / elapsed

            # Display FPS
            cv2.putText(
                frame,
                f"FPS: {fps:.2f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("VisionEdge", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        self.camera.release()
        cv2.destroyAllWindows()