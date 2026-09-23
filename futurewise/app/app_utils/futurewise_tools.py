"""Minimal implementations for:
1. TRIAL GUARD: add_trial, check_trials
2. CALENDAR REMINDER: create_trial_reminder
3. SEARCH SUB-AGENT: search_sub_agent wrapped as AgentTool
4. EXPENSES: log_expense, get_spending_summary
"""

import datetime
import secrets
from typing import Any, Dict, List, Optional
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.cloud import storage
from google.genai import types

from app.app_utils import firestore_db

# Hardcoded project configuration
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"
GCS_ASSETS_BUCKET = "futurewise-assets-qwiklabs-gcp-04-7459370ad109"
DEFAULT_USER_ID = "taylor_nyc_27"

# -----------------------------------------------------------------------------
# 1. TRIAL GUARD
# -----------------------------------------------------------------------------
PLATFORM_DEFAULT_RULES = {
    "app_store": {
        "rule": "cancel_2_days_before",
        "description": "App Store trials may terminate access immediately upon cancellation. Cancel 2 days before renewal.",
        "steps": [
            "Open iOS Settings -> Tap your Apple ID banner",
            "Tap Subscriptions -> Select the app",
            "Tap Cancel Free Trial and confirm",
        ],
    },
    "google_play": {
        "rule": "safe_now",
        "description": "Google Play preserves access until the end of the trial period even if cancelled early.",
        "steps": [
            "Open Google Play Store -> Profile icon",
            "Payments & subscriptions -> Subscriptions",
            "Select app -> Cancel subscription",
        ],
    },
    "website": {
        "rule": "cancel_2_days_before",
        "description": "Web cancellation policies vary widely and can terminate access immediately. Cancel 2 days before.",
        "steps": [
            "Sign in to the provider's website account settings",
            "Navigate to Billing / Manage Subscription",
            "Click Cancel or contact customer support",
        ],
    },
}


def _ensure_platform_rules():
    """Stores default platform rules in Firestore if not already present."""
    db = firestore_db.get_firestore_client()
    for platform, data in PLATFORM_DEFAULT_RULES.items():
        doc_ref = db.collection("platform_rules").document(platform)
        doc_ref.set(data, merge=True)


def add_trial(
    service: str,
    platform: str,
    start_date: str,
    trial_days: int,
    price_after_trial: float,
    billing_cycle: str = "monthly",
    user_id: str = DEFAULT_USER_ID,
) -> str:
    """Adds a free trial to the user's Trial Guard tracker.

    Args:
        service: Name of the service/app (e.g. 'Spotify', 'Calm').
        platform: Platform type: 'app_store', 'google_play', or 'website'.
        start_date: Start date of trial in YYYY-MM-DD format.
        trial_days: Duration of the free trial in days.
        price_after_trial: Dollar price charged if trial renews (e.g. 14.99).
        billing_cycle: 'monthly' or 'annual'.
        user_id: Unique user identifier (defaults to 'taylor_nyc_27').

    Returns:
        Confirmation message with trial end date.
    """
    _ensure_platform_rules()
    db = firestore_db.get_firestore_client()
    plat_key = platform.lower().replace(" ", "_")
    
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = start_dt + datetime.timedelta(days=trial_days)
    end_date_str = end_dt.strftime("%Y-%m-%d")

    trial_id = service.lower().replace(" ", "_").replace("-", "_")
    doc_ref = db.collection("users").document(user_id).collection("trials").document(trial_id)
    doc_ref.set({
        "id": trial_id,
        "service_name": service,
        "platform": plat_key,
        "start_date": start_date,
        "trial_days": trial_days,
        "trial_end_date": end_date_str,
        "price_after_trial": price_after_trial,
        "billing_cycle": billing_cycle,
    }, merge=True)

    return f"Trial for '{service}' ({plat_key}) added. Trial ends on {end_date_str}."


