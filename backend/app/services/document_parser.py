from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv", ".docx", ".pdf"}


def extract_document_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("仅支持 .txt、.md、.csv、.docx、.pdf 文件")

    if extension in {".txt", ".md", ".csv"}:
        return _decode_text(content)
    if extension == ".docx":
        return _extract_docx_text(content)
    return _extract_pdf_text(content)


def _decode_text(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            text = content.decode(encoding)
            return _normalize_text(text)
        except UnicodeDecodeError:
            continue
    return _normalize_text(content.decode("utf-8", errors="ignore"))


def _extract_docx_text(content: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(content)) as docx:
            xml = docx.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise ValueError("无法解析 docx 文件内容") from exc

    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace))
        if text.strip():
            paragraphs.append(text)
    return _normalize_text("\n".join(paragraphs))


def _extract_pdf_text(content: bytes) -> str:
    raw = content.decode("latin-1", errors="ignore")
    candidates = re.findall(r"\(([^()]{2,})\)", raw)
    text = "\n".join(item.replace("\\)", ")").replace("\\(", "(") for item in candidates)
    text = _normalize_text(text)
    if text:
        return text

    fallback = _normalize_text(re.sub(r"[^\x20-\x7E\u4e00-\u9fff]+", " ", raw))
    if len(fallback) < 20:
        raise ValueError("无法从 PDF 中提取可审计文本，建议上传可复制文本的 PDF 或 txt 文件")
    return fallback


def _normalize_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n").replace("\r", "\n")).strip()