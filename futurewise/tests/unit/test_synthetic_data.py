import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def test_bank_transactions_csv():
    csv_path = DATA_DIR / "bank_transactions_nyc_27yo.csv"
    assert csv_path.exists(), f"CSV not found at {csv_path}"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) >= 50, f"Expected at least 50 transactions, got {len(reader)}"
    categories = {row["Category"] for row in reader}
    assert "Rent" in categories
    assert "Groceries" in categories
    assert "Dining" in categories
    assert "Transit" in categories
    assert "Subscriptions" in categories
    assert "Income" in categories


def test_free_trials_json():
    json_path = DATA_DIR / "free_trials.json"
    assert json_path.exists()
    with open(json_path, mode="r", encoding="utf-8") as f:
        trials = json.load(f)
    assert len(trials) == 3
    platforms = {t["platform"] for t in trials}
    assert platforms == {"App Store", "Google Play", "Website"}
    days = {t["days_remaining"] for t in trials}
    assert days == {2, 5, 12}
    for t in trials:
        assert "price_after_trial" in t
        assert "cancellation_steps" in t


def test_life_events_deck_json():
    json_path = DATA_DIR / "life_events_deck.json"
    assert json_path.exists()
    with open(json_path, mode="r", encoding="utf-8") as f:
        deck = json.load(f)
    assert len(deck) == 15
    for event in deck:
        assert "id" in event
        assert "title" in event
        assert "options" in event
        assert 2 <= len(event["options"]) <= 3
        for opt in event["options"]:
            assert "financial_effects" in opt
            assert "monthly_cash_flow_delta" in opt["financial_effects"]


def test_tax_contribution_limits_json():
    json_path = DATA_DIR / "tax_contribution_limits.json"
    assert json_path.exists()
    with open(json_path, mode="r", encoding="utf-8") as f:
        limits = json.load(f)
    assert len(limits) >= 3
    for entry in limits:
        assert "tax_year" in entry
        assert "ira" in entry
        assert "hsa" in entry
        assert "healthcare_fsa" in entry
        assert "dependent_care_fsa" in entry


def test_learn_lessons_metadata_json():
    json_path = DATA_DIR / "learn_lessons_metadata.json"
    assert json_path.exists()
    with open(json_path, mode="r", encoding="utf-8") as f:
        lessons = json.load(f)
    assert len(lessons) >= 10
    for lesson in lessons:
        assert "topic_id" in lesson
        assert "title" in lesson
        assert "summary" in lesson
        assert "key_takeaways" in lesson
        assert "grounding_source" in lesson
        assert "interactive_calculator_type" in lesson
