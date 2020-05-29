"""
Tests for pylon detection.
"""
import pytest

from stellar.perception.pylon_detection import PylonDetector


def test_not_crashing():
    """
    Ensure pylon detection doesn't crash.
    """

    test_image_name = "0001"
    test_image = PylonDetector.load_image(
        f"tests/pylon_test_images/{test_image_name}.jpg")

    pylons_found = PylonDetector.find_pylons(test_image)

    image_out = PylonDetector.mark_pylons(test_image, pylons_found)
    PylonDetector.write_image_debug(image_out, "final")

    assert True


def test_0389_has_3_pylons():
    """
    Ensure PylonDetector detects the correct amount of pylons.
    """

    test_image_name = "0389"
    test_image = PylonDetector.load_image(
        f"tests/pylon_test_images/{test_image_name}.jpg")

    pylons_found = PylonDetector.find_pylons(test_image)

    image_out = PylonDetector.mark_pylons(test_image, pylons_found)
    PylonDetector.write_image_debug(image_out, "final")

    assert len(pylons_found) == 3


def test_distance_is_80():
    """
    Ensure PylonDetector detects the correct distance.
    """

    test_image_name = "distance-test"
    test_image = PylonDetector.load_image(
        f"tests/pylon_test_images/{test_image_name}.jpg")

    pylons_found = PylonDetector.find_pylons(test_image)

    image_out = PylonDetector.mark_pylons(test_image, pylons_found)
    PylonDetector.write_image_debug(image_out, "final")

    assert pylons_found[0].estimated_distance_cm == pytest.approx(80, 0.1)
