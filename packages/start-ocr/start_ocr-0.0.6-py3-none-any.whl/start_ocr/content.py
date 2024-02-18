import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import pdfplumber
from pdfplumber.page import CroppedPage, Page

from .components import (
    Bodyline,
    Footnote,
    get_header_line,
    get_page_end,
    get_page_num,
    page_width_lines,
    paragraph_break,
)
from .fetch import get_img_from_page, imaged_text, paged_text
from .slice import PageCut


@dataclass
class Content:
    """Metadata of a single content page.

    Field | Description
    --:|:--
    `page_num` | Page number
    `body` | Main content above an annex, if existing
    `segments` | Segments of the `body`'s text in the given `page_num`
    `annex` | Portion of page containing the footnotes; some pages are annex-free
    `footnotes` | Each footnote item in the `annex`'s text in the given `page_num`
    """  # noqa: E501

    page_num: int
    body: CroppedPage
    body_text: str
    annex: CroppedPage | None = None
    annex_text: str | None = None
    segments: list[Bodyline] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)

    def __post_init__(self):
        alpha = paragraph_break.split(self.body_text)
        beta = self.body_text.split("\n\n")
        candidates = alpha or beta
        self.segments = Bodyline.split(candidates, self.page_num)
        if self.annex and self.annex_text:
            self.footnotes = Footnote.extract_notes(self.annex_text, self.page_num)

    def __repr__(self) -> str:
        return f"<Content Page: {self.page_num}>"

    @classmethod
    def set(
        cls,
        page: Page,
        start_y: float | int | None = None,
        end_y: float | int | None = None,
    ) -> Self:
        """
        A `header_line` (related to `start_y`) and `page_line` (related to `end_y`) are utilized as local variables in this function.

        The `header_line` is the imaginary line at the top of the page. If the `start_y` is supplied, it means that the `header_line` no longer needs to be calculated.

        The `page_line` is the imaginary line at the bottom of the page. If the `end_y` is supplied, it means that the calculated `page_line` ought to be replaced.

        The presence of a `header_line` and a `page_endline` determine what to extract as content from a given `page`.

        Args:
            page (Page): The pdfplumber page to evaluate
            start_y (float | int | None, optional): If present, refers to The y-axis point of the starter page. Defaults to None.
            end_y (float | int | None, optional): If present, refers to The y-axis point of the ender page. Defaults to None.

        Returns:
            Self: Page with individual components mapped out.
        """  # noqa: E501
        im = get_img_from_page(page)

        header_line = start_y or get_header_line(im, page)
        if not header_line:
            raise Exception(f"No header line in {page.page_number=}")

        end_of_content, e = get_page_end(im, page)
        page_line = end_y or end_of_content

        body = PageCut.set(page=page, y0=header_line, y1=page_line)
        body_text = paged_text(body) or imaged_text(body)
        annex = None
        annex_text = None

        if e:
            annex = PageCut.set(page=page, y0=end_of_content, y1=e)
            annex_text = paged_text(annex) or imaged_text(annex)

        return cls(
            page_num=get_page_num(page, header_line),
            body=body,
            body_text=body_text,
            annex=annex,
            annex_text=annex_text,
        )


@dataclass
class Collection:
    """Metadata of a pdf file consisting of one or many `Content` structures.

    Field | Description
    --:|:--
    `pages` | A list of `Content` pages
    `body` | Compilation of each page's `body_text`
    `annex` | Compilation of each page's `annex_text`, if existing
    `segments` | Each `Bodyline` of the body
    `footnotes` | Each `Footnote` of the annex
    """

    pages: list[Content] = field(default_factory=list)
    segments: list[Bodyline] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)
    body: str = ""
    annex: str = ""

    def __repr__(self) -> str:
        return f"<Collection Page Count: {len(self.pages)}>"

    @classmethod
    def preliminary_page(cls, path: Path) -> Content:
        """Often necessary to format front page because of special rules, i.e.
        the logical start won't be at the top of the document but at some designated
        position.  For this example of a preliminary page, we'll use sample file's
        initial page which contains a line at the top of the document."""
        with pdfplumber.open(path) as pdf:
            first_page = pdf.pages[0]
            im = get_img_from_page(first_page)
            lines = page_width_lines(im)
            im_h, _, _ = im.shape
            start_y = (lines[0].y1 / im_h) * first_page.height
            content = Content.set(page=first_page, start_y=start_y)
            return content

    @classmethod
    def is_ok(cls, candidate: Page, min_char_length: int = 10):
        """A convenience function to check if the page contains text."""

        if text := candidate.extract_text_simple():
            if chars := len(text.strip()):
                if chars >= min_char_length:
                    return True
        return False

    @classmethod
    def make(cls, path: Path, preliminary_page: Content) -> Self:
        """Each instance of a `Collection` starts with the `preliminary_page`.
        Subsequent pages are checked if they contain text and are
        added to the instance. During the `add()` step, each of the
        pages are examined for `Content`."""
        with pdfplumber.open(path) as pdf:
            collection = cls(pages=[preliminary_page])
            next_pages = pdf.pages[1:]
            candidates = [page for page in next_pages if cls.is_ok(page)]
            collection.add(next_pages=candidates)
            return collection

    def add(self, next_pages: list[Page]):
        for page in next_pages:
            if page_valid := Content.set(page=page):
                self.pages.append(page_valid)
        self.join_segments()
        self.join_annexes()

    def join_segments(self):
        for page in self.pages:
            self.body += f"\n\n{page.body_text}"
            self.segments.extend(page.segments)

    def join_annexes(self):
        for page in self.pages:
            if page.annex_text:
                self.annex += f"\n\n{page.annex_text}"
                self.footnotes.extend(page.footnotes)