def check_trials(user_id: str = DEFAULT_USER_ID) -> str:
    """Checks all tracked trials for a user and calculates cancel dates, costs, safety, and steps.

    Args:
        user_id: Unique user identifier (defaults to 'taylor_nyc_27').

    Returns:
        Structured summary for each active trial.
    """
    _ensure_platform_rules()
    db = firestore_db.get_firestore_client()
    trials_ref = db.collection("users").document(user_id).collection("trials").stream()
    
    today = datetime.date(2026, 9, 22)  # Current app reference date
    results = []

    for doc in trials_ref:
        data = doc.to_dict()
        service = data.get("service_name", doc.id)
        platform = data.get("platform", "website").lower().replace(" ", "_")
        end_date_str = data.get("trial_end_date")
        if not end_date_str:
            continue
        
        end_dt = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        days_left = (end_dt - today).days

        price = data.get("price_after_trial", 0.0)
        cycle = data.get("billing_cycle", "monthly")
        
        # Calculate cost if forgotten
        if isinstance(price, (int, float)):
            price_val = float(price)
            annual_cost = price_val if cycle == "annual" else price_val * 12
            cost_str = f"${price_val:.2f}/{cycle} (${annual_cost:.2f}/year)"
        else:
            cost_str = str(price)

        # Platform rules from Firestore or fallback
        rule_doc = db.collection("platform_rules").document(platform).get()
        if rule_doc.exists:
            rule_data = rule_doc.to_dict()
        else:
            rule_data = PLATFORM_DEFAULT_RULES.get(platform, PLATFORM_DEFAULT_RULES["website"])

        rule_type = rule_data.get("rule", "cancel_2_days_before")
        steps = rule_data.get("steps", [])

        # App Store or unknown -> conservative rule: cancel at least 2 days before
        if platform == "app_store" or rule_type != "safe_now":
            safety = "Cancel 2 days before end (canceling immediately may terminate access)"
            rec_cancel_dt = end_dt - datetime.timedelta(days=2)
        else:
            safety = "Safe to cancel now (benefits preserved until end date)"
            rec_cancel_dt = today

        results.append(
            f"• {service} ({platform.replace('_', ' ').title()}):\n"
            f"  - Days Left: {days_left} days (Ends: {end_date_str})\n"
            f"  - Cost if Forgotten: {cost_str}\n"
            f"  - Cancellation Safety: {safety}\n"
            f"  - Recommended Cancel Date: {rec_cancel_dt.strftime('%Y-%m-%d')}\n"
            f"  - How to Cancel: {' -> '.join(steps)}"
        )

    if not results:
        return f"No active trials found for user '{user_id}'."

    return "Active Trial Guard Status:\n" + "\n\n".join(results)


# -----------------------------------------------------------------------------
# 2. CALENDAR REMINDER (.ics)
# -----------------------------------------------------------------------------
def create_trial_reminder(
    service: str,
    cancel_date: str,
    cancel_steps: str,
    price_after_trial: Optional[str] = None,
) -> str:
    """Builds an .ics calendar reminder file and uploads it to public Cloud Storage.

    Args:
        service: Name of the service (e.g. 'Calm', 'Duolingo').
        cancel_date: Recommended cancel date (YYYY-MM-DD).
        cancel_steps: Step-by-step instructions for canceling.
        price_after_trial: Optional price note (e.g. '$69.99/year').

    Returns:
        Public HTTPS URL of the uploaded .ics file.
    """
    clean_date = cancel_date.replace("-", "")
    price_note = f"\\nPrice after trial: {price_after_trial}" if price_after_trial else ""
    escaped_steps = cancel_steps.replace("\n", "\\n").replace(" -> ", "\\n- ")

    ics_content = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Futurewise//TrialGuard//EN\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{secrets.token_hex(16)}@futurewise.app\r\n"
        f"DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}\r\n"
        f"DTSTART;VALUE=DATE:{clean_date}\r\n"
        f"SUMMARY:Cancel Free Trial: {service}\r\n"
        f"DESCRIPTION:Reminder from Futurewise to cancel {service} free trial.{price_note}\\n\\nCancel Steps:\\n{escaped_steps}\r\n"
        "STATUS:CONFIRMED\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )

    random_id = secrets.token_hex(8)
    filename = f"reminders/{service.lower().replace(' ', '_')}_{random_id}.ics"

    client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = client.bucket(GCS_ASSETS_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_string(ics_content, content_type="text/calendar")

    public_url = f"https://storage.googleapis.com/{GCS_ASSETS_BUCKET}/{filename}"
    return f"Calendar reminder created for {service} on {cancel_date}. Download link: {public_url}"


# -----------------------------------------------------------------------------
# 3. SEARCH SUB-AGENT (ADK google_search wrapped as AgentTool)
# -----------------------------------------------------------------------------
search_sub_agent = Agent(
    name="search_sub_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "Specialized search agent that looks up current free-trial cancellation policies, "
        "and fetches current economy and market news with publication dates and sources."
    ),
    instruction=(
        "You are a dedicated market and web research agent.\n"
        "1. When searching for free-trial cancellation policies, determine whether cancellation immediately forfeits access or preserves it until trial end.\n"
        "2. When searching for economy or market news, always include publication sources and dates.\n"
        "3. Provide clear, objective summaries without offering investment advice."
    ),
    tools=[google_search],
)

