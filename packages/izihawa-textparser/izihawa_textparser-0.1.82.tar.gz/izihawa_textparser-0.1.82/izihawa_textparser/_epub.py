import re
import tempfile

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from izihawa_textutils.html_processing import canonize_tags

from .utils import BANNED_SECTIONS, md


class EpubParser:
    def __init__(self, banned_sections: set[str] = BANNED_SECTIONS):
        if banned_sections is None:
            self.banned_sections = set()
        else:
            self.banned_sections = banned_sections

    def parse_soup(self, soup: BeautifulSoup):
        body = soup.find("body")
        if not body:
            return

        for _ in list(
            soup.select("body > .copyright-mtp, body > .halftitle, body > .book-title")
        ):
            return

        for section in list(soup.find_all("section")):
            for child in section.children:
                if (
                    child.name in {"header", "h1", "h2", "h3", "h4", "h5", "h6", "div"}
                    and child.text.lower().strip(" :,.;") in self.banned_sections
                ):
                    section.extract()
                    break

        for summary in list(soup.select("details > summary.section-heading")):
            if summary.text.lower().strip(" :,.;") in self.banned_sections:
                summary.parent.extract()

        for header in list(soup.select("body h1")):
            if header.text.lower().strip(" :,.;") in self.banned_sections:
                header.parent.extract()

        for b_tag in list(soup.select("b, i")):
            b_tag.unwrap()

        for p_tag in list(soup.find_all("p")):
            sibling = p_tag.next_sibling
            while sibling == "\n":
                sibling = sibling.next_sibling
            if sibling and sibling.name == "blockquote":
                new_p_tag = soup.new_tag("p")
                new_p_tag.extend([p_tag.text, " ", sibling.text])
                p_tag.replace_with(new_p_tag)
                sibling.extract()

        for el in list(
            soup.select(
                'table, nav, ref, formula, math, figure, img, [role="note"], .Affiliations, '
                ".ArticleOrChapterToc, .FM-head, .EM-copyright-text, .EM-copyright-text-space, "
                ".AuthorGroup, .ChapterContextInformation, "
                ".Contacts, .CoverFigure, .Bibliography, "
                ".BookTitlePage, .BookFrontmatter, .CopyrightPage, .Equation, "
                ".FootnoteSection, .Table, .reference, .side-box-text, .thumbcaption"
            )
        ):
            el.extract()

        for el in list(soup.select("a, span")):
            el.unwrap()
        return md.convert_soup(canonize_tags(soup)).strip()


def extract_epub(content: bytes):
    epub_parser = EpubParser()
    with tempfile.NamedTemporaryFile(mode="w+b", delete=False) as t_file:
        t_file.write(content)
        file_name = t_file.name
        book = epub.read_epub(file_name)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        texts = []
        for item in items:
            if "chapter" in item.get_name():
                soup = BeautifulSoup(item.get_body_content(), "lxml")
                text = epub_parser.parse_soup(soup)
                text = re.sub("\n([a-z])", r' \g<1>', text)
                texts.append(text)
        return "\n\n".join(texts)
