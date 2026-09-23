import pytest
from app.app_utils import firestore_db, firestore_tools

TEST_USER_ID = "taylor_nyc_27"


def test_firestore_client_project_id():
    client = firestore_db.get_firestore_client()
    assert client.project == "qwiklabs-gcp-04-7459370ad109"


def test_read_user_profile():
    res = firestore_tools.read_user_profile(TEST_USER_ID)
    assert "taylor_nyc_27" in res
    assert "annual_income" in res


def test_read_recent_transactions():
    res = firestore_tools.read_recent_transactions(TEST_USER_ID, limit=5)
    assert "Recent transactions" in res
    assert "MTA" in res or "TRADER JOE" in res or "PAYROLL" in res


def test_read_budgets():
    res = firestore_tools.read_user_budgets(TEST_USER_ID)
    assert "Rent" in res
    assert "Groceries" in res


def test_read_goals():
    res = firestore_tools.read_user_goals(TEST_USER_ID)
    assert "Emergency Fund" in res


def test_read_trials():
    res = firestore_tools.read_active_trials(TEST_USER_ID)
    assert "Calm" in res
    assert "Duolingo" in res


def test_read_account_limits():
    res = firestore_tools.read_account_limits(2025)
    assert "Tax Year 2025" in res
    assert "HSA" in res
    assert "IRA" in res


def test_read_life_events():
    res = firestore_tools.read_life_events(chapter=1)
    assert "Event [" in res


def test_read_user_simulation_games():
    res = firestore_tools.read_user_simulation_games(TEST_USER_ID)
    assert "game_chapter_1" in res
