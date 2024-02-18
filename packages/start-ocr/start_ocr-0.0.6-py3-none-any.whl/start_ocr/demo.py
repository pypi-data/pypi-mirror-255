import cv2
import numpy as np

from .coordinates import CoordinatedImage
from .slice import get_contours


def show_contours(im: np.ndarray, rectangle_size: tuple[int, int]) -> list:
    contours = get_contours(
        im,
        rectangle_size,
        test_dilation=True,
        test_dilated_image="temp/dilated.png",
    )
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        obj = CoordinatedImage(im, x, y, w, h)
        obj.greenbox()
    cv2.imwrite("temp/boxes.png", im)
    return contours
