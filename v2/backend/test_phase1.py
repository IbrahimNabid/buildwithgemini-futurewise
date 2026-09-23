import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://127.0.0.1:8081"
HEADERS = {"Authorization": "Bearer demo-token-taylor_phase1"}

def run_tests():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Health
        res = client.get("/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("✓ Health check passed")

        # 2. Seed Demo Data
        res = client.post("/api/demo/seed", headers=HEADERS)
        assert res.status_code == 200, f"Seed failed: {res.text}"
        print("✓ Demo seed passed")

        # 3. Read Profile
        res = client.get("/api/profile", headers=HEADERS)
        assert res.status_code == 200, f"Get profile failed: {res.text}"
        profile = res.json()
        assert profile.get("name") == "Taylor Reynolds"
        print("✓ Profile read passed")

        # 4. Read Subcollections
        for col in ["accounts", "budgets", "sinking_funds", "trials", "subscriptions", "goals", "debts"]:
            res = client.get(f"/api/{col}", headers=HEADERS)
            assert res.status_code == 200, f"List {col} failed: {res.text}"
            items = res.json()
            assert len(items) > 0, f"Expected seeded items in {col}, got 0"
            print(f"✓ Subcollection {col} verified ({len(items)} items)")

        # 5. CRUD on goals
        res = client.post("/api/goals", headers=HEADERS, json={
            "title": "Down payment fund",
            "target_amount": 50000.0,
            "current_amount": 12000.0
        })
        assert res.status_code == 200, f"Create goal failed: {res.text}"
        new_goal = res.json()
        goal_id = new_goal["id"]
        print(f"✓ Create goal passed (id={goal_id})")

        res = client.put(f"/api/goals/{goal_id}", headers=HEADERS, json={
            "current_amount": 15000.0
        })
        assert res.status_code == 200, f"Update goal failed: {res.text}"
        assert res.json().get("current_amount") == 15000.0
        print("✓ Update goal passed")

        res = client.delete(f"/api/goals/{goal_id}", headers=HEADERS)
        assert res.status_code == 200, f"Delete goal failed: {res.text}"
        print("✓ Delete goal passed")

        # 6. Export JSON
        res = client.get("/api/settings/export?format=json", headers=HEADERS)
        assert res.status_code == 200, f"Export JSON failed: {res.text}"
        data = res.json()
        assert "profile" in data and "accounts" in data
        print("✓ Export JSON passed")

        # 7. Export CSV
        res = client.get("/api/settings/export?format=csv", headers=HEADERS)
        assert res.status_code == 200, f"Export CSV failed: {res.text}"
        assert "Section,Item_ID,Field,Value" in res.text
        print("✓ Export CSV passed")

        # 8. Delete Account
        res = client.delete("/api/settings/delete-account", headers=HEADERS)
        assert res.status_code == 200, f"Delete account failed: {res.text}"
        print("✓ Delete account passed")

        print("\nALL PHASE 1 BACKEND TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
