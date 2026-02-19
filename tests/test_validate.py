from app.services.validate import _score


def test_score_zero_when_no_hit():
    assert _score("hello", ["주택"], 25) == 0


def test_score_caps_at_max():
    text = "주택 재개발 재건축 상권 택지"
    assert _score(text, ["주택", "재개발", "재건축", "상권", "택지"], 25) == 25
