"""Financial analysis, simulation, and sandbox execution tools powered by Agent Platform Sandbox."""

import os
import random
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor
from google.adk.code_executors.base_code_executor import CodeExecutionInput
from app.app_utils import firestore_db

FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"
DEFAULT_USER_ID = "taylor_nyc_27"
AGENT_ENGINE_RESOURCE = "projects/754395904178/locations/us-east1/reasoningEngines/8383074673373478912"


def _get_sandbox_executor() -> AgentEngineSandboxCodeExecutor:
    os.environ["GOOGLE_CLOUD_PROJECT"] = FIRESTORE_PROJECT_ID
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east1"
    return AgentEngineSandboxCodeExecutor(agent_engine_resource_name=AGENT_ENGINE_RESOURCE)


def execute_sandbox_code(code: str) -> Dict[str, Any]:
    """Executes arbitrary Python code safely inside the Agent Engine Sandbox.

    Use this tool whenever custom computations, math, algorithms (e.g. fizzbuzz),
    or data analysis routines need to be evaluated in a sandboxed environment.

    Args:
        code: The Python code snippet to run.

    Returns:
        A dictionary containing 'stdout', 'stderr', and 'success' status.
    """
    executor = _get_sandbox_executor()
    mock_ctx = MagicMock()
    mock_ctx.session.state.get.return_value = None

    result = executor.execute_code(mock_ctx, CodeExecutionInput(code=code))
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": bool(not result.stderr or result.stdout),
    }


def run_spending_analysis(user_id: str = DEFAULT_USER_ID) -> Dict[str, Any]:
    """Runs full spending analysis in the sandbox using the user's actual transactions & budgets.

    Computes:
    - Spending by category
    - Budget vs Actual per category
    - Recurring charges (subscriptions)
    - Weekly safe-to-spend remainder
    """
    db = firestore_db.get_firestore_client()
    tx_docs = list(db.collection("users").document(user_id).collection("transactions").stream())
    budget_docs = list(db.collection("users").document(user_id).collection("budgets").stream())

    transactions = [d.to_dict() for d in tx_docs]
    budgets = {d.id: d.to_dict().get("monthly_limit", 0) for d in budget_docs}

    code = f"""
import json

transactions = {transactions!r}
budgets = {budgets!r}

cat_totals = {{}}
recurring = []

for tx in transactions:
    cat = tx.get('category', 'uncategorized')
    amt = float(tx.get('amount', 0))
    cat_totals[cat] = cat_totals.get(cat, 0.0) + amt
    if tx.get('is_recurring'):
        recurring.append({{'description': tx.get('description'), 'amount': amt, 'category': cat}})

total_spend = sum(cat_totals.values())
budget_comparison = {{}}
total_budget = sum(budgets.values())

for cat, limit in budgets.items():
    spent = cat_totals.get(cat, 0.0)
    budget_comparison[cat] = {{
        'limit': limit,
        'spent': round(spent, 2),
        'remaining': round(limit - spent, 2),
        'percent_used': round((spent / limit * 100) if limit > 0 else 0, 1)
    }}

total_remaining = max(0.0, total_budget - total_spend)
weekly_safe_to_spend = round(total_remaining / 4.33, 2)

result = {{
    'total_spent': round(total_spend, 2),
    'total_budget': round(total_budget, 2),
    'weekly_safe_to_spend': weekly_safe_to_spend,
    'category_totals': {{k: round(v, 2) for k, v in cat_totals.items()}},
    'budget_comparison': budget_comparison,
    'recurring_count': len(recurring)
}}
print(json.dumps(result))
"""
    res = execute_sandbox_code(code)
    import json
    try:
        return json.loads(res["stdout"].strip())
    except Exception:
        return {"error": "Failed to parse analysis", "raw": res}


