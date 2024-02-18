from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np
import pdfplumber
import pytesseract
from pdfplumber.page import Page


def remove_vertical_lines(im: np.ndarray):
    """Adopted from [stackoverflow answer](https://stackoverflow.com/questions/33949831/how-to-remove-all-lines-and-borders-in-an-image-while-keeping-text-programmatica)
    to handle issues seen in /raw/opinion.pdf
    """
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
    )
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(im, [c], -1, (255, 255, 255), 5)
    cv2.imwrite("temp/sample.png", im)
    return im


def paged_text(page: Page) -> str:
    """pdfplumber features an experimental setting `layout=True`.
    Used here in tandem with another setting `keep_blank_chars` to monitor
    line breaks.

    Args:
        page (Page): pdfplumber Page.

    Returns:
        str: text found from the page.
    """
    return page.extract_text(layout=True, keep_blank_chars=True).strip()


def imaged_text(page: Page) -> str:
    """Use pytesseract to extract text from the apge by first
    converting the page to numpy format."""
    img = get_img_from_page(page)
    text = pytesseract.image_to_string(img)
    return text.strip()


def get_img_from_page(page: Page) -> np.ndarray:
    """Converts a `pdfplumber.Page` to an OpenCV formatted image file.

    Args:
        page (Page): pdfplumber.Page

    Returns:
        np.ndarray: OpenCV format.
    """
    obj = page.to_image(resolution=300).original
    im = np.array(obj)
    img = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    cleaned = remove_vertical_lines(im=img)
    return cleaned


def get_page_and_img(pdfpath: str | Path, index: int) -> tuple[Page, np.ndarray]:
    """Each page of a PDF file, can be opened and cropped via `pdfplumber`.
    To parse, it's necessary to convert the pdf to an `opencv` compatible-image format
    (i.e. `np.ndarray`). This function converts a `Path` object into a pair of objects:

    1. the first part is a `pdfplumber.Page`
    2. the second part is an openCV image, i.e. `np.ndarray`

    Examples:
        >>> page, im = get_page_and_img(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf", 0) # 0 marks the first page
        >>> page.page_number # the first page
        1
        >>> isinstance(page, Page)
        True
        >>> isinstance(im, np.ndarray)
        True
        >>> page.pdf.close()

    Args:
        pdfpath (str | Path): Path to the PDF file.
        index (int): Zero-based index that determines the page number.

    Returns:
        tuple[Page, np.ndarray]: Page identified by `index`  with image of the
            page  (in np format) that can be manipulated.
    """  # noqa: E501
    with pdfplumber.open(pdfpath) as pdf:
        page = pdf.pages[index]
        img = get_img_from_page(page)
        return page, img


def get_pages_and_imgs(
    pdfpath: str | Path,
) -> Iterator[tuple[Page, np.ndarray]]:
    """Get page and images in sequential order.

    Examples:
        >>> results = get_pages_and_imgs(Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf")
        >>> result = next(results)
        >>> type(result)
        <class 'tuple'>
        >>> isinstance(result[0], Page)
        True
        >>> result[0].page_number == 1 # first
        True

    Args:
        pdfpath (Page | Path): Path to the PDF file.

    Yields:
        Iterator[tuple[Page, np.ndarray]]: Pages with respective images
    """  # noqa: E501
    with pdfplumber.open(pdfpath) as pdf:
        index = 0
        while index < len(pdf.pages):
            page = pdf.pages[index]
            yield page, get_img_from_page(page)
            index += 1


def get_reverse_pages_and_imgs(
    pdfpath: str | Path,
) -> Iterator[tuple[Page, np.ndarray]]:
    """Start from end page to get to first page to determine terminal values.

    Examples:
        >>> x = Path().cwd() / "tests" / "data" / "lorem_ipsum.pdf"
        >>> num_pages = pdfplumber.open(x).pages
        >>> results = get_reverse_pages_and_imgs(x)
        >>> result = next(results)
        >>> type(result)
        <class 'tuple'>
        >>> isinstance(result[0], Page)
        True
        >>> result[0].page_number == len(num_pages) # last page is first
        True

    Args:
        pdfpath (Page | Path): Path to the PDF file.

    Yields:
        Iterator[tuple[Page, np.ndarray]]: Pages with respective images
    """  # noqa: E501
    with pdfplumber.open(pdfpath) as pdf:
        index = len(pdf.pages) - 1
        while index >= 0:
            page = pdf.pages[index]
            yield page, get_img_from_page(page)
            index -= 1
