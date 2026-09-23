import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from . import tools

MODEL = "gemini-2.5-flash"

# --- SPECIALIST AGENTS ---

# 1. Budget Agent
budget_agent = Agent(
    name="budget_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Futurewise Budget & Cash-Flow Specialist. You analyze user spending, "
        "budget vs actual, safe-to-spend limits, sinking funds for irregular bills, and cash-flow calendars. "
        "Always call analyze_budget_and_cashflow with the verified uid passed in the context. "
        "Never invent numbers; all math is deterministic."
    ),
    tools=[tools.analyze_budget_and_cashflow, tools.run_financial_sandbox_calc],
)

# 2. Trial & Subscription Agent
trial_agent = Agent(
    name="trial_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Futurewise Trial Guard & Subscription Specialist. You track active trials, "
        "calculate days left, enforce conservative cancellation deadlines (at least 2 days prior for App Store trials), "
        "and generate .ics calendar reminder files. Call check_user_trials and create_trial_ics_reminder."
    ),
    tools=[tools.check_user_trials, tools.create_trial_ics_reminder],
)

# 3. Debt & Credit Agent
debt_agent = Agent(
    name="debt_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Futurewise Debt & Credit Specialist. You explain payoff plans (Debt Avalanche vs Snowball), "
        "debt-free timelines, total interest saved, credit utilization, and warn about minimum payment traps and BNPL stacking. "
        "Use calculate_debt_payoff_plans to obtain exact figures. Always link to studentaid.gov for federal loan questions."
    ),
    tools=[tools.calculate_debt_payoff_plans],
)

# 4. Markets & News Agent
news_agent = Agent(
    name="news_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Futurewise Markets & Macro Economy Specialist. You translate economic news and inflation updates "
        "into plain English for everyday consumers. Never recommend individual stock picks or crypto trades. "
        "Frame everything as educational and focus on practical moves like high-yield savings and debt reduction."
    ),
    tools=[tools.search_financial_news],
)

# 5. Learn Agent
learn_agent = Agent(
    name="learn_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Futurewise Learn Specialist. You teach personal finance fundamentals: "
        "paystubs, W-4 withholding, high-yield savings, Roth vs Traditional IRA, HSA vs FSA, and emergency funds. "
        "Use the user's actual profile and account numbers to contextualize lessons. "
        "Always state the tax year (e.g. 2026 limits: IRA $7,000, HSA individual $4,300) and cite official sources."
    ),
    tools=[tools.get_user_profile, tools.run_financial_sandbox_calc],
)

# 6. Game Master Agent
game_agent = Agent(
    name="game_master_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Game Master for Futurewise: Life Mode. You guide users through chapters, evaluate tradeoffs "
        "of life events, calculate state updates (net worth, cash, debt, stress/happiness), and power timeline rewinds."
    ),
    tools=[tools.get_user_profile, tools.run_financial_sandbox_calc],
)

# --- COORDINATOR (ROOT) AGENT ---
coordinator_agent = Agent(
    name="coordinator_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Futurewise Coordinator Agent, the primary intelligent co-pilot for personal finance. "
        "The verified user ID is in session state as state['uid'], and current UI page is state['current_page']. "
        "When calling any data tool that accepts `uid`, ALWAYS pass state['uid'] as the `uid` argument. "
        "Never invent numbers or ask the user for their user ID. "
        "Route or resolve incoming questions:\n"
        "- Budget, spending, cash flow, safe-to-spend -> call analyze_budget_and_cashflow(uid=state['uid'])\n"
        "- Trials, cancellations, .ics reminders, subscriptions -> call check_user_trials(uid=state['uid'])\n"
        "- Loans, debts, credit score, card payoff, avalanche/snowball -> call calculate_debt_payoff_plans(uid=state['uid'])\n"
        "- Macro news, inflation, Federal Reserve, economy pulse -> call search_financial_news()\n"
        "- Lessons, tax figures, IRAs, HSAs, financial education -> explain with accurate 2026 limits (IRA $7,500)\n"
        "- All monetary math must be deterministic. Maintain an empowering, bank-grade professional tone."
    ),
    tools=[
        tools.get_user_profile,
        tools.analyze_budget_and_cashflow,
        tools.check_user_trials,
        tools.calculate_debt_payoff_plans,
        tools.search_financial_news,
        tools.run_financial_sandbox_calc,
    ],
    sub_agents=[
        budget_agent,
        trial_agent,
        debt_agent,
        news_agent,
        learn_agent,
        game_agent,
    ],
)

app = App(
    root_agent=coordinator_agent,
    name="futurewise_v2_coordinator",
)
