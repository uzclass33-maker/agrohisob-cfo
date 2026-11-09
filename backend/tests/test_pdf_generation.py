"""
Tests for PDF Bank Dossier generator using ReportLab (Assignment 5).
"""

import os
import tempfile
import pytest

from app.reporting.dossier_builder import DossierBuilder
from app.reporting.pdf_generator import PDFReportGenerator


def test_generate_pdf_in_memory():
    """Verify that PDF generation produces non-empty bytes with valid %PDF- magic header."""
    dossier = DossierBuilder.build_dossier("scenario-small-farmer")
    pdf_bytes = PDFReportGenerator.generate_dossier_pdf(dossier)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 5000  # ReportLab multi-page document should exceed 5KB
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_pdf_to_file():
    """Verify writing PDF directly to disk."""
    dossier = DossierBuilder.build_dossier("scenario-exporter")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        pdf_bytes = PDFReportGenerator.generate_dossier_pdf(dossier, output_path=tmp_path)
        assert os.path.exists(tmp_path)
        file_size = os.path.getsize(tmp_path)
        assert file_size == len(pdf_bytes)
        assert file_size > 5000
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
