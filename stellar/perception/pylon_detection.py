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


class PylonDetector:
    @staticmethod
    def load_image(path):
        """
        Loads image in HSV color space from specified path.
        """
        return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2HSV)

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

        image_bin = np.zeros(image.shape, dtype=np.uint8)
        image_bin[image_segregated[:, :, 0] < THRESHOLD_HUE] = 255

        # Blur image to reduce noise.
        image_blurred = cv2.GaussianBlur(image_bin, (5, 5), 0)
        # Blur returns 3 channel image, we only want 1.
        image_blurred = image_blurred[:, :, :1]

        return cv2.threshold(image_blurred, 60, 255, cv2.THRESH_BINARY)[1]

    @staticmethod
    def find_pylons(image):
        # Resize image to reduce computational strain.
        image_resized = PylonDetector.resize_image(image, MAX_IMAGE_SIZE)

        pylon_map = PylonDetector.get_pylon_map(image_resized)

        _, _, stats, _ = cv2.connectedComponentsWithStats(pylon_map)

        # Ignore first element (background)
        # Keep only first 4 stats (position & dimension)
        result = stats[1:, :4]

        # Scale coordinates and dimensions back to original image size.
        factor = image.shape[0] / image_resized.shape[0]
        # Since array is uint8 but factor is float32, we can't use the *= operator.
        result[:, :] = result[:, :] * factor

        return result
