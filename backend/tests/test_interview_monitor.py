import asyncio

from app.models.schemas import InterviewAnalysisRequest, InterviewRecordBase
from app.services.interview_monitor import interview_monitor


def test_interview_monitor_detects_disparate_impact():
    request = InterviewAnalysisRequest(
        interview_data=[
            InterviewRecordBase(candidate_id=1, job_id=1, scores={"tech": 5, "comm": 5}, demographic_group="A"),
            InterviewRecordBase(candidate_id=2, job_id=1, scores={"tech": 1, "comm": 1}, demographic_group="B"),
        ]
    )

    response = asyncio.run(interview_monitor.analyze_interviews(request))

    assert response.fairness_metrics.four_fifths_rule_passed is False
    assert response.fairness_metrics.disparate_impact_ratio < 0.8