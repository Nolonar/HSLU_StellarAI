import cv2
import numpy as np

# The maximum size of the image to be processed.
# Bigger images will be shrunk to match the size.
# Smaller images will be left as is.
MAX_IMAGE_SIZE = 300

# How far two pixels can be to be considered neighbors.
# Higher values increase computing time.
COLOR_SEGREGATION_SPATIAL_RADIUS = 20
# How far two colors can be to be considered similar.
COLOR_SEGREGATION_COLOR_RADIUS = 40

# The maximum hue [0, 179] we are looking for.
THRESHOLD_HUE = 30

# Debug only: used to give debug images unique names between different test of the same test run.
run_id = 0


class PylonDetector:
    @staticmethod
    def load_image(path):
        """
        Loads image in HSV color space from specified path.
        """
        return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2HSV)

    @staticmethod
    def write_image(image, path):
        """
        Writes image to sepcified path.
        """

        image_out = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)

        cv2.imwrite(path, image_out)

    @staticmethod
    def write_image_debug(image, name):
        """
        Debug only: writes a debug image with specified name.
        """

        image_out = image
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_out = cv2.cvtColor(image_out, cv2.COLOR_HSV2BGR)

        cv2.imwrite(
            f"tests/pylon_test_images_output/{run_id}_{name}.jpg", image_out)

    @staticmethod
    def mark_pylons(image, pylons_found):
        """
        Marks found pylons in image by drawing rectangles around them.
        """

        for pylon in pylons_found:
            pt1 = (pylon[0], pylon[1])
            pt2 = (pt1[0] + pylon[2], pt1[1] + pylon[3])

            cv2.rectangle(image, pt1, pt2, [120, 255, 255], 2)

        return image

    @staticmethod
    def resize_image(image, max_size):
        """
        Resizes image while preserving aspect ratio.
        Width and height are guaranteed to be equal to
        or smaller than max_size.
        """
        x_res = image.shape[1]
        y_res = image.shape[0]

        x_factor = max_size / x_res
        y_factor = max_size / y_res
        factor = min([x_factor, y_factor])

        x_res_new = int(x_res * factor)
        y_res_new = int(y_res * factor)

        return cv2.resize(image, (x_res_new, y_res_new))

    @staticmethod
    def segregate_colors(image):
        """
        Segregates colors from image to simplify object recognition.
        """
        return cv2.pyrMeanShiftFiltering(image, COLOR_SEGREGATION_SPATIAL_RADIUS, COLOR_SEGREGATION_COLOR_RADIUS)

    @staticmethod
    def get_pylon_map(image):
        """
        Produces a map of the same dimension and size as image,
        where 1 indicates a pixel belonging to a pylon,
        and 0 indicates a pixel not belonging to a pylon.
        """
        image_segregated = PylonDetector.segregate_colors(image)
        PylonDetector.write_image_debug(image_segregated, "b_seg")

        image_bin = np.zeros(image.shape, dtype=np.uint8)
        image_bin[image_segregated[:, :, 0] < THRESHOLD_HUE] = 255
        PylonDetector.write_image_debug(image_bin, "c_bin")

        # Reduce noise
        structuring_element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        image_filtered = cv2.morphologyEx(
            image_bin, cv2.MORPH_CLOSE, structuring_element, iterations=3)
        image_filtered = image_filtered[:, :, :1]
        PylonDetector.write_image_debug(image_filtered, "d_bin_filtered")

        return cv2.threshold(image_filtered, 60, 255, cv2.THRESH_BINARY)[1]

    @staticmethod
    def find_pylons(image):
        global run_id
        run_id += 1

        # Resize image to reduce computational strain.
        image_resized = PylonDetector.resize_image(image, MAX_IMAGE_SIZE)
        PylonDetector.write_image_debug(image_resized, "a_resized")

        pylon_map = PylonDetector.get_pylon_map(image_resized)
        PylonDetector.write_image_debug(pylon_map, "e_map")

        _, _, stats, _ = cv2.connectedComponentsWithStats(pylon_map)

        # Ignore first element (background)
        # Keep only first 4 stats (position & dimension)
        result = stats[1:, :4]

        # Scale coordinates and dimensions back to original image size.
        factor = image.shape[0] / image_resized.shape[0]
        # Since array is uint8 but factor is float32, we can't use the *= operator.
        result[:, :] = result[:, :] * factor

        return result
