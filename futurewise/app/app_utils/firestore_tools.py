"""Firestore tools for Futurewise Agent.

Provides callable function tools to read and write:
- users
- transactions
- budgets
- goals
- trials
- account_limits
- events
- games
"""

from typing import List, Optional
from app.app_utils import firestore_db


def read_user_profile(user_id: str) -> str:
    """Reads a user's financial profile from Firestore.

    Args:
        user_id: The unique identifier of the user (e.g. 'taylor_nyc_27').

    Returns:
        A formatted string describing the user's financial profile.
    """
    profile = firestore_db.get_user_profile(user_id)
    if not profile:
        return f"No profile found for user '{user_id}'."
    return f"User Profile for {user_id}: {profile}"


def update_user_profile(
    user_id: str,
    annual_income: Optional[float] = None,
    pay_schedule: Optional[str] = None,
    location: Optional[str] = None,
    age: Optional[int] = None,
    occupation: Optional[str] = None,
) -> str:
    """Updates or creates a user profile in Firestore.

    Args:
        user_id: The unique identifier of the user.
        annual_income: Annual gross salary or income.
        pay_schedule: Frequency and timing of pay (e.g. 'bi-weekly on Fridays', 'semi-monthly on 1st and 15th').
        location: City and state of residence (e.g. 'NYC, NY').
        age: Age of the user.
        occupation: Job title or line of work.

    Returns:
        Status message confirming the update.
    """
    data = {}
    if annual_income is not None:
        data["annual_income"] = annual_income
    if pay_schedule is not None:
        data["pay_schedule"] = pay_schedule
    if location is not None:
        data["location"] = location
    if age is not None:
        data["age"] = age
    if occupation is not None:
        data["occupation"] = occupation

    return firestore_db.set_user_profile(user_id, data)


def read_recent_transactions(user_id: str, limit: int = 15, category: Optional[str] = None) -> str:
    """Reads recent bank transactions for a user from Firestore.

    Args:
        user_id: The unique user identifier.
        limit: Maximum number of transactions to retrieve (default 15).
        category: Optional category filter (e.g. 'Groceries', 'Dining', 'Transit', 'Subscriptions', 'Rent').

    Returns:
        A list of recent transactions.
    """
    txs = firestore_db.get_transactions(user_id, limit=limit, category=category)
    if not txs:
        cat_msg = f" in category '{category}'" if category else ""
        return f"No transactions found for user '{user_id}'{cat_msg}."
    lines = [f"- {t.get('date')}: {t.get('description')} (${abs(float(t.get('amount', 0))):.2f}) [{t.get('category')}]" for t in txs]
    return f"Recent transactions for {user_id}:\n" + "\n".join(lines)


def log_user_expense(user_id: str, date: str, description: str, category: str, amount: float) -> str:
    """Logs a new expense transaction into the user's Firestore database.

    Args:
        user_id: The unique user identifier.
        date: Date in YYYY-MM-DD format.
        description: Description of the merchant or charge.
        category: Category (e.g. 'Dining', 'Groceries', 'Transit', 'Entertainment', 'Shopping').
        amount: Dollar amount of the expense (positive number).

    Returns:
        Confirmation message.
    """
    return firestore_db.add_transaction(
        user_id=user_id,
        date=date,
        description=description,
        category=category,
        amount=-abs(amount),
        tx_type="Debit",
    )


def read_user_budgets(user_id: str) -> str:
    """Retrieves all category budget limits for a user.

    Args:
        user_id: The unique user identifier.

    Returns:
        A summary of monthly budget limits by category.
    """
    budgets = firestore_db.get_budgets(user_id)
    if not budgets:
        return f"No monthly budgets configured for user '{user_id}'."
    lines = [f"- {b.get('category')}: ${float(b.get('monthly_limit', 0)):.2f}/month" for b in budgets]
    return f"Monthly budgets for {user_id}:\n" + "\n".join(lines)


def set_category_budget(user_id: str, category: str, monthly_limit: float) -> str:
    """Sets or updates a monthly budget target for a specific category.

    Args:
        user_id: The unique user identifier.
        category: Category name (e.g. 'Groceries', 'Dining', 'Transit', 'Subscriptions').
        monthly_limit: Monthly spending cap in dollars.

    Returns:
        Confirmation message.
    """
    return firestore_db.set_budget(user_id, category, monthly_limit)


def read_user_goals(user_id: str) -> str:
    """Reads all financial goals and current progress for a user.

    Args:
        user_id: The unique user identifier.

    Returns:
        Summary of user financial goals.
    """
    goals = firestore_db.get_financial_goals(user_id)
    if not goals:
        return f"No financial goals found for user '{user_id}'."
    lines = [
        f"- {g.get('goal_name')}: ${float(g.get('current_amount', 0)):.2f} / ${float(g.get('target_amount', 0)):.2f} (Target date: {g.get('target_date', 'Ongoing')})"
        for g in goals
    ]
    return f"Financial goals for {user_id}:\n" + "\n".join(lines)


def save_user_goal(
    user_id: str,
    goal_name: str,
    target_amount: float,
    current_amount: float = 0.0,
    target_date: Optional[str] = None,
) -> str:
    """Creates or updates a financial goal for a user.

    Args:
        user_id: The unique user identifier.
        goal_name: Name of the goal (e.g. 'Emergency Fund', 'Roth IRA Max').
        target_amount: Target goal amount in dollars.
        current_amount: Current amount saved so far.
        target_date: Target completion date in YYYY-MM-DD or description.

    Returns:
        Confirmation message.
    """
    return firestore_db.set_financial_goal(
        user_id=user_id,
        goal_name=goal_name,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date,
    )


