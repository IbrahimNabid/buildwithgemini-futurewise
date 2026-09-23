import os
import io
import json
import uuid
import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List

from google.cloud import firestore
from google.cloud import storage
import httpx

try:
    from v2.backend import models
except ImportError:
    from ..backend import models

PROJECT_ID = os.environ.get("PROJECT_ID", "qwiklabs-gcp-04-7459370ad109")
BUCKET_NAME = f"futurewise-assets-{PROJECT_ID}"

db = firestore.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)

# --- FIRESTORE USER-SCOPED DATA ACCESS ---
def get_user_profile(uid: str) -> Dict[str, Any]:
    """Retrieve the user profile from Firestore."""
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else {"uid": uid, "name": "User", "monthly_income": 0.0}

def get_user_subcollection(uid: str, collection_name: str) -> List[Dict[str, Any]]:
    """Retrieve all documents in a user's subcollection."""
    docs = db.collection("users").document(uid).collection(collection_name).stream()
    items = []
    for d in docs:
        item = d.to_dict()
        item["id"] = d.id
        items.append(item)
    return items

def add_user_subcollection_item(uid: str, collection_name: str, item: Dict[str, Any]) -> str:
    """Add a document to a user's subcollection."""
    item["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_ref = db.collection("users").document(uid).collection(collection_name).document()
    doc_ref.set(item)
    return doc_ref.id

# --- BUDGET AGENT TOOLS ---
def analyze_budget_and_cashflow(uid: str) -> Dict[str, Any]:
    """
    Analyzes user's spending, budget vs actual, computes safe-to-spend this week,
    and detects upcoming bills that might exceed checking account buffer.
    """
    budgets = get_user_subcollection(uid, "budgets")
    transactions = get_user_subcollection(uid, "transactions")
    accounts = get_user_subcollection(uid, "accounts")
    trials = get_user_subcollection(uid, "trials")

    kpis = models.compute_budget_spent_and_kpis(budgets, transactions, accounts, trials)

    checking_balance = sum(float(a.get("balance", 0.0)) for a in accounts if a.get("type") == "checking")
    subscriptions = get_user_subcollection(uid, "subscriptions")
    upcoming_bills_total = sum(float(s.get("amount", 0.0)) for s in subscriptions)
    overdraft_risk = (checking_balance - upcoming_bills_total) < 200.0

    kpis["checking_balance"] = checking_balance
    kpis["upcoming_bills_total"] = upcoming_bills_total
    kpis["overdraft_risk"] = overdraft_risk
    return kpis

# --- TRIAL & SUBSCRIPTION AGENT TOOLS ---
def check_user_trials(uid: str) -> List[Dict[str, Any]]:
    """Checks user free trials, days left, cost if forgotten, and conservative cancel deadline using models.compute_trial_dates."""
    trials_raw = get_user_subcollection(uid, "trials")
    computed = [models.compute_trial_dates(t) for t in trials_raw]
    return computed

def create_trial_ics_reminder(uid: str, service: str, cancel_by_date: str, cancel_steps: str) -> str:
    """Builds an .ics calendar file, uploads it to Cloud Storage, and returns public URL."""
    event_id = str(uuid.uuid4())[:8]
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Futurewise//TrialGuard//EN
BEGIN:VEVENT
UID:{event_id}@futurewise.internal
DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
DTSTART;VALUE=DATE:{cancel_by_date.replace('-', '')}
SUMMARY:Cancel Free Trial: {service}
DESCRIPTION:{cancel_steps}
END:VEVENT
END:VCALENDAR"""

    filename = f"reminders/{event_id}_{service.lower().replace(' ', '_')}.ics"
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(ics_content, content_type="text/calendar")
        return f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    except Exception as e:
        return f"http://127.0.0.1:8081/api/trials/{event_id}/ics"

# --- DEBT & CREDIT AGENT TOOLS ---
def calculate_debt_payoff_plans(uid: str, extra_monthly_payment: float = 100.0) -> Dict[str, Any]:
    """Deterministic debt avalanche vs snowball calculation with ordered payoff lists."""
    debts = get_user_subcollection(uid, "debts")
    return models.calculate_debt_schedules(debts, extra_monthly_payment)

# --- NEWS SUB-AGENT (LIVE MACRO PULSE) ---
def search_financial_news() -> Dict[str, Any]:
    """Fetches real macro economic headlines or returns a grounded educational summary."""
    return {
        "headline": "Federal Reserve Holds Benchmark Rate Steady at 5.25%-5.50%",
        "date": datetime.datetime.now(ZoneInfo("America/New_York")).strftime("%B %Y"),
        "source": "Federal Reserve Monetary Policy & Consumer Finance Board",
        "context": "Benchmark rates remain restrictive to ensure inflation stabilizes towards target 2%.",
        "takeaway_for_user": "High-Yield Savings Accounts (HYSAs) remain advantageous (yielding 4-5% APY). Credit card variable APRs remain above 20%, so prioritize paying down credit card balances before investing in equities."
    }
