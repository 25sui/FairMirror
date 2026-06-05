import os
import zipfile
from io import BytesIO

os.environ["DATABASE_URL"] = "sqlite:///./fairmirror_test.db"

from fastapi.testclient import TestClient

from app.data import demo as demo_data
from app.db.session import engine
from app.models.domain import Base
from app.main import app
from app.services.document_parser import extract_document_text
from app.services.rule_repository import rules_for, semantic_review_rules_for

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def _make_minimal_docx(text: str) -> bytes:
    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>
</w:document>'''
    payload = BytesIO()
    with zipfile.ZipFile(payload, "w") as docx:
        docx.writestr("[Content_Types].xml", "")
        docx.writestr("word/document.xml", document_xml)
    return payload.getvalue()


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_payload_includes_competition_sample_container():
    response = client.get("/api/v1/demo")
    assert response.status_code == 200
    body = response.json()
    assert body["jd"]
    assert body["resume"]
    assert body["interview_records"]
    assert body["competition_samples"]["source_file"] == "docs/AI大赛脱敏数据.xlsx"
    assert "jd_count" in body["competition_samples"]["stats"]
    assert "resume_count" in body["competition_samples"]["stats"]


def test_competition_sample_loader_falls_back_when_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(demo_data, "JD_SAMPLE_FILE", tmp_path / "missing-jd.json")
    monkeypatch.setattr(demo_data, "RESUME_SAMPLE_FILE", tmp_path / "missing-resume.json")
    samples = demo_data.competition_samples()
    assert samples["jd"] == []
    assert samples["resume"] == []
    assert samples["stats"] == {"jd_count": 0, "resume_count": 0}


def test_competition_jd_samples_trigger_expected_rule_audits():
    samples = {sample["sample_id"]: sample for sample in demo_data.competition_samples()["jd"]}
    expected_types = {
        "competition-jd-001": {"age", "education", "region", "workstyle"},
        "competition-jd-002": {"age", "education", "region", "identity"},
        "competition-jd-003": {"age", "education", "gender", "workstyle"},
    }
    assert expected_types.keys() <= samples.keys()

    for sample_id, required_types in expected_types.items():
        sample = samples[sample_id]
        response = client.post(
            "/api/v1/jd/audit",
            json={"title": sample["title"], "content": sample["content"], "role": "hr"},
        )
        assert response.status_code == 200
        body = response.json()
        finding_types = {item["type"] for item in body["findings"]}
        assert required_types <= finding_types
        assert body["risk_score"] > 65
        assert body["rewritten"] != sample["content"]


def test_document_extract_supports_text_upload():
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("jd.txt", "要求35岁以下，985/211优先。".encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "jd.txt"
    assert "35岁以下" in body["text"]
    assert body["characters"] > 0


def test_document_parser_cleans_markdown_text():
    text = extract_document_text("resume.md", "# 陈瑞\n![头像](photo.png)\n[邮箱](mailto:a@example.com)\n```python\nprint('skip')\n```".encode("utf-8"))
    assert "陈瑞" in text
    assert "邮箱" in text
    assert "print" not in text


def test_document_parser_extracts_docx_text_with_fallback():
    text = extract_document_text("resume.docx", _make_minimal_docx("辽宁工程技术大学 数据科学与大数据技术"))
    assert "辽宁工程技术大学" in text
    assert "数据科学" in text


def test_rule_repository_loads_configured_rules():
    assert any(rule["id"] == "jd-age-direct" for rule in rules_for("jd"))
    assert any(rule["id"] == "semantic-jd-age-proxy-energy" for rule in semantic_review_rules_for("jd"))


def test_jd_audit_detects_semantic_proxy_bias():
    response = client.post(
        "/api/v1/jd/audit",
        json={"title": "测试岗位", "content": "我们是年轻团队，希望候选人精力充沛，毕业不超过3年。", "role": "hr"},
    )
    assert response.status_code == 200
    body = response.json()
    assert any(item["type"] == "age" for item in body["findings"])
    assert any(item["source"] == "semantic_review" for item in body["findings"])
    assert body["risk_score"] > 50


def test_jd_audit_detects_age_bias():
    response = client.post(
        "/api/v1/jd/audit",
        json={"title": "测试岗位", "content": "要求35岁以下，985/211优先，抗压能力强。", "role": "hr"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_score"] > 50
    assert any(item["type"] == "age" for item in body["findings"])
    assert body["rewritten"] != "要求35岁以下，985/211优先，抗压能力强。"


def test_resume_audit_returns_ats_and_anonymized_version():
    response = client.post(
        "/api/v1/resume/audit",
        json={
            "candidate_name": "张敏",
            "target_role": "增长产品经理",
            "content": "张敏，女，河南籍，32岁，已婚已育。简历含个人照片。曾因家庭原因有2年职业空窗期。",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_score"] > 50
    assert len(body["ats_scores"]) >= 4
    assert "张敏" not in body["rewritten"]
    assert body["anonymity_tips"]


def test_custom_interview_audit_applies_four_fifths_rule():
    response = client.post(
        "/api/v1/interview/audit",
        json={
            "batch_name": "测试批次",
            "records": [
                {"candidate_id": "A1", "group": "多数群体", "score": 90, "passed": True, "question_depth": 4},
                {"candidate_id": "A2", "group": "多数群体", "score": 82, "passed": True, "question_depth": 4},
                {"candidate_id": "B1", "group": "保护群体", "score": 70, "passed": False, "question_depth": 1},
                {"candidate_id": "B2", "group": "保护群体", "score": 68, "passed": False, "question_depth": 1},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["four_fifths_rule"] is False
    assert body["risk_level"] == "high"
    metric_codes = {item["code"] for item in body["fairness_metrics"]}
    assert "selection_rate" in metric_codes
    assert "demographic_parity_difference" in metric_codes
    assert body["calculation_notes"]


def test_interview_demo_has_fairness_metrics():
    response = client.get("/api/v1/interview/demo")
    assert response.status_code == 200
    body = response.json()
    assert "disparate_impact_ratio" in body
    assert len(body["metrics"]) >= 3


def test_model_audit_returns_model_source_and_attribution():
    response = client.post(
        "/api/v1/ai/model-audit",
        json={"scenario": "jd", "content": "年轻团队，要求35岁以下，985/211优先。"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["runtime_mode"] in {"transformers", "local_surrogate"}
    assert body["risk_score"] > 50
    assert any(item["source"] == "model" for item in body["findings"])
    assert any(item["token"] == "35岁以下" for item in body["token_contributions"])


def test_debiasing_demo_improves_fairness_metrics():
    response = client.get("/api/v1/ai/debiasing-demo")
    assert response.status_code == 200
    body = response.json()
    assert body["debiased"]["disparate_impact_ratio"] >= body["baseline"]["disparate_impact_ratio"]
    assert body["debiased"]["selection_rate_gap"] <= body["baseline"]["selection_rate_gap"]
    assert body["training_trace"]


def test_roles_cover_four_personas():
    response = client.get("/api/v1/roles")
    assert response.status_code == 200
    roles = {item["role"] for item in response.json()}
    assert roles == {"enterprise_admin", "hr", "candidate", "auditor"}


def test_report_summary_has_full_chain_coverage():
    response = client.get("/api/v1/reports/summary")
    assert response.status_code == 200
    body = response.json()
    assert "JD 智能审计" in body["coverage"]
    assert "AI 面试公平监控" in body["coverage"]
    assert body["key_findings"]


def test_dashboard_and_jobs_use_persisted_audit_records():
    before = client.get("/api/v1/dashboard/summary").json()["audits_completed"]
    audit_response = client.post(
        "/api/v1/jd/audit",
        json={"title": "持久化测试岗位", "content": "要求35岁以下，本地户籍优先。", "role": "hr"},
    )
    assert audit_response.status_code == 200
    audit_id = audit_response.json()["audit_id"]

    dashboard = client.get("/api/v1/dashboard/summary").json()
    assert dashboard["audits_completed"] == before + 1
    assert dashboard["open_risks"] >= 1

    jobs = client.get("/api/v1/audit-jobs").json()
    assert jobs[0]["audit_id"] == audit_id
    assert jobs[0]["title"] == "持久化测试岗位 JD 审计"
