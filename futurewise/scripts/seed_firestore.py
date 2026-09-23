"""Seed Firestore with synthetic data for Futurewise.

Hardcodes the GCP project ID as a string to avoid project number issues on Agent Platform.
Populates collections:
- users: fictional 27yo in NYC earning $68k
- users/{userId}/transactions: 60 transactions from bank export CSV
- users/{userId}/budgets: monthly budgets by category
- users/{userId}/goals: emergency fund and HSA goals
- users/{userId}/trials: 3 active trials from free_trials.json
- account_limits: contribution limits for 2024, 2025, 2026
- events: 15 scenario cards from life_events_deck.json
- users/{userId}/games: initial simulation game session
"""

import csv
import json
from pathlib import Path
from google.cloud import firestore

# Hardcoded project ID as string
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

USER_ID = "taylor_nyc_27"


def seed_all():
    print(f"Connecting to Firestore using project ID: {FIRESTORE_PROJECT_ID}...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    print("Connected successfully!")

    # 1. users: Profile for Taylor
    print("\n[1/8] Seeding users collection...")
    user_ref = db.collection("users").document(USER_ID)
    user_profile = {
        "user_id": USER_ID,
        "name": "Taylor",
        "age": 27,
        "location": "Crown Heights, Brooklyn, NYC",
        "annual_income": 68000.0,
        "pay_schedule": "Bi-weekly on alternating Fridays",
        "net_paycheck": 1982.40,
        "occupation": "Graphic Designer",
        "baseline_monthly_expenses": 3200.0,
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    user_ref.set(user_profile, merge=True)
    print(f"  ✓ Seeded profile for {USER_ID}")

    # 2. users/{userId}/transactions: Bank export CSV
    print("\n[2/8] Seeding transactions collection from CSV...")
    csv_path = DATA_DIR / "bank_transactions_nyc_27yo.csv"
    batch = db.batch()
    batch_count = 0
    total_txs = 0

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tx_id = row["Transaction ID"]
            amt = float(row["Amount"])
            doc_ref = user_ref.collection("transactions").document(tx_id)
            batch.set(
                doc_ref,
                {
                    "transaction_id": tx_id,
                    "date": row["Date"],
                    "description": row["Description"],
                    "category": row["Category"],
                    "amount": amt,
                    "type": row["Type"],
                    "running_balance": float(row["Running Balance"]),
                },
                merge=True,
            )
            batch_count += 1
            total_txs += 1
            if batch_count >= 400:
                batch.commit()
                batch = db.batch()
                batch_count = 0
    if batch_count > 0:
        batch.commit()
    print(f"  ✓ Seeded {total_txs} transactions for {USER_ID}")

    # 3. users/{userId}/budgets: Monthly category targets
    print("\n[3/8] Seeding budgets collection...")
    budgets = [
        {"category": "Rent", "monthly_limit": 1850.0},
        {"category": "Groceries", "monthly_limit": 450.0},
        {"category": "Dining", "monthly_limit": 300.0},
        {"category": "Transit", "monthly_limit": 135.0},
        {"category": "Subscriptions", "monthly_limit": 65.0},
        {"category": "Utilities", "monthly_limit": 90.0},
        {"category": "Health", "monthly_limit": 60.0},
    ]
    for b in budgets:
        doc_id = b["category"].lower()
        user_ref.collection("budgets").document(doc_id).set(b, merge=True)
    print(f"  ✓ Seeded {len(budgets)} category budgets for {USER_ID}")

    # 4. users/{userId}/goals: Financial goals
    print("\n[4/8] Seeding goals collection...")
    goals = [
        {
            "goal_id": "emergency_fund",
            "goal_name": "3-Month Emergency Fund",
            "target_amount": 9600.0,
            "current_amount": 3240.50,
            "target_date": "2027-03-31",
            "category": "Safety",
        },
        {
            "goal_id": "hsa_annual_max",
            "goal_name": "Annual HSA Contribution",
            "target_amount": 4450.0,
            "current_amount": 1600.0,
            "target_date": "2026-12-31",
            "category": "Healthcare",
        },
        {
            "goal_id": "roth_ira_max",
            "goal_name": "Max Out Roth IRA",
            "target_amount": 7500.0,
            "current_amount": 3000.0,
            "target_date": "2026-12-31",
            "category": "Retirement",
        },
    ]
    for g in goals:
        user_ref.collection("goals").document(g["goal_id"]).set(g, merge=True)
    print(f"  ✓ Seeded {len(goals)} financial goals for {USER_ID}")

    # 5. users/{userId}/trials: Free trials from free_trials.json
    print("\n[5/8] Seeding trials collection from free_trials.json...")
    trials_path = DATA_DIR / "free_trials.json"
    with open(trials_path, mode="r", encoding="utf-8") as f:
        trials = json.load(f)
    for t in trials:
        user_ref.collection("trials").document(t["id"]).set(t, merge=True)
    print(f"  ✓ Seeded {len(trials)} free trials for {USER_ID}")

    # 6. account_limits: Statutory limits for 2024, 2025, 2026
    print("\n[6/8] Seeding account_limits collection...")
    limits_path = DATA_DIR / "tax_contribution_limits.json"
    with open(limits_path, mode="r", encoding="utf-8") as f:
        limits = json.load(f)
    for lim in limits:
        tax_year = str(lim["tax_year"])
        db.collection("account_limits").document(tax_year).set(lim, merge=True)
    print(f"  ✓ Seeded {len(limits)} tax years into account_limits")

    # 7. events: Life events deck (15 scenario cards)
    print("\n[7/8] Seeding events collection from life_events_deck.json...")
    events_path = DATA_DIR / "life_events_deck.json"
    with open(events_path, mode="r", encoding="utf-8") as f:
        events = json.load(f)
    for evt in events:
        db.collection("events").document(evt["id"]).set(evt, merge=True)
    print(f"  ✓ Seeded {len(events)} life simulation events into events")

    # 8. users/{userId}/games: Simulation game session
    print("\n[8/8] Seeding games collection...")
    initial_game = {
        "game_id": "game_chapter_1",
        "current_chapter": 1,
        "net_worth": 12500.0,
        "cash_balance": 3240.50,
        "annual_salary": 68000.0,
        "status": "in_progress",
        "choices_made": [
            {
                "chapter": 1,
                "event_id": "evt_001_rent_hike",
                "choice": "B",
                "summary": "Negotiated 2-year lease at +$75/month saving $1,500/year compared to initial ask.",
            }
        ],
    }
    user_ref.collection("games").document("game_chapter_1").set(initial_game, merge=True)
    print(f"  ✓ Seeded initial game session in games collection for {USER_ID}")

    print("\n🎉 All 8 Firestore collections seeded successfully!")


if __name__ == "__main__":
    seed_all()
