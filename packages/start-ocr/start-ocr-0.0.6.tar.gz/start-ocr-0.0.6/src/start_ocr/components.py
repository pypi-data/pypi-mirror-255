import re
from typing import NamedTuple, Self

import cv2
import numpy as np
from pdfplumber.page import Page

from .coordinates import CoordinatedImage
from .slice import get_contours

line_break = re.compile(r"\s*\n+\s*")

paragraph_break = re.compile(r"\s{10,}(?=[A-Z])")

footnote_nums = re.compile(r"(\n\s+|^)(?P<fn>\d+)(?=\s+[A-Z])")


class Bodyline(NamedTuple):
    """Each page may be divided into lines which, for our purposes,
    will refer to an arbitrary segmentation of text based on regex parameters.

    Field | Type | Description
    --:|:--:|:--
    `num` | int | Order in the page
    `line` | str | The text found based on segmentation
    """

    page_num: int
    order_num: int
    line: str

    @classmethod
    def split(cls, prelim_lines: list[str], page_num: int) -> list[Self]:
        """Get paragraphs using regex `\\s{10,}(?=[A-Z])`
        implying many spaces before a capital letter then
        remove new lines contained in non-paragraph lines.

        Args:
            prelim_lines (list[str]): Previously split text

        Returns:
            list[Self]: Bodylines of segmented text
        """
        lines = []
        for order_num, par in enumerate(prelim_lines, start=1):
            obj = cls(
                page_num=page_num,
                order_num=order_num,
                line=line_break.sub(" ", par).strip(),
            )
            lines.append(obj)
        lines.sort(key=lambda obj: obj.order_num)
        return lines


class Footnote(NamedTuple):
    """Each page may contain an annex which consists of footnotes. Note
    that this is based on a imperfect use of regex to detect the footnote
    number `fn_id` and its corresponding text `note`.

    Field | Type | Description
    --:|:--:|:--
    `fn_id` | int | Footnote number
    `note` | str | The text found based on segmentation of footnotes
    """

    page_num: int
    fn_id: int
    note: str

    @classmethod
    def extract_notes(cls, text: str, page_num: int) -> list[Self]:
        """Get footnote digits using regex `\\n\\s+(?P<fn>\\d+)(?=\\s+[A-Z])`
        then for each matching span, the start span becomes the anchor
        for the balance of the text for each remaining foornote in the while
        loop. The while loop extraction must use `.pop()` where the last
        item is removed first.

        Args:
            text (str): Text that should be convertible to footnotes based on regex

        Returns:
            list[Self]: Footnotes separated by digits.
        """
        notes = []
        while True:
            matches = list(footnote_nums.finditer(text))
            if not matches:
                break
            note = matches.pop()  # start from the last
            footnote_num = int(note.group("fn"))
            digit_start, digit_end = note.span()
            footnote_body = text[digit_end:].strip()
            obj = cls(
                page_num=page_num,
                fn_id=footnote_num,
                note=footnote_body,
            )
            notes.append(obj)
            text = text[:digit_start]
        notes.sort(key=lambda obj: obj.fn_id)
        return notes


## HEADER


def get_header_upper_right(
    im: np.ndarray,
) -> tuple[int, int, int, int] | None:
    """The header represents non-title page content above the main content.

    It usually consists of three items:

    Item | Label | Test PDF
    --:|:--|:--
    1 | Indicator text | `Indicator`
    2 | Page number | `1`
    3 | Some other detail | `xyzabc123`

    This detects Item (3) which implies that it is the in upper right quarter
    of the document:

    ```py
    x > im_w / 2  # ensures that it is on the right side of the page
    y <= im_h * 0.2  # ensures that it is on the top quarter of the page
    ```

    Item (3) is the only one above that is likely to have a second vertical line,
    hence choosing this as the the typographic bottom for the header makes sense.

    Examples:
        >>> from start_ocr import get_page_and_img
        >>> from pathlib import Path
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 1)
        >>> isinstance(get_header_upper_right(im), tuple)
        True
        >>> page.pdf.close()

    Args:
        im (numpy.ndarray): The full page image

    Returns:
        tuple[int, int, int, int] | None: The coordinates of the docket, if found.
    """  # noqa: E501
    im_h, im_w, _ = im.shape
    for cnt in get_contours(im, (50, 50)):
        x, y, w, h = cv2.boundingRect(cnt)
        if x > im_w / 2 and y <= im_h * 0.25 and w > 200:
            return x, y, w, h
    return None


def get_header_line(im: np.ndarray, page: Page) -> int | float | None:
    """The header represents non-title page content above the main content.

    The terminating header line is a non-visible line that separates the
    decision's header from its main content. We'll use a typographic bottom
    of the header to signify this line.

    Examples:
        >>> from pathlib import Path
        >>> from start_ocr import get_page_and_img
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 1)
        >>> int(get_header_line(im, page)) in [76, 77]
        True
        >>> page.pdf.close()

    Args:
        im (numpy.ndarray): The full page image
        page (Page): The pdfplumber page

    Returns:
        float | None: Y-axis point (pdfplumber point) at bottom of header
    """  # noqa: E501
    im_h, im_w, _ = im.shape
    if hd := get_header_upper_right(im):
        _, y, _, h = hd
        header_end = (y + h) / im_h
        terminal = header_end * page.height
        return terminal
    return None


