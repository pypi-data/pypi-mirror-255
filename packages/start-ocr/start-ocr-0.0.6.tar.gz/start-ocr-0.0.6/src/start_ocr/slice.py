from difflib import SequenceMatcher
from typing import NamedTuple

import cv2
import numpy as np
import pytesseract
from pdfplumber._typing import T_bbox
from pdfplumber.page import CroppedPage, Page


def is_match_text(
    sliced_im: np.ndarray,
    text_to_match: str,
    likelihood: float = 0.7,
) -> bool:
    """Test whether textual image in `sliced_im` resembles `text_to_match` by
    a `likelihood` percentage.

    Args:
        sliced_im (np.ndarray): Slice of a larger image containing text
        text_to_match (str): How to match the text slice in `im`
        likelihood (float): Allowed percentage expressed in decimals

    Returns:
        bool: Whether or not the `text_to_match` resembles `sliced_im`'s text.
    """
    upper_candidate = pytesseract.image_to_string(sliced_im).strip().upper()
    upper_matcher = text_to_match.upper()
    match = SequenceMatcher(None, a=upper_candidate, b=upper_matcher)
    return match.ratio() > likelihood


def get_contours(
    im: np.ndarray,
    rectangle_size: tuple[int, int],
    test_dilation: bool = False,
    test_dilated_image: str | None = "temp/dilated.png",
) -> list:
    """Using tiny `rectangle_size` of the format `(width, height)`, create a dilated version
    of the image `im`. The contours found are outputed by this function.

    Examples:
        >>> from pathlib import Path
        >>> from start_ocr.fetch import get_page_and_img
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 0)
        >>> contours = get_contours(im, (50,50))
        >>> len(contours)
        15
        >>> contours = get_contours(im, (10,10))
        >>> len(contours) in [222,223]
        True

    Args:
        im (np.ndarray): The opencv formatted image
        rectangle_size (tuple[int, int]): The width and height of the contours to make
        test_dilation (bool, optional): If `test_dilation` is `True`, a file will be created in the path represented in `test_dilated_image` to illustrate what the "diluted" image looks like.. Defaults to False.
        test_dilated_image (str | None, optional): _description_. Defaults to "temp/dilated.png".

    Returns:
        list: The contours found based on the specified structuring element

    """  # noqa: E501
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, rectangle_size)
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    if test_dilation and test_dilated_image:
        cv2.imwrite(test_dilated_image, dilate)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    return sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])


def get_likelihood_centered_coordinates(
    im: np.ndarray, text_to_match: str
) -> tuple[int, int, int, int] | None:
    """With a image `im`, get all contours found in the center
    of the image and then for each of these matches, if they
    are text resembling `text_to_match`, extract the coordinates of
    such contours.

    Examples:
        >>> from pathlib import Path
        >>> from start_ocr.fetch import get_page_and_img
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 0)
        >>> get_likelihood_centered_coordinates(im, 'Decision') # None found
        >>> res = get_likelihood_centered_coordinates(im, 'Memo')
        >>> isinstance(res, tuple)
        True
        >>> page.pdf.close()

    Args:
        im (np.ndarray): The base image to look for text
        text_to_match (str): The words that should match

    Returns:
        tuple[int, int, int, int] | None: (x, y, w, h) pixels representing
            `cv2.boundingRect`, if found.
    """  # noqa: E501
    _, im_w, _ = im.shape
    for cnt in get_contours(im, (50, 50)):
        x, y, w, h = cv2.boundingRect(cnt)
        x0_mid_left = (1 * im_w) / 4 < x
        endpoint_on_right = x + w > im_w / 2
        short_width = w > 200
        if all([x0_mid_left, endpoint_on_right, short_width]):
            # cv2.rectangle(im, (x, y), (x + w, y + h), (36, 255, 12), 3)
            # cv2.imwrite("temp/sample_boxes.png", im)
            if is_match_text(
                sliced_im=im[y : y + h, x : x + w],
                text_to_match=text_to_match,
                likelihood=0.7,
            ):
                return x, y, w, h
    return None


class PageCut(NamedTuple):
    """Fields:

    field | type | description
    --:|:--|:--
    page | pdfplumber.page.Page | The page to cut
    x0 | float or int | The x axis where the slice will start
    x1 | float or int | The x axis where the slice will terminate
    y0 | float or int | The y axis where the slice will start
    y1 | float or int | The y axis where the slice will terminate

    When the above fields are populated, the `@slice` property describes
    the area of the page that will be used to extract text from.
    """

    page: Page
    x0: float | int
    x1: float | int
    y0: float | int
    y1: float | int

    @property
    def slice(self) -> CroppedPage:
        """Unlike slicing from an image based on a `np.ndarray`, a page cut
        implies a page derived from `pdfplumber`. The former is based on pixels;
        the latter on points.

        Examples:
            >>> from pathlib import Path
            >>> from start_ocr.fetch import get_page_and_img
            >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 0) # page 1
            >>> page.height
            936
            >>> cutpage = PageCut(page=page, x0=100, x1=200, y0=100, y1=200).slice
            >>> cutpage.height
            100
            >>> page.pdf.close()

        Returns:
            CroppedPage: The page crop where to extract text from.
        """  # noqa: E501
        box: T_bbox = (self.x0, self.y0, self.x1, self.y1)
        return self.page.crop(box, relative=False, strict=True)

    @classmethod
    def set(cls, page: Page, y0: float | int, y1: float | int) -> CroppedPage:
        """Using a uniform margin on the x-axis, supply the page
        to generate page width and thus force preset margins. The `y0`
        and `y1` fields determine how to slice the page.

        Examples:
            >>> import pdfplumber
            >>> from pathlib import Path
            >>> from start_ocr.fetch import get_img_from_page
            >>> pdf = pdfplumber.open(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf")
            >>> page = pdf.pages[1] # page 2
            >>> im = get_img_from_page(page)
            >>> crop = PageCut.set(page, y0=0, y1=page.height * 0.1)
            >>> crop.extract_text()
            'ALorem IpsumDocument 2 June1,2023'
            >>> pdf.close()

        Args:
            page (Page): pdfplumber Page object
            y0 (float | int): Top y-axis
            y1 (float | int): Bottom y-axis

        Returns:
            CroppedPage: The page crop where to extract text from.
        """  # noqa: E501
        SIDE_MARGIN = 50
        x0, x1 = SIDE_MARGIN, page.width - SIDE_MARGIN
        cut = cls(page=page, x0=x0, x1=x1, y0=y0, y1=y1)
        result = cut.slice
        return result