def read_active_trials(user_id: str) -> str:
    """Reads all active free trials and auto-renewing subscriptions being tracked for a user.

    Args:
        user_id: The unique user identifier.

    Returns:
        Summary of tracked trials, renewal dates, and prices.
    """
    trials = firestore_db.get_free_trials(user_id)
    if not trials:
        return f"No active free trials or subscriptions tracked for user '{user_id}'."
    lines = []
    for t in trials:
        line = f"- {t.get('service_name')} ({t.get('platform')}): Ends {t.get('trial_end_date')} | Renews at {t.get('price_after_trial')}"
        if t.get("recommended_action"):
            line += f"\n  Action: {t.get('recommended_action')}"
        lines.append(line)
    return f"Active trials for {user_id}:\n" + "\n".join(lines)


def track_free_trial(
    user_id: str,
    service_name: str,
    platform: str,
    trial_end_date: str,
    price_after_trial: str,
    recommended_action: Optional[str] = None,
) -> str:
    """Adds a new free trial or subscription to Trial Guard for a user.

    Args:
        user_id: The unique user identifier.
        service_name: Name of the service or app.
        platform: Platform hosting the subscription ('App Store', 'Google Play', or 'Website').
        trial_end_date: Date the free trial ends (YYYY-MM-DD).
        price_after_trial: Price charged once trial ends (e.g. '$69.99/year', '$12.99/month').
        recommended_action: Guidance on when and how to cancel.

    Returns:
        Confirmation message.
    """
    return firestore_db.save_free_trial(
        user_id=user_id,
        service_name=service_name,
        platform=platform,
        trial_end_date=trial_end_date,
        price_after_trial=price_after_trial,
        recommended_action=recommended_action,
    )


def read_account_limits(tax_year: int) -> str:
    """Retrieves official contribution limits and rules for IRAs, HSAs, FSAs, and 401(k)s for a tax year.

    Args:
        tax_year: The tax year to query (e.g. 2024, 2025, 2026).

    Returns:
        A detailed summary of statutory contribution limits for that tax year.
    """
    limits = firestore_db.get_account_limits(tax_year)
    if not limits:
        return f"No statutory limits found for tax year {tax_year}."
    ira = limits.get("ira", {})
    hsa = limits.get("hsa", {})
    fsa = limits.get("healthcare_fsa", {})
    k401 = limits.get("retirement_401k_403b", {})
    return (
        f"Tax Year {tax_year} Contribution Limits:\n"
        f"- IRA: ${ira.get('regular_contribution_limit'):,} (Catch-up 50+: +${ira.get('catch_up_limit_age_50_plus'):,})\n"
        f"- HSA: Individual ${hsa.get('individual_coverage_limit'):,} | Family ${hsa.get('family_coverage_limit'):,} (Catch-up 55+: +${hsa.get('catch_up_limit_age_55_plus'):,})\n"
        f"- Healthcare FSA: ${fsa.get('employee_salary_reduction_limit'):,} (Max carryover: ${fsa.get('max_carryover_to_next_year'):,})\n"
        f"- 401(k) Elective Deferral: ${k401.get('employee_elective_deferral_limit'):,} (Catch-up 50+: +${k401.get('catch_up_limit_age_50_plus'):,})"
    )


def read_life_events(category: Optional[str] = None, chapter: Optional[int] = None) -> str:
    """Retrieves life simulation scenario events from the deck.

    Args:
        category: Optional category filter (e.g. 'Housing', 'Career', 'Health', 'Retirement', 'Debt').
        chapter: Optional chapter number (1 to 5).

    Returns:
        Summary of scenario cards in the deck.
    """
    events = firestore_db.get_life_events(category=category, chapter=chapter)
    if not events:
        return "No life simulation events found matching the criteria."
    lines = []
    for e in events:
        lines.append(f"Event [{e.get('id')}]: {e.get('title')} ({e.get('category')}, Chapter {e.get('chapter')})")
        lines.append(f"  Prompt: {e.get('prompt')}")
        for opt in e.get("options", []):
            lines.append(f"    [{opt.get('option_id')}] {opt.get('label')}")
    return "\n".join(lines)


def read_user_simulation_games(user_id: str) -> str:
    """Reads past or ongoing life simulation game sessions for a user.

    Args:
        user_id: The unique user identifier.

    Returns:
        Summary of simulation games and scores.
    """
    games = firestore_db.get_user_games(user_id)
    if not games:
        return f"No simulation games found for user '{user_id}'."
    lines = [
        f"- Game '{g.get('game_id')}': Chapter {g.get('current_chapter')}, Net Worth: ${float(g.get('net_worth', 0)):,.2f}, Status: {g.get('status')}"
        for g in games
    ]
    return f"Simulation games for {user_id}:\n" + "\n".join(lines)


def save_user_simulation_game(
    user_id: str,
    game_id: str,
    current_chapter: int,
    net_worth: float,
    cash_balance: float,
    choice_summary: str,
    status: str = "in_progress",
) -> str:
    """Saves or updates a user's life simulation game progress.

    Args:
        user_id: The unique user identifier.
        game_id: Identifier for the game session (e.g. 'game_2026_01').
        current_chapter: The current chapter reached (1-5).
        net_worth: Estimated net worth in dollars.
        cash_balance: Liquid cash balance.
        choice_summary: Summary of latest choice made.
        status: Status ('in_progress' or 'completed').

    Returns:
        Confirmation message.
    """
    return firestore_db.save_game_session(
        user_id=user_id,
        game_id=game_id,
        current_chapter=current_chapter,
        net_worth=net_worth,
        cash_balance=cash_balance,
        choices_made=[{"chapter": current_chapter, "summary": choice_summary}],
        status=status,
    )