def get_page_num(page: Page, header_line: int | float) -> int:
    """Aside from the first page, which should always be `1`,
    this function gets the first matching digit in the header's text.
    If no such digit is round, return 0.

    Examples:
        >>> import pdfplumber
        >>> from pathlib import Path
        >>> from start_ocr import get_img_from_page
        >>> x = Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf"
        >>> pdf = pdfplumber.open(x)
        >>> page = pdf.pages[1] # page 2
        >>> im = get_img_from_page(page)
        >>> header_line = get_header_line(im, page)
        >>> get_page_num(page, header_line)
        2
        >>> pdf.close()

    Args:
        page (Page): The pdfplumber page
        header_line (int | float): The value retrieved from `get_header_line()`

    Returns:
        int | None: The page number, if found
    """
    if page.page_number == 1:
        return 1  # The first page should always be page 1

    box = (0, 0, page.width, header_line)
    header = page.crop(box, relative=False, strict=True)
    texts = header.extract_text(layout=True, keep_blank_chars=True).split()
    for text in texts:
        if text.isdigit() and len(text) <= 3:
            return int(text)  # Subsequent pages shall be based on the header

    return 0  # 0 implies


## FOOTER


PERCENT_OF_MAX_PAGE = 0.94


def page_width_lines(im: np.ndarray) -> list[CoordinatedImage]:
    """Filter long horizontal lines:

    1. Edges of lines must be:
        - on the left of the page; and
        - on the right of the page
    2. Each line must be at least 1/2 the page width

    Examples:
        >>> from start_ocr import get_page_and_img
        >>> from pathlib import Path
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 0)
        >>> res = page_width_lines(im)
        >>> len(res) # only one image matches the filter
        3
    """  # noqa: E501
    _, im_w, _ = im.shape
    results = []
    contours = get_contours(
        im=im,
        rectangle_size=(100, 100),
        test_dilation=True,
        test_dilated_image="temp/dilated.png",
    )
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        contoured = CoordinatedImage(im, x, y, w, h)
        contoured.redbox()
        filtering_criteria = [
            w > im_w / 2,  # width greater than half
            x < im_w / 3,  # edge of line on first third
            (x + w) > im_w * (2 / 3),  # edge of line on last third
        ]
        if all(filtering_criteria):
            obj = CoordinatedImage(im, x, y, w, h)
            obj.greenbox()
            results.append(obj)
    cv2.imwrite("temp/boxes.png", im)
    return results


def footnote_lines(im: np.ndarray) -> list[CoordinatedImage]:
    """Filter short horizontal lines:

    1. > width of 300 pixels
    2. height of less than 40 pixels, using the test pdf, any larger than 44 pixels will make this include text as well.

    The footer represents content below the main content. This is also
    called the annex of the page.

    This detects a short line in the lower half of the page that has at least a width
    of 400 pixels and a , indicating a narrow box
    (as dilated by openCV). Text found below this box represents the annex.

    Examples:
        >>> from start_ocr import get_page_and_img
        >>> from pathlib import Path
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 0)
        >>> res = footnote_lines(im)
        >>> len(res) # only one image matches the filter
        1

    """  # noqa: E501
    _, im_w, _ = im.shape
    contours = get_contours(
        im=im,
        rectangle_size=(30, 10),
        test_dilation=True,
        test_dilated_image="temp/dilated.png",
    )
    results = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        filtering_criteria = [
            x < (im_w / 2),
            (x + w) < (im_w / 2),
            (im_w / 2) > w > 300,
            h < 40,
        ]
        if all(filtering_criteria):
            obj = CoordinatedImage(im, x, y, w, h)
            obj.greenbox()
            results.append(obj)
    cv2.imwrite("temp/boxes.png", im)
    return results


def get_page_end(im: np.ndarray, page: Page) -> tuple[float, float | None]:
    """Given an `im`, detect footnote line of annex and return relevant points in the y-axis as a tuple.

    Scenario | Description | y0 | y1
    :--:|:-- |:--:|:--:
    Footnote line exists | Page contains footnotes | int or float | int or float signifying end of page
    Footnote line absent | Page does not contain footnotes | int or float signifying end of page | `None`

    Examples:
        >>> from start_ocr import get_page_and_img
        >>> from pathlib import Path
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 0)
        >>> res = get_page_end(im, page)
        >>> isinstance(res, tuple)
        True
        >>> int(res[0])
        822
        >>> int(res[1])
        879

    Args:
        im (numpy.ndarray): the openCV image that may contain a footnote line
        page (Page): the pdfplumber.page.Page based on `im`

    Returns:
        tuple[float, float | None]: Annex line's y-axis (if it exists) and the page's end content line.
    """  # noqa: E501
    y1 = PERCENT_OF_MAX_PAGE * page.height
    im_h, _, _ = im.shape
    if lines := footnote_lines(im):
        fn_line_end = lines[0].y / im_h
        y0 = fn_line_end * page.height
        return y0, y1
    return y1, None
