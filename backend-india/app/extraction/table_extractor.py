"""
QuantView — PDF Table Extraction Service

Extracts tabular financial data from PDF reports to populate relational database schemas.
"""

import logging
import os
import tabula
import pandas as pd

logger = logging.getLogger("table_extractor")

class TableExtractor:
    """Handles parsing and extraction of tables from PDFs using tabula-py."""

    @staticmethod
    def extract_tables(pdf_path: str, page_number: int = 1) -> list[pd.DataFrame]:
        """
        Parses tables from a specific page of a PDF file.
        Returns a list of pandas DataFrames.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return []

        try:
            # tabula-py extracts tables as DataFrames
            dfs = tabula.read_pdf(pdf_path, pages=page_number, multiple_tables=True)
            return dfs
        except Exception as e:
            logger.error(f"Error extracting tables from PDF {pdf_path} page {page_number}: {e}")
            return []
