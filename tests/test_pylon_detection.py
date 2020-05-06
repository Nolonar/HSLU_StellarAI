"""
Tests for pylon detection.
"""
import cv2
import numpy as np
import pytest

from stellar.perception.pylon_detection import PylonDetector


def test_not_crashing():
    """
    Ensure pylon detection doesn't crash.
    """

    testee = PylonDetector()

    test_image = cv2.imread("tests/pylon_test_images/0001.jpg")
    result = testee.find_pylon(cv2.cvtColor(test_image, cv2.COLOR_BGR2HSV))

    if result["is_found"]:
        cv2.rectangle(test_image, result["position_top_left"],
                      result["position_bottom_right"], [255, 0, 0], 2)
        cv2.imwrite("tests/pylon_test_images_output/0001.jpg", test_image)

    assert True
