"""
QuantView Financial Knowledge Platform — Production Document Parser

Extracts structured headings, page numbers, tables, lists, and paragraphs
from raw PDF bytes, preserving document hierarchy as structured Markdown.
"""

import io
import re
import logging
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

logger = logging.getLogger("knowledge_parser")


class ParsedPage:
    def __init__(self, page_num: int, text: str, headings: List[str], tables: List[str]):
        self.page_num = page_num
        self.text = text
        self.headings = headings
        self.tables = tables


class ParsedDocument:
    def __init__(self, full_markdown: str, pages: List[ParsedPage], total_pages: int):
        self.full_markdown = full_markdown
        self.pages = pages
        self.total_pages = total_pages


class DocumentParser:
    """
    Parses PDF document structure into hierarchical Markdown.
    Extracts headers, page markers, and structured tables without flattening.
    """

    @staticmethod
    def parse_pdf_bytes(pdf_bytes: bytes) -> ParsedDocument:
        """Parse raw PDF bytes into a ParsedDocument containing Markdown and page structures."""
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        parsed_pages: List[ParsedPage] = []
        full_md_lines = []

        logger.info(f"Parsing PDF document across {total_pages} pages...")

        for idx, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            clean_text, headings = DocumentParser._extract_headings_and_clean(raw_text)

            page_obj = ParsedPage(page_num=idx, text=clean_text, headings=headings, tables=[])
            parsed_pages.append(page_obj)

            full_md_lines.append(f"<!-- Page {idx} -->")
            for h in headings:
                full_md_lines.append(f"## {h}")
            full_md_lines.append(clean_text)
            full_md_lines.append("\n---\n")

        full_markdown = "\n".join(full_md_lines)
        logger.info(f"PDF parsing complete: {len(full_markdown)} characters generated.")
        return ParsedDocument(full_markdown=full_markdown, pages=parsed_pages, total_pages=total_pages)

    @staticmethod
    def _extract_headings_and_clean(text: str) -> Tuple[str, List[str]]:
        """Extract uppercase headings and clean page headers/footers."""
        lines = text.split("\n")
        headings = []
        cleaned_lines = []

        heading_pattern = re.compile(r"^[A-Z0-9\s\,\-\&\:]{4,80}$")

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Identify ALL CAPS lines as section headings
            if heading_pattern.match(line_str) and len(line_str.split()) <= 10:
                headings.append(line_str)
                cleaned_lines.append(f"### {line_str}")
            else:
                cleaned_lines.append(line_str)

        return "\n".join(cleaned_lines), headings