def run_stability_check(user_id: str = DEFAULT_USER_ID) -> Dict[str, Any]:
    """Runs a 3-pillar stability check inside the sandbox.

    Calculates:
    - Months of living expenses covered by savings
    - Monthly savings rate
    - High-interest debt status and payoff priority
    """
    db = firestore_db.get_firestore_client()
    user_doc = db.collection("users").document(user_id).get()
    user_data = user_doc.to_dict() or {}

    salary = user_data.get("salary", 68000)
    savings = user_data.get("savings_balance", 4500)
    debt = user_data.get("debt_balance", 3200)

    code = f"""
import json

salary = {salary}
savings_balance = {savings}
debt_balance = {debt}

monthly_gross = salary / 12.0
monthly_net_est = monthly_gross * 0.72 # NYC approx net
monthly_essential_expenses = 3200.0

months_covered = round(savings_balance / monthly_essential_expenses, 1)
savings_rate = round(((monthly_net_est - monthly_essential_expenses) / monthly_net_est) * 100, 1)

high_interest_alert = debt_balance > 0
payoff_recommendation = (
    "Prioritize paying down high-interest credit card balance before aggressive investing."
    if high_interest_alert else "Debt free from high-interest debt! Focus on emergency fund and retirement accounts."
)

res = {{
    'months_expenses_covered': months_covered,
    'target_months': 3.0,
    'savings_rate_percent': savings_rate,
    'target_savings_rate': 20.0,
    'high_interest_debt': debt_balance,
    'payoff_recommendation': payoff_recommendation,
    'status': 'Cautious' if months_covered < 3.0 else 'Stable'
}}
print(json.dumps(res))
"""
    res = execute_sandbox_code(code)
    import json
    try:
        return json.loads(res["stdout"].strip())
    except Exception:
        return {"error": "Failed to parse stability check", "raw": res}


def compare_hsa_vs_fsa(user_id: str = DEFAULT_USER_ID, expected_medical_spend: float = 1200.0) -> Dict[str, Any]:
    """Runs an HSA vs FSA comparison tailored to user numbers in sandbox."""
    code = f"""
import json

spend = {expected_medical_spend}
tax_bracket = 0.22 # 22% marginal federal bracket
fica_rate = 0.0765

hsa_limit_single = 4300
fsa_limit = 3300

# HSA: triple-tax advantaged, rolls over indefinitely, investable
hsa_tax_savings = round(spend * (tax_bracket + fica_rate), 2)
# FSA: use-it-or-lose-it, limited rollover ($660 max)
fsa_tax_savings = round(spend * (tax_bracket + fica_rate), 2)

res = {{
    'expected_spend': spend,
    'hsa_limit': hsa_limit_single,
    'fsa_limit': fsa_limit,
    'estimated_tax_savings': hsa_tax_savings,
    'hsa_features': {{
        'rollover': '100% rolls over forever; never forfeited',
        'investment': 'Can be invested in index funds / growth assets',
        'portability': 'Stays with you forever even if changing employers'
    }},
    'fsa_features': {{
        'rollover': 'Use-it-or-lose-it (max $660 rollover allowed)',
        'investment': 'Cannot be invested',
        'portability': 'Tied strictly to current employer plan'
    }},
    'recommendation': 'HSA is superior if enrolled in an HDHP due to permanent rollover and investment growth.'
}}
print(json.dumps(res))
"""
    res = execute_sandbox_code(code)
    import json
    try:
        return json.loads(res["stdout"].strip())
    except Exception:
        return {"error": "Failed to parse HSA/FSA comparison", "raw": res}


