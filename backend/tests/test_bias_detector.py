from app.services.bias_detector import bias_detector


def test_jd_bias_detector_finds_multiple_bias_types():
    results = bias_detector.detect_bias_rules("招聘男性工程师，35岁以下，985优先")
    bias_types = {item.type.value for item in results}

    assert "gender" in bias_types
    assert "age" in bias_types
    assert "education" in bias_types


def test_jd_bias_detector_accepts_neutral_text():
    results = bias_detector.detect_bias_rules("负责平台后端开发，熟悉 Python 和数据库设计")

    assert results == []