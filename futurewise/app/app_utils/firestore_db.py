"""Firestore database client and collection helper for Futurewise.

Hardcoded GCP project ID as requested to prevent Agent Platform
project number translation issues.
"""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# IMPORTANT: Hardcoded project ID as string.
# On Agent Platform, google.auth.default() or GOOGLE_CLOUD_PROJECT returns the numeric project number,
# which breaks Firestore calls on deployed reasoning engines.
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"

_db: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client connected with the hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    return _db


# -----------------------------------------------------------------------------
# User Profile Collection: users/{userId}
# -----------------------------------------------------------------------------
def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves user profile data (income, age, location, financial baseline)."""
    db = get_firestore_client()
    doc = db.collection("users").document(user_id).get()
    return doc.to_dict() if doc.exists else None


def set_user_profile(user_id: str, profile_data: Dict[str, Any]) -> str:
    """Creates or updates a user profile."""
    db = get_firestore_client()
    db.collection("users").document(user_id).set(profile_data, merge=True)
    return f"User profile for '{user_id}' updated successfully."


# -----------------------------------------------------------------------------
# Transactions Collection: users/{userId}/transactions/{transactionId}
# -----------------------------------------------------------------------------
def get_transactions(user_id: str, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Gets recent transactions for a user, optionally filtered by category."""
    db = get_firestore_client()
    query = db.collection("users").document(user_id).collection("transactions")
    if category:
        query = query.where("category", "==", category)
    docs = query.order_by("date", direction=firestore.Query.DESCENDING).limit(limit).stream()
    return [doc.to_dict() for doc in docs]


def add_transaction(
    user_id: str,
    date: str,
    description: str,
    category: str,
    amount: float,
    tx_type: str = "Debit",
    transaction_id: Optional[str] = None,
) -> str:
    """Logs a single transaction for a user."""
    db = get_firestore_client()
    tx_ref = (
        db.collection("users").document(user_id).collection("transactions").document(transaction_id)
        if transaction_id
        else db.collection("users").document(user_id).collection("transactions").document()
    )
    doc_data = {
        "transaction_id": tx_ref.id,
        "date": date,
        "description": description,
        "category": category,
        "amount": amount,
        "type": tx_type,
    }
    tx_ref.set(doc_data, merge=True)
    return f"Transaction '{tx_ref.id}' for ${amount:.2f} in '{category}' recorded."


# -----------------------------------------------------------------------------
# Budgets Collection: users/{userId}/budgets/{category}
# -----------------------------------------------------------------------------
def get_budgets(user_id: str) -> List[Dict[str, Any]]:
    """Gets monthly budget targets for all categories for a user."""
    db = get_firestore_client()
    docs = db.collection("users").document(user_id).collection("budgets").stream()
    return [doc.to_dict() for doc in docs]


def set_budget(user_id: str, category: str, monthly_limit: float) -> str:
    """Sets or updates a monthly budget limit for a category."""
    db = get_firestore_client()
    doc_ref = db.collection("users").document(user_id).collection("budgets").document(category.lower())
    doc_ref.set({"category": category, "monthly_limit": monthly_limit}, merge=True)
    return f"Budget for '{category}' set to ${monthly_limit:.2f}/month."


