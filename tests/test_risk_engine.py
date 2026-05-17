from file_guard.models import RiskEvent
from file_guard.risk_engine import build_risk_event, calculate_risk_score, classify_risk_level


def test_classify_risk_level():
    assert classify_risk_level(10) == "LOW"
    assert classify_risk_level(30) == "MEDIUM"
    assert classify_risk_level(60) == "HIGH"
    assert classify_risk_level(80) == "CRITICAL"


def test_deleted_high_risk():
    change = {
        "event_type": "DELETED",
        "relative_path": "account_list.txt",
        "old_hash": "a",
        "new_hash": None,
        "old_size": 10,
        "new_size": None,
        "sensitivity": "HIGH",
        "extension": ".txt",
    }
    score, rules = calculate_risk_score(change)
    assert score >= 80
    assert any("DELETED" in rule for rule in rules)


def test_modified_high_sensitive_file():
    event = build_risk_event(
        {
            "event_type": "MODIFIED",
            "relative_path": "finance_report.txt",
            "old_hash": "a",
            "new_hash": "b",
            "old_size": 10,
            "new_size": 12,
            "sensitivity": "HIGH",
            "extension": ".txt",
        }
    )
    assert event.level in {"HIGH", "CRITICAL"}


def test_suspicious_ps1_high_risk():
    score, _ = calculate_risk_score(
        {
            "event_type": "SUSPICIOUS_EXTENSION",
            "relative_path": "suspicious.ps1",
            "old_hash": None,
            "new_hash": "b",
            "old_size": None,
            "new_size": 20,
            "sensitivity": "LOW",
            "extension": ".ps1",
        }
    )
    assert score >= 60


def test_build_risk_event_returns_riskevent():
    event = build_risk_event(
        {
            "event_type": "CREATED",
            "relative_path": "new.txt",
            "old_hash": None,
            "new_hash": "b",
            "old_size": None,
            "new_size": 20,
            "sensitivity": "LOW",
            "extension": ".txt",
        }
    )
    assert isinstance(event, RiskEvent)
    assert event.evidence
