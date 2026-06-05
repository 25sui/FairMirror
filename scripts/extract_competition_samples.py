from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any, Dict, List
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE_XLSX = ROOT / "docs" / "AI大赛脱敏数据.xlsx"
JD_OUTPUT = ROOT / "demo-data" / "fairmirror-jd-samples.json"
RESUME_OUTPUT = ROOT / "demo-data" / "fairmirror-resume-samples.json"

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _text_of(element: ET.Element) -> str:
    return "".join(element.itertext()).strip()


def _load_shared_strings(book: zipfile.ZipFile) -> List[str]:
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    values: List[str] = []
    for item in root.findall("s:si", NS):
        values.append(_text_of(item))
    return values


def _column_name(cell_ref: str) -> str:
    return re.sub(r"\d+", "", cell_ref)


def _cell_value(cell: ET.Element, shared_strings: List[str]) -> str:
    value = cell.find("s:v", NS)
    if value is None or value.text is None:
        return ""
    raw = value.text.strip()
    if cell.attrib.get("t") == "s" and raw.isdigit():
        index = int(raw)
        if 0 <= index < len(shared_strings):
            return shared_strings[index]
    return raw


def _sheet_rows(book: zipfile.ZipFile, sheet_file: str, shared_strings: List[str]) -> List[Dict[str, str]]:
    root = ET.fromstring(book.read(f"xl/worksheets/{sheet_file}"))
    rows: List[Dict[str, str]] = []
    for row in root.findall(".//s:sheetData/s:row", NS):
        values: Dict[str, str] = {}
        for cell in row.findall("s:c", NS):
            ref = cell.attrib.get("r", "")
            if not ref:
                continue
            value = _cell_value(cell, shared_strings).strip()
            if value:
                values[_column_name(ref)] = value
        if values:
            rows.append(values)
    return rows


def _rows_as_records(rows: List[Dict[str, str]], required_header: str) -> List[Dict[str, str]]:
    header_index = -1
    header_row: Dict[str, str] = {}
    for index, row in enumerate(rows):
        if required_header in row.values():
            header_index = index
            header_row = row
            break
    if header_index < 0:
        return []

    records: List[Dict[str, str]] = []
    for row in rows[header_index + 1 :]:
        record = {header.strip(): row.get(column, "").strip() for column, header in header_row.items() if header.strip()}
        if any(record.values()):
            records.append(record)
    return records


def _compact(text: str) -> str:
    return re.sub(r"[ \t\u00a0]+", " ", text).strip()


def _risk_tags(text: str) -> List[str]:
    checks = {
        "age": r"\d{2}\s*[岁周]\s*(?:-|一|至|到)?\s*\d{0,2}\s*岁?|\d{2}\s*周岁|年轻|应届|毕业生",
        "education": r"985|211|双一流|本科|大专|中专|学历|党员",
        "region": r"本地|户籍|籍贯|周边居住|现居|城市",
        "gender_marriage": r"男士|女士|男性|女性|已婚|未婚|婚育",
        "workstyle": r"吃苦耐劳|抗压|加班|非诚勿扰|长期|稳定",
    }
    tags = [name for name, pattern in checks.items() if re.search(pattern, text, flags=re.IGNORECASE)]
    return tags


def _build_jd_content(record: Dict[str, str]) -> str:
    parts = [
        record.get("职位名称", ""),
        f"职类：{record.get('职类名称', '')}",
        f"薪资：{record.get('薪资', '')}",
        f"年限要求：{record.get('年限要求', '')}",
        f"学历要求：{record.get('学历要求', '')}",
        f"城市要求：{record.get('城市要求', '')}",
        f"职位关键词：{record.get('职位关键词', '')}",
        record.get("职位描述", ""),
    ]
    return "\n".join(_compact(part) for part in parts if _compact(part))


def _jd_samples(records: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        content = _build_jd_content(record)
        if not content:
            continue
        samples.append(
            {
                "sample_id": f"competition-jd-{index:03d}",
                "title": record.get("职位名称") or f"比赛脱敏岗位 {index}",
                "job_family": record.get("职类名称", ""),
                "city": record.get("城市要求", ""),
                "salary": record.get("薪资", ""),
                "education": record.get("学历要求", ""),
                "years": record.get("年限要求", ""),
                "company": record.get("公司名称", ""),
                "source": "AI大赛脱敏数据.xlsx/JD部分",
                "risk_tags": _risk_tags(content),
                "content": content,
            }
        )
    return samples


def _build_resume_content(record: Dict[str, str]) -> str:
    fields = [
        ("姓名", record.get("姓名", "")),
        ("性别", record.get("性别", "")),
        ("求职状态", record.get("求职状态", "")),
        ("年龄", record.get("年龄", "")),
        ("工作年限", record.get("工作年限", "")),
        ("最高学历", record.get("最高学历", "")),
        ("现居地址", record.get("现居地址", "")),
        ("求职期望", record.get("求职期望", "")),
        ("工作/实习经历", record.get("工作/实习经历", "")),
        ("项目经历", record.get("项目经历", "")),
        ("教育经历", record.get("教育经历", "")),
        ("个人优势", record.get("个人优势", "")),
        ("资格证书", record.get("资格证书", "")),
    ]
    return "\n".join(f"{name}：{_compact(value)}" for name, value in fields if _compact(value))


def _target_role(record: Dict[str, str]) -> str:
    expectation = record.get("求职期望", "")
    match = re.search(r'"期望职类"\s*:\s*"([^"]+)"', expectation)
    if match:
        return match.group(1)
    return "目标岗位"


def _resume_samples(records: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        content = _build_resume_content(record)
        if not content:
            continue
        candidate_name = record.get("姓名") or f"候选人{index}"
        samples.append(
            {
                "sample_id": f"competition-resume-{index:03d}",
                "candidate_name": candidate_name,
                "quality_label": record.get("简历质量", ""),
                "target_role": _target_role(record),
                "gender": record.get("性别", ""),
                "age": record.get("年龄", ""),
                "education": record.get("最高学历", ""),
                "city": record.get("现居地址", ""),
                "work_years": record.get("工作年限", ""),
                "source": "AI大赛脱敏数据.xlsx/CV部分",
                "risk_tags": _risk_tags(content),
                "content": content,
            }
        )
    return samples


def main() -> None:
    with zipfile.ZipFile(SOURCE_XLSX) as book:
        shared_strings = _load_shared_strings(book)
        jd_rows = _sheet_rows(book, "sheet1.xml", shared_strings)
        resume_rows = _sheet_rows(book, "sheet2.xml", shared_strings)

    jd_records = _rows_as_records(jd_rows, "职位名称")
    resume_records = _rows_as_records(resume_rows, "简历质量")

    jd_samples = _jd_samples(jd_records)
    resume_samples = _resume_samples(resume_records)

    JD_OUTPUT.write_text(json.dumps(jd_samples, ensure_ascii=False, indent=2), encoding="utf-8")
    RESUME_OUTPUT.write_text(json.dumps(resume_samples, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"jd_samples": len(jd_samples), "resume_samples": len(resume_samples)}, ensure_ascii=False))


if __name__ == "__main__":
    main()