search_agent_tool = AgentTool(agent=search_sub_agent)


# -----------------------------------------------------------------------------
# 4. EXPENSES (Firestore transactions collection)
# -----------------------------------------------------------------------------
def log_expense(
    description: str,
    category: str,
    amount: float,
    date: Optional[str] = None,
    user_id: str = DEFAULT_USER_ID,
) -> str:
    """Logs an expense transaction to the user's Firestore transactions collection.

    Args:
        description: Description of the merchant or item (e.g. 'Trader Joe's groceries').
        category: Expense category (e.g. 'Groceries', 'Dining', 'Transit', 'Utilities', 'Subscriptions').
        amount: Dollar amount of the expense (positive number).
        date: Date in YYYY-MM-DD format (defaults to current date).
        user_id: Unique user identifier (defaults to 'taylor_nyc_27').

    Returns:
        Confirmation message.
    """
    db = firestore_db.get_firestore_client()
    tx_date = date or datetime.date(2026, 9, 22).strftime("%Y-%m-%d")
    user_ref = db.collection("users").document(user_id)
    tx_ref = user_ref.collection("transactions").document()

    doc_data = {
        "transaction_id": tx_ref.id,
        "date": tx_date,
        "description": description,
        "category": category,
        "amount": -abs(float(amount)),
        "type": "Debit",
    }
    tx_ref.set(doc_data, merge=True)
    return f"Logged expense of ${abs(float(amount)):.2f} for '{description}' [{category}] on {tx_date}."


def get_spending_summary(user_id: str = DEFAULT_USER_ID, limit: int = 50) -> str:
    """Reads transactions from Firestore for the user and computes a spending summary by category.

    Args:
        user_id: Unique user identifier (defaults to 'taylor_nyc_27').
        limit: Max transactions to analyze (defaults to 50).

    Returns:
        A breakdown of total spending and category subtotals.
    """
    db = firestore_db.get_firestore_client()
    docs = (
        db.collection("users")
        .document(user_id)
        .collection("transactions")
        .order_by("date", direction=firestore_db.firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    category_totals: Dict[str, float] = {}
    total_spent = 0.0
    count = 0

    for doc in docs:
        data = doc.to_dict()
        amt = float(data.get("amount", 0.0))
        # Spending is negative debit
        if amt < 0:
            spend = abs(amt)
            cat = data.get("category", "Uncategorized")
            category_totals[cat] = category_totals.get(cat, 0.0) + spend
            total_spent += spend
            count += 1

    if count == 0:
        return f"No spending transactions found for user '{user_id}'."

    lines = [f"Spending Summary for {user_id} (Last {count} expense transactions):"]
    lines.append(f"• Total Outflow: ${total_spent:,.2f}")
    lines.append("• Category Breakdown:")
    for cat, subtotal in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (subtotal / total_spent) * 100 if total_spent > 0 else 0
        lines.append(f"  - {cat}: ${subtotal:,.2f} ({pct:.1f}%)")

    return "\n".join(lines)
