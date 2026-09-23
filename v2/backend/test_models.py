import datetime
from v2.backend.models import compute_trial_dates, compute_budget_spent_and_kpis, calculate_debt_schedules

def test_trial_dates():
    today = datetime.date(2026, 9, 23)
    
    # App Store trial (7 days, starts Sep 20) -> end is Sep 27 -> cancel_by is Sep 25 (2 days before)
    app_store_trial = {
        "service": "Fitness App",
        "platform": "app_store",
        "start_date": "2026-09-20",
        "trial_days": 7,
        "price_after_trial": 59.99,
        "billing_cycle": "annual"
    }
    res = compute_trial_dates(app_store_trial, today)
    assert res["trial_end"] == "2026-09-27"
    assert res["cancel_by_date"] == "2026-09-25"
    assert res["days_to_cancel"] == 2
    assert res["annual_conversion_warning"] is True
    assert res["urgency"] == "critical"
    print("✓ App Store trial dates & 2-day buffer test passed")

    # Web trial (14 days, starts Sep 20) -> end is Oct 4 -> cancel_by is Oct 4
    web_trial = {
        "service": "Cloud Storage",
        "platform": "website",
        "start_date": "2026-09-20",
        "trial_days": 14,
        "price_after_trial": 9.99,
        "billing_cycle": "monthly"
    }
    res_web = compute_trial_dates(web_trial, today)
    assert res_web["trial_end"] == "2026-10-04"
    assert res_web["cancel_by_date"] == "2026-10-04"
    assert res_web["days_to_cancel"] == 11
    assert res_web["annual_conversion_warning"] is False
    print("✓ Web trial dates test passed")

def test_budgets_and_kpis():
    today = datetime.date(2026, 9, 23)
    budgets = [
        {"category": "Groceries", "allocated": 500.0},
        {"category": "Rent", "allocated": 2000.0}
    ]
    transactions = [
        {"date": "2026-09-05", "category": "Groceries", "amount": 150.0},
        {"date": "2026-09-12", "category": "Groceries", "amount": 120.0},
        {"date": "2026-09-15", "category": "Groceries", "amount": -20.0}, # refund
        {"date": "2026-08-20", "category": "Groceries", "amount": 300.0}, # past month, must be ignored
        {"date": "2026-09-01", "category": "Rent", "amount": 2000.0}
    ]
    accounts = [
        {"type": "checking", "balance": 1500.0},
        {"type": "savings", "balance": 7500.0}
    ]
    trials = [
        {"platform": "app_store", "start_date": "2026-09-20", "trial_days": 5, "price_after_trial": 10.0}
    ]

    res = compute_budget_spent_and_kpis(budgets, transactions, accounts, trials, today)
    # Groceries: 150 + 120 - 20 = 250
    g_budget = next(b for b in res["budgets"] if b["category"] == "Groceries")
    assert g_budget["spent"] == 250.0
    assert g_budget["remaining"] == 250.0
    
    # Rent: 2000
    r_budget = next(b for b in res["budgets"] if b["category"] == "Rent")
    assert r_budget["spent"] == 2000.0

    # Emergency months: savings (7500) / essential expenses (2500) = 3.0 months
    assert res["emergency_months"] == 3.0
    assert res["safe_to_spend_this_week"] > 0
    print("✓ Dynamic budget spent, refunds, and emergency fund months test passed")

def test_debt_payoff():
    debts = [
        {"name": "Card A", "balance": 1200.0, "apr": 24.0, "min_payment": 40.0},
        {"name": "Loan B", "balance": 5000.0, "apr": 5.0, "min_payment": 100.0}
    ]
    res = calculate_debt_schedules(debts, extra_monthly_payment=100.0)
    assert res["avalanche"]["payoff_order"][0] == "Card A" # highest APR first
    assert res["snowball"]["payoff_order"][0] == "Card A" # lowest balance first
    assert res["avalanche"]["total_interest"] <= res["snowball"]["total_interest"]
    print("✓ Debt payoff avalanche vs snowball test passed")

if __name__ == "__main__":
    test_trial_dates()
    test_budgets_and_kpis()
    test_debt_payoff()
    print("\nALL CALCULATION UNIT TESTS PASSED!")
