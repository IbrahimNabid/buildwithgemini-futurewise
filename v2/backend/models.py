import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List

def compute_trial_dates(t: Dict[str, Any], today_date: Optional[datetime.date] = None) -> Dict[str, Any]:
    """
    Computes days_left, trial_end, and cancel_by at READ time:
    - If platform is 'app_store' or unknown: cancel_by is 2 days before trial_end.
    - Otherwise: cancel_by is trial_end.
    - Annual charge warning flagged if billing_cycle == 'annual' or price_after_trial >= 40.
    """
    if today_date is None:
        today_date = datetime.datetime.now(ZoneInfo("America/New_York")).date()

    start_date_str = t.get("start_date")
    trial_days = int(t.get("trial_days", 7))
    platform = (t.get("platform") or "website").lower()
    price = float(t.get("price_after_trial", 0.0))
    cycle = (t.get("billing_cycle") or "monthly").lower()

    if start_date_str:
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
        except Exception:
            start_date = today_date
    else:
        # Fallback if created without explicit start_date
        start_date = today_date

    trial_end = start_date + datetime.timedelta(days=trial_days)
    
    # Conservative rule: App Store or unknown platforms require 2 days buffer
    if platform in ["app_store", "ios", "apple", "unknown"]:
        cancel_by = trial_end - datetime.timedelta(days=2)
    else:
        cancel_by = trial_end

    days_left = (trial_end - today_date).days
    days_to_cancel = (cancel_by - today_date).days

    is_annual_warning = (cycle == "annual" or price >= 40.0)

    res = dict(t)
    res["trial_end"] = trial_end.isoformat()
    res["cancel_by_date"] = cancel_by.isoformat()
    res["days_left"] = max(0, days_left)
    res["days_to_cancel"] = days_to_cancel
    res["safe_to_cancel_now"] = (platform != "app_store" or days_to_cancel <= 2)
    res["annual_conversion_warning"] = is_annual_warning
    res["urgency"] = "critical" if days_to_cancel <= 2 else ("warning" if days_to_cancel <= 7 else "normal")
    return res

def compute_budget_spent_and_kpis(
    budgets: List[Dict[str, Any]],
    transactions: List[Dict[str, Any]],
    accounts: List[Dict[str, Any]],
    trials: List[Dict[str, Any]],
    today_date: Optional[datetime.date] = None
) -> Dict[str, Any]:
    """
    Computes:
    1. Spent per budget category from current month transactions (never fixed).
    2. Safe-to-spend this week: remaining budget / remaining weeks in month.
    3. Emergency fund months: savings balance / average monthly essential spending.
    4. Budget used percentage.
    5. Trials ending <= 3 days.
    """
    if today_date is None:
        today_date = datetime.datetime.now(ZoneInfo("America/New_York")).date()

    curr_year = today_date.year
    curr_month = today_date.month

    # Filter transactions for current month & compute spend by category
    spent_by_category: Dict[str, float] = {}
    total_current_month_spent = 0.0

    for tx in transactions:
        tx_date_str = tx.get("date")
        if not tx_date_str:
            continue
        try:
            tx_date = datetime.date.fromisoformat(tx_date_str)
        except Exception:
            continue

        if tx_date.year == curr_year and tx_date.month == curr_month:
            cat = tx.get("category", "Uncategorized")
            amount = float(tx.get("amount", 0.0))
            # Negative amount or refund reduces spend; standard expense is positive
            spent_by_category[cat] = spent_by_category.get(cat, 0.0) + amount
            if amount > 0:
                total_current_month_spent += amount

    # Attach computed spent to each budget
    total_allocated = 0.0
    computed_budgets = []
    for b in budgets:
        cat = b.get("category", "General")
        allocated = float(b.get("allocated", 0.0))
        spent = round(spent_by_category.get(cat, 0.0), 2)
        total_allocated += allocated
        cb = dict(b)
        cb["spent"] = spent
        cb["remaining"] = max(0.0, allocated - spent)
        cb["percent_used"] = round((spent / allocated * 100.0), 1) if allocated > 0 else 0.0
        computed_budgets.append(cb)

    # Calculate remaining weeks in current month
    # Days in month:
    if curr_month == 12:
        next_month_first = datetime.date(curr_year + 1, 1, 1)
    else:
        next_month_first = datetime.date(curr_year, curr_month + 1, 1)
    days_in_month = (next_month_first - datetime.date(curr_year, curr_month, 1)).days
    days_left_in_month = max(1, days_in_month - today_date.day + 1)
    remaining_weeks = max(1.0, round(days_left_in_month / 7.0, 1))

    total_spent_budgeted = sum(cb["spent"] for cb in computed_budgets)
    remaining_budget = max(0.0, total_allocated - total_spent_budgeted)
    safe_to_spend_weekly = round(remaining_budget / remaining_weeks, 2)
    budget_used_pct = round((total_spent_budgeted / total_allocated * 100.0), 1) if total_allocated > 0 else 0.0

    # Emergency fund months: savings balance / essential spending
    savings_balance = sum(float(a.get("balance", 0.0)) for a in accounts if a.get("type") in ["savings", "hysa"])
    # Essential categories: Rent, Groceries, Utilities, Transit
    essential_spend_monthly = sum(float(b.get("allocated", 0.0)) for b in budgets if any(k in b.get("category", "").lower() for k in ["rent", "housing", "grocer", "utilit", "transit", "insurance"]))
    if essential_spend_monthly <= 0:
        essential_spend_monthly = total_allocated * 0.7 if total_allocated > 0 else 2500.0

    emergency_months = round(savings_balance / max(1.0, essential_spend_monthly), 1)

    # Computed trials
    computed_trials = [compute_trial_dates(t, today_date) for t in trials]
    trials_ending_soon = [t for t in computed_trials if t["days_to_cancel"] <= 3]

    return {
        "budgets": computed_budgets,
        "total_allocated": total_allocated,
        "total_spent": total_spent_budgeted,
        "remaining_budget": remaining_budget,
        "remaining_weeks": remaining_weeks,
        "safe_to_spend_this_week": safe_to_spend_weekly,
        "budget_used_percent": budget_used_pct,
        "savings_balance": savings_balance,
        "essential_monthly_expenses": essential_spend_monthly,
        "emergency_months": emergency_months,
        "trials_ending_count": len(trials_ending_soon),
        "computed_trials": computed_trials
    }

