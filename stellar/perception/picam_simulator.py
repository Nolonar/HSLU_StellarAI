import sys
from os import path

import cv2
import numpy as np

DIRECTORY = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(DIRECTORY))
# workaround for autopep8 moving imports to the top.
if 'send_message' not in sys.modules:
    from communication.sender import send_message


class Simulator:
    is_running: bool = True
    stream: cv2.VideoCapture = None

    def __init__(self, source_video_path: str):
        self.stream = cv2.VideoCapture(source_video_path)

    def run(self):
        while self.is_running:
            got_frame, frame = self.stream.read()
            print(got_frame)
            print(frame)

            if got_frame:
                send_message('perception/camera', {
                    'frame': frame
                })

            self.is_running = got_frame

    def stop(self):
        self.is_running = False


simulator = Simulator("cv_video_final.mp4")
simulator.run()