def compare_roth_vs_traditional(
    user_id: str = DEFAULT_USER_ID,
    annual_contribution: float = 7000.0,
    years_to_grow: int = 30,
) -> Dict[str, Any]:
    """Runs a personalized Roth vs Traditional retirement account comparison."""
    code = f"""
import json

contrib = {annual_contribution}
years = {years_to_grow}
annual_return = 0.07
current_bracket = 0.22
retirement_bracket = 0.15 # estimated lower bracket in retirement

# Compound growth formula: FV = P * ((1 + r)^t - 1) / r
fv = contrib * (((1 + annual_return)**years - 1) / annual_return)

# Roth: Pay tax today (post-tax dollars), zero tax at withdrawal
roth_initial_tax = contrib * current_bracket
roth_final_wealth = fv

# Traditional: Tax deduction today, pay ordinary income tax on full withdrawal
trad_initial_tax_savings = contrib * current_bracket
trad_final_wealth_after_tax = fv * (1 - retirement_bracket)

res = {{
    'annual_contribution': contrib,
    'horizon_years': years,
    'projected_gross_portfolio': round(fv, 2),
    'roth_after_tax_wealth': round(roth_final_wealth, 2),
    'traditional_after_tax_wealth': round(trad_final_wealth_after_tax, 2),
    'roth_advantage': round(roth_final_wealth - trad_final_wealth_after_tax, 2),
    'summary': 'Roth IRA yields tax-free growth and distributions, giving higher net wealth if current taxes are lower or equal to future brackets.'
}}
print(json.dumps(res))
"""
    res = execute_sandbox_code(code)
    import json
    try:
        return json.loads(res["stdout"].strip())
    except Exception:
        return {"error": "Failed to parse Roth/Trad comparison", "raw": res}


def run_life_simulation(user_id: str = DEFAULT_USER_ID, seed: int = 42) -> Dict[str, Any]:
    """Runs the 5-chapter life simulator and 1,000-lives replay inside the sandbox.

    Selects 5 chapters from the Firestore events deck, runs a fixed random seed
    deterministic path, and executes a 1,000-lives Monte Carlo replay returning a decision score.
    """
    db = firestore_db.get_firestore_client()
    events_docs = list(db.collection("events").stream())
    events = [d.to_dict() for d in events_docs]

    code = f"""
import json
import random

seed = {seed}
events = {events!r}

# Set fixed seed
random.seed(seed)

# Select 5 chapters
sample_events = random.sample(events, min(5, len(events)))
chapters = []
current_age = 27
current_net_worth = 12000.0

for i, ev in enumerate(sample_events):
    age = current_age + (i * 7)
    title = ev.get('title', f'Chapter {{i+1}}')
    options = ev.get('options', [])
    chosen_opt = options[0] if options else {{'title': 'Conservative Choice', 'cost': -1000, 'net_worth_effect': 5000}}
    nw_delta = float(chosen_opt.get('net_worth_effect', 2000))
    current_net_worth += nw_delta
    chapters.append({{
        'chapter_number': i + 1,
        'age': age,
        'event_title': title,
        'selected_option': chosen_opt.get('title', 'Choice A'),
        'net_worth': round(current_net_worth, 2),
        'lesson': ev.get('lesson', 'Every financial trade-off compounds over time.')
    }})

# 1,000-lives Monte Carlo replay
outcomes = []
for _ in range(1000):
    nw = 12000.0
    for ev in sample_events:
        opts = ev.get('options', [])
        # random decision distribution
        opt = random.choice(opts) if opts else {{'net_worth_effect': 2000}}
        market_luck = random.gauss(1.06, 0.05) # market variability
        nw = (nw + float(opt.get('net_worth_effect', 1500))) * (market_luck ** 7)
    outcomes.append(round(nw, 2))

mean_outcome = sum(outcomes) / len(outcomes)
decision_score = min(100, max(0, int(75 + (current_net_worth / mean_outcome) * 20)))

res = {{
    'chapters': chapters,
    'final_net_worth': round(current_net_worth, 2),
    'monte_carlo_1000_sample': outcomes[:100], # sample distribution for charting
    'monte_carlo_mean': round(mean_outcome, 2),
    'decision_score': decision_score,
    'score_tier': 'Master Wealth Builder' if decision_score >= 85 else 'Prudent Strategist'
}}
print(json.dumps(res))
"""
    res = execute_sandbox_code(code)
    import json
    try:
        return json.loads(res["stdout"].strip())
    except Exception:
        return {"error": "Failed to parse simulation", "raw": res}
