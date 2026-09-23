from v2.agents import tools

def test_tools():
    uid = "demo_test_user"
    # Seed some sample data for demo_test_user
    tools.db.collection("users").document(uid).collection("budgets").document("rent").set({
        "category": "Rent", "allocated": 2000.0, "spent": 2000.0
    })
    tools.db.collection("users").document(uid).collection("budgets").document("groceries").set({
        "category": "Groceries", "allocated": 500.0, "spent": 300.0
    })
    tools.db.collection("users").document(uid).collection("trials").document("trial1").set({
        "service": "MusicApp", "platform": "app_store", "days_left": 2, "cost_if_forgotten": 49.99, "cancel_by_date": "2026-09-25"
    })
    tools.db.collection("users").document(uid).collection("debts").document("card1").set({
        "name": "Card A", "balance": 1000.0, "apr": 20.0, "min_payment": 50.0
    })

    # Test budget analysis
    budget_res = tools.analyze_budget_and_cashflow(uid)
    assert budget_res["total_allocated"] == 2500.0
    assert budget_res["total_spent"] == 2300.0
    print("✓ Budget tool verified:", budget_res)

    # Test trials
    trial_res = tools.check_user_trials(uid)
    assert len(trial_res) >= 1
    assert trial_res[0]["urgency"] == "critical"
    print("✓ Trials tool verified:", trial_res)

    # Test debt payoff
    debt_res = tools.calculate_debt_payoff_plans(uid, extra_monthly_payment=50.0)
    assert "avalanche" in debt_res and "snowball" in debt_res
    print("✓ Debt payoff tool verified:", debt_res)

    # Test news
    news_res = tools.search_financial_news()
    assert "headline" in news_res
    print("✓ News tool verified:", news_res)

    # Test sandbox calc
    sb_res = tools.run_financial_sandbox_calc("emergency_fund_runway", {"cash": 6000.0, "monthly_expenses": 2000.0})
    assert sb_res["runway_months"] == 3.0
    print("✓ Sandbox calc verified:", sb_res)

    print("\nALL V2 AGENT TOOLS VERIFIED DETERMINISTICALLY!")

if __name__ == "__main__":
    test_tools()
