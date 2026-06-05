import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
JD_SAMPLE_FILE = ROOT / "demo-data" / "fairmirror-jd-samples.json"
RESUME_SAMPLE_FILE = ROOT / "demo-data" / "fairmirror-resume-samples.json"
STATS_SAMPLE_FILE = ROOT / "demo-data" / "fairmirror-competition-sample-stats.json"


SAMPLE_JD = """高级增长产品经理
岗位要求：35岁以下，985/211本科及以上，抗压能力强，能长期高强度加班和频繁出差。候选人需要有狼性、执行力强，优先考虑本地户籍，有大厂背景者优先。
"""

SAMPLE_RESUME = """张敏，女，河南籍，32岁，已婚已育。2014年毕业于普通本科，曾因家庭原因有2年职业空窗期。熟悉用户研究、数据分析、A/B测试，主导过会员增长项目，转化率提升18%。简历含个人照片。
"""

SAMPLE_INTERVIEW_RECORDS = [
    {"candidate_id": "C001", "group": "男性", "score": 86, "passed": True, "question_depth": 5},
    {"candidate_id": "C002", "group": "男性", "score": 79, "passed": True, "question_depth": 4},
    {"candidate_id": "C003", "group": "男性", "score": 74, "passed": True, "question_depth": 4},
    {"candidate_id": "C004", "group": "女性", "score": 81, "passed": True, "question_depth": 3},
    {"candidate_id": "C005", "group": "女性", "score": 72, "passed": False, "question_depth": 2},
    {"candidate_id": "C006", "group": "女性", "score": 69, "passed": False, "question_depth": 2},
    {"candidate_id": "C007", "group": "35岁以上", "score": 75, "passed": False, "question_depth": 2},
    {"candidate_id": "C008", "group": "35岁以上", "score": 68, "passed": False, "question_depth": 1},
]


def _load_json_samples(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _load_json_object(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def competition_samples() -> Dict[str, Any]:
    jd_samples = _load_json_samples(JD_SAMPLE_FILE)
    resume_samples = _load_json_samples(RESUME_SAMPLE_FILE)
    sample_stats = _load_json_object(STATS_SAMPLE_FILE) if jd_samples or resume_samples else {}
    sample_counts = sample_stats.get("sample_counts") if isinstance(sample_stats.get("sample_counts"), dict) else {}
    stats = {"jd_count": len(jd_samples), "resume_count": len(resume_samples)}
    if jd_samples or resume_samples:
        stats = {
            **stats,
            "total": len(jd_samples) + len(resume_samples),
            "source_file": sample_stats.get("source_file", "docs/AI大赛脱敏数据.xlsx"),
            "derived_files": sample_stats.get("derived_files", {}),
            "sample_counts": sample_counts,
        }
    return {
        "source_file": "docs/AI大赛脱敏数据.xlsx",
        "derived_files": {
            "jd": "demo-data/fairmirror-jd-samples.json",
            "resume": "demo-data/fairmirror-resume-samples.json",
            "stats": "demo-data/fairmirror-competition-sample-stats.json",
        },
        "jd": jd_samples,
        "resume": resume_samples,
        "stats": stats,
        "risk_tag_distribution": {
            "jd": sample_stats.get("jd_risk_tag_distribution", {}),
            "resume": sample_stats.get("resume_risk_tag_distribution", {}),
        },
        "evidence_summary": sample_stats.get("evidence_summary", []),
    }