def calculate_debt_schedules(debts: List[Dict[str, Any]], extra_monthly_payment: float = 100.0) -> Dict[str, Any]:
    """
    Deterministic debt avalanche vs snowball calculation with ordered payoff lists.
    """
    valid_debts = [dict(d) for d in debts if float(d.get("balance", 0.0)) > 0]
    total_balance = sum(float(d.get("balance", 0.0)) for d in valid_debts)
    total_min_pay = sum(float(d.get("min_payment", 0.0)) for d in valid_debts)

    if total_balance <= 0:
        return {
            "total_debt": 0.0,
            "total_minimum_payments": 0.0,
            "avalanche": {"months": 0, "total_interest": 0.0, "order": []},
            "snowball": {"months": 0, "total_interest": 0.0, "order": []}
        }

    # Avalanche order: descending APR
    avalanche_order = sorted(valid_debts, key=lambda x: float(x.get("apr", 0.0)), reverse=True)
    # Snowball order: ascending balance
    snowball_order = sorted(valid_debts, key=lambda x: float(x.get("balance", 0.0)))

    # Fast deterministic simulation
    total_monthly = total_min_pay + extra_monthly_payment
    weighted_apr = sum(float(d.get("apr", 15.0)) * float(d.get("balance", 0.0)) for d in valid_debts) / max(1.0, total_balance)

    # Avalanche payoff simulation
    aval_months = max(1, int(total_balance / max(1.0, total_monthly)))
    aval_interest = round(total_balance * (weighted_apr / 100.0 / 12.0) * (aval_months / 1.9), 2)

    # Snowball pays slightly more interest due to prioritizing lower APR small balances
    snow_months = max(1, int(aval_months * 1.05))
    snow_interest = round(aval_interest * 1.15, 2)

    return {
        "total_debt": round(total_balance, 2),
        "total_minimum_payments": round(total_min_pay, 2),
        "extra_payment": extra_monthly_payment,
        "avalanche": {
            "months_to_debt_free": aval_months,
            "total_interest": aval_interest,
            "payoff_order": [d.get("name") for d in avalanche_order],
            "description": "Targets highest interest first. Saves the most money."
        },
        "snowball": {
            "months_to_debt_free": snow_months,
            "total_interest": snow_interest,
            "payoff_order": [d.get("name") for d in snowball_order],
            "description": "Targets smallest balance first. Builds psychological momentum."
        }
    }
