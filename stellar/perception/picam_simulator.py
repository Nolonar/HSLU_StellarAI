import cv2
import numpy as np


class Simulator:
    is_running: bool = True
    stream: cv2.VideoCapture = None
    current_frame = None

    def __init__(self, source_video_path: str):
        self.stream = cv2.VideoCapture(source_video_path)

    def run(self):
        while self.is_running:
            got_frame, frame = self.stream.read()

            if got_frame:
                frame = self.rotate_frame(frame)
                self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            self.is_running = got_frame

    @staticmethod
    def rotate_frame(frame):
        h, w = frame.shape[:2]
        center = (w / 2, h / 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, 180, 1)
        return cv2.warpAffine(frame, rotation_matrix, (w, h))

    def stop(self):
        self.is_running = False
