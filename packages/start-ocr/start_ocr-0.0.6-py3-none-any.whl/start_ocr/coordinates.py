from typing import NamedTuple

import cv2
from numpy import ndarray

GREEN = (36, 255, 12)
PURPLE = (255, 0, 0)


class CoordinatedImage(NamedTuple):
    """Each filtered item can be wrapped around this data structure where each will have its own
    dimensions, that can be used in relation to the original image (`im`):

    raw dimension | definition
    --:|:--
    `x` | _x_-axis position marking the start of the filtered item
    `y` | _y_-axis position marking the start of the filtered item
    `w` | x-axis based _w_idth of the filtered item
    `h` | y-axis based _h_eight of the filtered item

    This "coordinates" setup enables the calculation of the end positions (of the
    filtered items) as properties, e.g.:

    calculated dimension | calculation | definition
    --:|:--:|:--
    `x1` | `x + w` | x-axis position marking the end of the filtered item
    `y1` | `y + h` | y-axis position marking the end of the filtered item
    """  # noqa: E501

    im: ndarray
    x: float
    y: float
    w: float
    h: float

    @property
    def x1(self):
        """X-axis position marking end of filtered item."""
        return self.x + self.w

    @property
    def y1(self):
        """Y-axis position marking end of filtered item."""
        return self.y + self.h

    @property
    def upper_left_point(self) -> tuple[float, float]:
        """The upper left point of a rectangle."""
        return (self.x, self.y)

    @property
    def lower_right_point(self) -> tuple[float, float]:
        """The lower right point of a rectangle."""
        return (self.x1, self.y1)

    @property
    def fragment(self) -> ndarray:
        """The slice of an image with the filtered coordinates in the format:
        image [pt1, pt2] where:

        1. pt1 = from point y to point y1
        1. pt2 = from point x to point x1
        """
        return self.im[self.y : self.y1, self.x : self.x1]

    def greenbox(self):
        """Add a "green box" to the image where the box area is represented by the
        diagonal of pt1 and pt2: pt1 being the upper left point and pt2 being
        the lower right point of the rectangle."""
        return cv2.rectangle(
            img=self.im,
            pt1=self.upper_left_point,
            pt2=self.lower_right_point,
            color=GREEN,
            thickness=2,
        )

    def redbox(self):
        """Add a "green box" to the image where the box area is represented by the
        diagonal of pt1 and pt2: pt1 being the upper left point and pt2 being
        the lower right point of the rectangle."""
        return cv2.rectangle(
            img=self.im,
            pt1=self.upper_left_point,
            pt2=self.lower_right_point,
            color=PURPLE,
            thickness=1,
        )
