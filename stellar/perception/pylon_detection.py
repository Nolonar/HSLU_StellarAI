import os
from multiprocessing.dummy import Pool as ThreadPool

import cv2
import numpy as np

channels = [0, 1]
hist_size = [180, 64, 8][:len(channels)]
ranges = [0, 180, 0, 255, 0, 255][:len(channels) * 2]

step_x = 1
step_y = 1

threshold = 0.


class PylonDetector:
    def __init__(self):
        self.pylon = cv2.cvtColor(cv2.imread(
            'stellar/perception/pylon.jpg'), cv2.COLOR_BGR2HSV)
        self.hist_pylon = cv2.calcHist(
            [self.pylon], channels, None, hist_size, ranges)

    def find_pylon(self, image):
        pool = ThreadPool(os.cpu_count())

        res_x = image.shape[0] - self.pylon.shape[0]
        res_y = image.shape[1] - self.pylon.shape[1]

        result = np.ones(image.shape[:2])

        def processRow(x: int):
            row = np.ones(image.shape[1])
            for y in range(0, res_y, step_y):
                image_part = image[x: x + self.pylon.shape[0],
                                   y: y + self.pylon.shape[1]]
                hist_part = cv2.calcHist(
                    [image_part], channels, None, hist_size, ranges)

                row[y] = cv2.compareHist(
                    self.hist_pylon, hist_part, cv2.HISTCMP_BHATTACHARYYA)

            result[x, :] = row

        pool.map(processRow, range(0, res_x, step_x))

        min_val, _, min_loc, _ = cv2.minMaxLoc(result)
        confidence = 1 - min_val

        return {
            "is_found": confidence >= threshold,
            "confidence": confidence,
            "position_top_left": min_loc,
            "position_bottom_right": (
                min_loc[0] + self.pylon.shape[1], min_loc[1] + self.pylon.shape[0])
        }
