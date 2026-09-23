import requests
import datetime

BASE_URL = "http://127.0.0.1:8081"
HEADERS = {"Authorization": "Bearer demo-token-taylor_27"}

def test_full_user_journey():
    # 1. Health check
    res = requests.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # 2. Seed demo data idempotently
    res = requests.post(f"{BASE_URL}/api/demo/seed", headers=HEADERS)
    assert res.status_code == 200
    assert res.json()["status"] == "seeded"

    # 3. Verify Overview computed KPIs
    res = requests.get(f"{BASE_URL}/api/dashboard/overview", headers=HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["safe_to_spend_this_week"] > 0
    assert data["budget_used_percent"] > 0
    assert data["emergency_months"] >= 2.0
    assert len(data["computed_trials"]) == 3

    # 4. Verify App Store 2-day buffer in trials
    res = requests.get(f"{BASE_URL}/api/trials/computed", headers=HEADERS)
    assert res.status_code == 200
    trials = res.json()
    app_store_t = next(t for t in trials if t["platform"] == "app_store")
    # days_to_cancel must equal days_left - 2
    assert app_store_t["days_to_cancel"] == app_store_t["days_left"] - 2
    assert app_store_t["annual_conversion_warning"] is True

    # 5. Debt Payoff Planner
    res = requests.get(f"{BASE_URL}/api/debts/payoff-schedule?extra_monthly=150", headers=HEADERS)
    assert res.status_code == 200
    debts = res.json()
    assert debts["avalanche"]["months_to_debt_free"] > 0
    assert debts["snowball"]["months_to_debt_free"] > 0
    assert debts["avalanche"]["total_interest"] <= debts["snowball"]["total_interest"]

    # 6. Complete Quiz
    res = requests.post(f"{BASE_URL}/api/learn/lessons/hysa-vs-checking/quiz", headers=HEADERS, json={"answers": [0, 1, 0]})
    assert res.status_code == 200
    assert "score" in res.json()

    # 7. Life Mode Game: Start, Choice, Rewind
    res = requests.post(f"{BASE_URL}/api/game/start", headers=HEADERS, json={"difficulty": "Normal"})
    assert res.status_code == 200
    assert res.json()["game_state"]["current_chapter"] == 1

    res = requests.post(f"{BASE_URL}/api/game/choice", headers=HEADERS, json={"choice_id": "fund_emergency"})
    assert res.status_code == 200
    assert res.json()["game_state"]["current_chapter"] == 2
    assert res.json()["game_state"]["stats"]["cash"] == 11190.0

    res = requests.post(f"{BASE_URL}/api/game/rewind", headers=HEADERS, json={"target_chapter": 1})
    assert res.status_code == 200
    assert res.json()["game_state"]["current_chapter"] == 1
    assert res.json()["game_state"]["stats"]["cash"] == 7190.0

    # 8. Autopilot Run
    res = requests.post(f"{BASE_URL}/api/autopilot/run-now", headers=HEADERS)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # 9. AI Assistant Real Chat
    res = requests.post(f"{BASE_URL}/api/assistant/chat", headers=HEADERS, json={"prompt": "Which of my free trials should I cancel?", "page": "trials"})
    assert res.status_code == 200
    assert "Trial Guard Alert" in res.json()["reply"]

    # 10. Data Export
    res = requests.get(f"{BASE_URL}/api/settings/export?format=json", headers=HEADERS)
    assert res.status_code == 200
    export_json = res.json()
    assert "accounts" in export_json
    assert "budgets" in export_json
    assert len(export_json["transactions"]) >= 60

    print("\nALL END-TO-END FLOW TESTS PASSED!")

if __name__ == "__main__":
    test_full_user_journey()
