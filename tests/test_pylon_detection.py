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

    test_image_name = "0124"

    test_image = PylonDetector.load_image(
        f"tests/pylon_test_images/{test_image_name}.jpg")
    pylons_found = PylonDetector.find_pylons(test_image)

    print(len(pylons_found))

    output_image = cv2.cvtColor(test_image, cv2.COLOR_HSV2RGB)
    # weird bug in openCV, where conversion from HSV to RGB actually returns BGR instead...
    output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
    for pylon in pylons_found:
        pt1 = (pylon[0], pylon[1])
        pt2 = (pt1[0] + pylon[2], pt1[1] + pylon[3])

        cv2.rectangle(output_image, pt1, pt2, [255, 0, 0], 2)

    cv2.imwrite(
        f"tests/pylon_test_images_output/{test_image_name}.jpg", output_image)

    assert True