# -----------------------------------------------------------------------------
# Goals Collection: users/{userId}/goals/{goalId}
# -----------------------------------------------------------------------------
def get_financial_goals(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all financial goals for a user."""
    db = get_firestore_client()
    docs = db.collection("users").document(user_id).collection("goals").stream()
    return [doc.to_dict() for doc in docs]


def set_financial_goal(
    user_id: str,
    goal_name: str,
    target_amount: float,
    current_amount: float = 0.0,
    target_date: Optional[str] = None,
    goal_id: Optional[str] = None,
) -> str:
    """Sets or updates a financial goal."""
    db = get_firestore_client()
    doc_id = goal_id or goal_name.lower().replace(" ", "_")
    doc_ref = db.collection("users").document(user_id).collection("goals").document(doc_id)
    doc_data = {
        "goal_id": doc_id,
        "goal_name": goal_name,
        "target_amount": target_amount,
        "current_amount": current_amount,
        "target_date": target_date,
    }
    doc_ref.set(doc_data, merge=True)
    return f"Goal '{goal_name}' (${current_amount:.2f}/${target_amount:.2f}) saved."


# -----------------------------------------------------------------------------
# Trials Collection: users/{userId}/trials/{trialId}
# -----------------------------------------------------------------------------
def get_free_trials(user_id: str) -> List[Dict[str, Any]]:
    """Gets all tracked free trials and subscriptions for a user."""
    db = get_firestore_client()
    docs = db.collection("users").document(user_id).collection("trials").stream()
    return [doc.to_dict() for doc in docs]


def save_free_trial(
    user_id: str,
    service_name: str,
    platform: str,
    trial_end_date: str,
    price_after_trial: str,
    trial_id: Optional[str] = None,
    recommended_action: Optional[str] = None,
    cancellation_steps: Optional[List[str]] = None,
) -> str:
    """Adds or updates a free trial under the user's trial guard."""
    db = get_firestore_client()
    doc_id = trial_id or service_name.lower().replace(" ", "_").replace("-", "_")
    doc_ref = db.collection("users").document(user_id).collection("trials").document(doc_id)
    doc_data = {
        "id": doc_id,
        "service_name": service_name,
        "platform": platform,
        "trial_end_date": trial_end_date,
        "price_after_trial": price_after_trial,
        "recommended_action": recommended_action,
        "cancellation_steps": cancellation_steps or [],
    }
    doc_ref.set(doc_data, merge=True)
    return f"Free trial for '{service_name}' on {platform} (ends {trial_end_date}) saved."


# -----------------------------------------------------------------------------
# Account Limits Collection: account_limits/{taxYear}
# -----------------------------------------------------------------------------
def get_account_limits(tax_year: int) -> Optional[Dict[str, Any]]:
    """Retrieves IRS/statutory contribution limits for IRAs, HSAs, FSAs, and 401(k)s for a tax year."""
    db = get_firestore_client()
    doc = db.collection("account_limits").document(str(tax_year)).get()
    return doc.to_dict() if doc.exists else None


# -----------------------------------------------------------------------------
# Life Events Deck Collection: events/{eventId}
# -----------------------------------------------------------------------------
def get_life_events(category: Optional[str] = None, chapter: Optional[int] = None) -> List[Dict[str, Any]]:
    """Gets life simulation scenario events from the deck, optionally filtered."""
    db = get_firestore_client()
    query = db.collection("events")
    if category:
        query = query.where("category", "==", category)
    if chapter:
        query = query.where("chapter", "==", chapter)
    docs = query.stream()
    return [doc.to_dict() for doc in docs]


def get_life_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """Gets a specific life simulation event by its ID."""
    db = get_firestore_client()
    doc = db.collection("events").document(event_id).get()
    return doc.to_dict() if doc.exists else None


# -----------------------------------------------------------------------------
# Games / Simulation Sessions Collection: users/{userId}/games/{gameId}
# -----------------------------------------------------------------------------
def get_user_games(user_id: str) -> List[Dict[str, Any]]:
    """Gets all simulation game sessions for a user."""
    db = get_firestore_client()
    docs = db.collection("users").document(user_id).collection("games").stream()
    return [doc.to_dict() for doc in docs]


def save_game_session(
    user_id: str,
    game_id: str,
    current_chapter: int,
    net_worth: float,
    cash_balance: float,
    choices_made: List[Dict[str, Any]],
    status: str = "in_progress",
) -> str:
    """Saves or updates a user's life simulation game state."""
    db = get_firestore_client()
    doc_ref = db.collection("users").document(user_id).collection("games").document(game_id)
    doc_data = {
        "game_id": game_id,
        "current_chapter": current_chapter,
        "net_worth": net_worth,
        "cash_balance": cash_balance,
        "choices_made": choices_made,
        "status": status,
    }
    doc_ref.set(doc_data, merge=True)
    return f"Simulation game '{game_id}' updated (Chapter {current_chapter}, Net Worth ${net_worth:,.2f})."
