# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.app_utils import (
    firestore_tools,
    futurewise_tools,
    image_tools,
    chart_tools,
    sandbox_finance_tools,
    rag_knowledge,
)

MODEL = "gemini-2.5-flash"


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session to Memory Bank for extraction."""
    try:
        await callback_context.add_session_to_memory()
    except ValueError as e:
        if "memory service is not available" not in str(e).lower():
            raise
    return None


def get_weather(query: str) -> str:
    """Simulates a web search for weather."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are Futurewise, an AI personal finance assistant that guides users toward financial stability.\n"
        "Tagline: 'Learn it. Track it. Play it forward.'\n"
        "Unless specified otherwise by the user, the default user ID is 'taylor_nyc_27'.\n\n"
        "Core Capabilities:\n"
        "1. MONEY BRIEF: When the user asks for their Money Brief, provide an executive summary containing:\n"
        "   - Free trials ending soon (from check_trials)\n"
        "   - Budget status (from run_spending_analysis or Firestore)\n"
        "   - Financial stability check (run_stability_check: months of expenses covered, savings rate, high-interest debt status)\n"
        "   - One economy headline explained in plain English (via search_sub_agent)\n\n"
        "2. LEARN & RAG: Use consult_learn_rag to ground educational answers in IRS Publication 969, IRS Publication 590-A, or CFPB 'Your Money, Your Goals'.\n"
        "   - ALWAYS cite and name the official publication used.\n"
        "   - Use compare_hsa_vs_fsa and compare_roth_vs_traditional to calculate exact numbers in the sandbox.\n\n"
        "3. BUDGET & TRIAL GUARD:\n"
        "   - Track free trials with add_trial and check_trials. Enforce the conservative rule for App Store trials (cancel 2 days prior).\n"
        "   - Create calendar reminder .ics links with create_trial_reminder.\n"
        "   - Log expenses with log_expense and compute spending breakdown with run_spending_analysis.\n\n"
        "4. SANDBOX CODE EXECUTION & CHARTS:\n"
        "   - Run Python code in the sandbox with execute_sandbox_code (e.g. for fizzbuzz, financial formulas).\n"
        "   - Generate charts with make_chart and visual illustrations with generate_futurewise_image.\n\n"
        "5. LIFE SIMULATOR:\n"
        "   - Run life simulation with run_life_simulation (5 chapters from Firestore events, fixed random seed, 1,000-lives replay, and decision score).\n"
        "   - Generate chapter images with generate_futurewise_image.\n\n"
        "You also have persistent long-term memory across sessions. Proactively remember user goals, completed lessons, and recurring subscriptions."
    ),
    tools=[
        PreloadMemoryTool(),
        # Trial Guard & Calendar
        futurewise_tools.add_trial,
        futurewise_tools.check_trials,
        futurewise_tools.create_trial_reminder,
        # Search & Economy
        futurewise_tools.search_agent_tool,
        # Expense & Spending
        futurewise_tools.log_expense,
        futurewise_tools.get_spending_summary,
        # Sandbox & Finance Analytics
        sandbox_finance_tools.execute_sandbox_code,
        sandbox_finance_tools.run_spending_analysis,
        sandbox_finance_tools.run_stability_check,
        sandbox_finance_tools.compare_hsa_vs_fsa,
        sandbox_finance_tools.compare_roth_vs_traditional,
        sandbox_finance_tools.run_life_simulation,
        # Images & Charts
        image_tools.generate_futurewise_image,
        chart_tools.make_chart,
        # RAG Knowledge
        rag_knowledge.consult_learn_rag,
        # Firestore Direct Access
        firestore_tools.read_user_profile,
        firestore_tools.update_user_profile,
        firestore_tools.read_recent_transactions,
        firestore_tools.read_user_budgets,
        firestore_tools.set_category_budget,
        firestore_tools.read_user_goals,
        firestore_tools.save_user_goal,
        firestore_tools.read_account_limits,
        firestore_tools.read_life_events,
        firestore_tools.read_user_simulation_games,
        firestore_tools.save_user_simulation_game,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
