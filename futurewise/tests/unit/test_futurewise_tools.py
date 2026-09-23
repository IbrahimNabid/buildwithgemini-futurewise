import pytest
from app.app_utils import futurewise_tools

TEST_USER_ID = "taylor_nyc_27"


def test_add_and_check_trials():
    # Test add_trial
    msg = futurewise_tools.add_trial(
        service="TestFitnessPro",
        platform="app_store",
        start_date="2026-09-20",
        trial_days=7,
        price_after_trial=29.99,
        billing_cycle="monthly",
        user_id=TEST_USER_ID,
    )
    assert "Trial for 'TestFitnessPro' (app_store) added" in msg
    assert "2026-09-27" in msg

    # Test check_trials
    summary = futurewise_tools.check_trials(user_id=TEST_USER_ID)
    assert "Active Trial Guard Status:" in summary
    assert "TestFitnessPro" in summary
    # App Store rule: cancel 2 days before
    assert "Cancel 2 days before end" in summary
    assert "2026-09-25" in summary  # 2026-09-27 minus 2 days


def test_create_trial_reminder():
    res = futurewise_tools.create_trial_reminder(
        service="TestFitnessPro",
        cancel_date="2026-09-25",
        cancel_steps="Settings -> Apple ID -> Subscriptions -> Cancel",
        price_after_trial="$29.99/month",
    )
    assert "Calendar reminder created for TestFitnessPro" in res
    assert "https://storage.googleapis.com/futurewise-assets-qwiklabs-gcp-04-7459370ad109/reminders/" in res
    assert res.endswith(".ics")


def test_log_expense_and_spending_summary():
    # Log an expense
    log_res = futurewise_tools.log_expense(
        description="Organic Apples & Almond Milk",
        category="Groceries",
        amount=14.50,
        user_id=TEST_USER_ID,
    )
    assert "Logged expense of $14.50" in log_res
    assert "Groceries" in log_res

    # Check spending summary
    summary = futurewise_tools.get_spending_summary(user_id=TEST_USER_ID, limit=10)
    assert "Spending Summary for taylor_nyc_27" in summary
    assert "Total Outflow:" in summary
    assert "Groceries:" in summary


def test_search_agent_tool():
    # Verify search_agent_tool is properly configured
    assert futurewise_tools.search_agent_tool is not None
    assert futurewise_tools.search_sub_agent.name == "search_sub_agent"
    assert len(futurewise_tools.search_sub_agent.tools) == 1
