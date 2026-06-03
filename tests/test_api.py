from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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


def test_interview_demo_has_fairness_metrics():
    response = client.get("/api/v1/interview/demo")
    assert response.status_code == 200
    body = response.json()
    assert "disparate_impact_ratio" in body
    assert len(body["metrics"]) >= 3


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
