import os
import tempfile
import pytest
from urllib.parse import urlparse
from unittest.mock import patch, MagicMock

# Assume your functions live in pdf_utils.py
from app.utils.pdf_utils import (
    classify_pdf_path,
    is_url_reachable,
    classify_pdf_list,
)

def test_classify_pdf_path_local(tmp_path):
    # create a dummy PDF file
    p = tmp_path / "doc.pdf"
    p.write_text("dummy")
    # absolute and relative
    assert classify_pdf_path(str(p)) == "local"
    assert classify_pdf_path(f"file://{p}") == "local"

def test_classify_pdf_path_url():
    assert classify_pdf_path("https://example.com/foo.pdf") == "url"
    assert classify_pdf_path("http://example.com/bar.PDF") == "url"
    assert classify_pdf_path("ftp://ftp.example.org/manual.pdf") == "url"

def test_classify_pdf_path_unknown(tmp_path):
    # non-existing file
    assert classify_pdf_path(str(tmp_path / "no.pdf")) == "unknown"
    # wrong extension
    assert classify_pdf_path("https://example.com/file.txt") == "unknown"
    assert classify_pdf_path("random_string") == "unknown"

@patch("pdf_utils.requests.head")
def test_is_url_reachable_success(mock_head):
    # mock a 200 OK PDF response
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {"Content-Type": "application/pdf; charset=UTF-8"}
    mock_head.return_value = resp

    assert is_url_reachable("https://fake.test/doc.pdf") is True
    mock_head.assert_called_once()

@patch("pdf_utils.requests.head")
def test_is_url_reachable_failure_status(mock_head):
    # mock a 404 Not Found
    resp = MagicMock()
    resp.status_code = 404
    resp.headers = {"Content-Type": "application/pdf"}
    mock_head.return_value = resp

    assert is_url_reachable("https://fake.test/missing.pdf") is False

@patch("pdf_utils.requests.head", side_effect=Exception("timeout"))
def test_is_url_reachable_exception(mock_head):
    assert is_url_reachable("https://fake.test/timeout.pdf") is False

def test_classify_pdf_list_without_verification(tmp_path):
    # setup local file
    local = tmp_path / "a.pdf"
    local.write_text("x")
    paths = [
        str(local),
        "https://site.com/x.pdf",
        "not_a_pdf.txt",
    ]
    locals_, urls_ = classify_pdf_list(paths, verify_urls=False)
    assert locals_ == [str(local)]
    assert urls_ == ["https://site.com/x.pdf"]

@patch("pdf_utils.is_url_reachable")
def test_classify_pdf_list_with_verification(mock_reach, tmp_path):
    # setup local file
    local = tmp_path / "b.pdf"
    local.write_text("y")
    paths = [
        str(local),
        "https://site.com/good.pdf",
        "https://site.com/bad.pdf",
    ]
    # good is reachable, bad is not
    def reach(url):
        return url.endswith("good.pdf")
    mock_reach.side_effect = reach

    locals_, urls_ = classify_pdf_list(paths, verify_urls=True)
    assert locals_ == [str(local)]
    assert urls_ == ["https://site.com/good.pdf"]
