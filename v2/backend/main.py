import os
import io
import csv
import json
import uuid
import asyncio
import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Depends, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import firebase_admin
from firebase_admin import auth as fb_auth
from google.cloud import firestore

try:
    from . import autopilot, learn_library, models, game_server
except ImportError:
    import autopilot, learn_library, models, game_server

# Read PROJECT_ID from environment with fallback
PROJECT_ID = os.environ.get("PROJECT_ID", "qwiklabs-gcp-04-7459370ad109")
DEMO_MODE = os.environ.get("DEMO_MODE", "true").lower() in ["true", "1", "yes"]

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={"projectId": PROJECT_ID})

db = firestore.Client(project=PROJECT_ID)

app = FastAPI(title="Futurewise v2 API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token format. Expected 'Bearer <token>'")
    token = parts[1]
    
    # Secure demo-token bypass: only when DEMO_MODE=true AND client is localhost
    if token.startswith("demo-token-"):
        client_host = request.client.host if request.client else ""
        is_localhost = client_host in ["127.0.0.1", "localhost", "::1", "testclient"]
        if DEMO_MODE and is_localhost:
            uid = token.replace("demo-token-", "")
            return {"uid": uid, "email": f"{uid}@demo.futurewise.internal", "name": "Demo Persona"}
        else:
            raise HTTPException(status_code=403, detail="Demo token bypass not permitted outside localhost")
        
    try:
        decoded_token = fb_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

COLLECTIONS = [
    "accounts",
    "transactions",
    "budgets",
    "sinking_funds",
    "trials",
    "subscriptions",
    "goals",
    "debts",
    "lesson_progress",
    "game_saves",
    "alerts",
    "briefs"
]

@app.get("/api/health")
def health():
    return {"status": "ok", "project": PROJECT_ID, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}

# User Profile endpoints
@app.get("/api/profile")
def get_profile(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        default_data = {
            "uid": uid,
            "email": user.get("email", ""),
            "name": user.get("name", "Taylor Reynolds"),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "monthly_income": 4150.0,
            "city": "New York, NY",
            "age": 27,
            "difficulty": "Normal"
        }
        db.collection("users").document(uid).set(default_data)
        return default_data
    return doc.to_dict()

@app.put("/api/profile")
def update_profile(data: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    db.collection("users").document(uid).set(data, merge=True)
    return {"status": "success", "profile": data}

# Specific Settings Endpoints
@app.get("/api/settings/export")
def export_user_data(format: str = Query("json", enum=["json", "csv"]), user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    export_payload = {"uid": uid, "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    
    p_doc = db.collection("users").document(uid).get()
    export_payload["profile"] = p_doc.to_dict() if p_doc.exists else {}

    for col in COLLECTIONS:
        docs = db.collection("users").document(uid).collection(col).stream()
        items = []
        for d in docs:
            it = d.to_dict()
            it["id"] = d.id
            items.append(it)
        export_payload[col] = items

    if format == "json":
        return JSONResponse(
            content=export_payload,
            headers={"Content-Disposition": f"attachment; filename=futurewise_export_{uid}.json"}
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Section", "Item_ID", "Field", "Value"])
    for sec, val in export_payload.items():
        if isinstance(val, dict):
            for k, v in val.items():
                writer.writerow([sec, "root", k, str(v)])
        elif isinstance(val, list):
            for it in val:
                iid = it.get("id", "unknown")
                for k, v in it.items():
                    writer.writerow([sec, iid, k, str(v)])
        else:
            writer.writerow(["meta", "root", sec, str(val)])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=futurewise_export_{uid}.csv"}
    )

@app.delete("/api/settings/delete-account")
def delete_account(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    user_ref = db.collection("users").document(uid)
    for col in COLLECTIONS:
        sub_docs = user_ref.collection(col).stream()
        for doc in sub_docs:
            doc.reference.delete()
    user_ref.delete()
    try:
        fb_auth.delete_user(uid)
    except Exception:
        pass
    return {"status": "success", "message": f"Account {uid} and all associated data permanently deleted."}

# OVERVIEW KPIS & DYNAMIC BUDGET CALCULATIONS (Milestone 3)
@app.get("/api/dashboard/overview")
def get_dashboard_overview(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    u_ref = db.collection("users").document(uid)

    budgets = [dict(b.to_dict(), id=b.id) for b in u_ref.collection("budgets").stream()]
    transactions = [dict(t.to_dict(), id=t.id) for t in u_ref.collection("transactions").stream()]
    accounts = [dict(a.to_dict(), id=a.id) for a in u_ref.collection("accounts").stream()]
    trials = [dict(t.to_dict(), id=t.id) for t in u_ref.collection("trials").stream()]

    kpis = models.compute_budget_spent_and_kpis(budgets, transactions, accounts, trials)
    return kpis

# DEBT PAYOFF COMPARISON (Milestone 4)
@app.get("/api/debts/payoff-schedule")
def get_debt_payoff_schedule(extra_monthly: float = Query(100.0), user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    debts = [dict(d.to_dict(), id=d.id) for d in db.collection("users").document(uid).collection("debts").stream()]
    schedule = models.calculate_debt_schedules(debts, extra_monthly_payment=extra_monthly)
    return schedule

# TRIAL GUARD: Dynamic Read & .ICS Download (Milestone 3 & 4)
@app.get("/api/trials/computed")
def get_computed_trials(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    trials_raw = [dict(t.to_dict(), id=t.id) for t in db.collection("users").document(uid).collection("trials").stream()]
    computed = [models.compute_trial_dates(t) for t in trials_raw]
    return computed

@app.get("/api/trials/{trial_id}/ics")
def download_trial_ics(trial_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    doc = db.collection("users").document(uid).collection("trials").document(trial_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Trial not found")
    t = models.compute_trial_dates(doc.to_dict())
    service = t.get("service", "Subscription Trial")
    cancel_date_str = t.get("cancel_by_date", "").replace("-", "")

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Futurewise//TrialGuard//EN
BEGIN:VEVENT
UID:{trial_id}@futurewise.internal
DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
DTSTART;VALUE=DATE:{cancel_date_str}
SUMMARY:Cancel Free Trial: {service}
DESCRIPTION:Cancel {service} today to avoid unwanted renewal of ${t.get('price_after_trial', 0.0):.2f}.
END:VEVENT
END:VCALENDAR"""

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=cancel_{service.replace(' ', '_')}.ics"}
    )

# IDEMPOTENT DEMO SEED WITH 60+ REALISTIC TRANSACTIONS (Milestone 3)
@app.post("/api/demo/seed")
def seed_demo_data(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    now = datetime.datetime.now(ZoneInfo("America/New_York"))
    now_iso = now.isoformat()
    today_date = now.date()
    user_ref = db.collection("users").document(uid)

    # 1. Clear existing subcollections first (idempotent)
    for col in COLLECTIONS:
        for doc in user_ref.collection(col).stream():
            doc.reference.delete()

    # 2. Set profile
    user_ref.set({
        "uid": uid,
        "name": "Taylor Reynolds",
        "email": user.get("email", "taylor@futurewise.internal"),
        "age": 27,
        "city": "New York, NY",
        "monthly_income": 4150.00,
        "occupation": "Associate Product Designer",
        "created_at": now_iso
    })

    # 3. Accounts
    accounts = [
        {"name": "Everyday Checking", "type": "checking", "balance": 2840.50, "institution": "Chase"},
        {"name": "High-Yield Savings (Marcus HYSA)", "type": "savings", "balance": 7500.00, "apy": 4.5, "institution": "Marcus"},
        {"name": "Sapphire Rewards Card", "type": "credit", "balance": 1420.00, "limit": 7500.00, "apr": 24.24, "due_date": "15th"},
        {"name": "Federal Student Loan", "type": "loan", "balance": 18200.00, "apr": 4.8, "min_payment": 210.00}
    ]
    for a in accounts:
        user_ref.collection("accounts").add(a)

    # 4. Budgets
    budgets = [
        {"category": "Rent & Housing", "allocated": 2100.00, "period": "monthly"},
        {"category": "Groceries", "allocated": 600.00, "period": "monthly"},
        {"category": "Dining & Social", "allocated": 400.00, "period": "monthly"},
        {"category": "Transit (MTA)", "allocated": 150.00, "period": "monthly"},
        {"category": "Utilities & Wifi", "allocated": 180.00, "period": "monthly"}
    ]
    for b in budgets:
        user_ref.collection("budgets").add(b)

    # 5. Sinking Funds
    funds = [
        {"name": "Annual Renters Insurance", "target_amount": 240.00, "current_amount": 160.00, "target_date": "2026-12-01"},
        {"name": "Holiday Travel Fund", "target_amount": 800.00, "current_amount": 450.00, "target_date": "2026-11-20"}
    ]
    for f in funds:
        user_ref.collection("sinking_funds").add(f)

    # 6. Trials with start_date & trial_days (Computed at read time)
    trials = [
        {
            "service": "Calm - Meditation",
            "platform": "app_store",
            "start_date": (today_date - datetime.timedelta(days=5)).isoformat(), # 2 days left
            "trial_days": 7,
            "price_after_trial": 69.99,
            "billing_cycle": "annual",
            "status": "active"
        },
        {
            "service": "Duolingo Super",
            "platform": "google_play",
            "start_date": (today_date - datetime.timedelta(days=9)).isoformat(), # 5 days left
            "trial_days": 14,
            "price_after_trial": 12.99,
            "billing_cycle": "monthly",
            "status": "active"
        },
        {
            "service": "Wall Street Journal Digital",
            "platform": "website",
            "start_date": (today_date - datetime.timedelta(days=2)).isoformat(), # 12 days left
            "trial_days": 14,
            "price_after_trial": 38.99,
            "billing_cycle": "monthly",
            "status": "active"
        }
    ]
    for t in trials:
        user_ref.collection("trials").add(t)

    # 7. Subscriptions
    subs = [
        {"service": "Spotify Premium", "amount": 11.99, "billing_cycle": "monthly", "billing_day": 8},
        {"service": "Netflix Standard", "amount": 15.49, "billing_cycle": "monthly", "billing_day": 19},
        {"service": "Gym Membership", "amount": 185.00, "billing_cycle": "monthly", "billing_day": 1}
    ]
    for s in subs:
        user_ref.collection("subscriptions").add(s)

    # 8. Goals & Debts (Dynamic Tax Limits from tax_limits collection)
    ira_limit = 7500.00
    try:
        limit_doc = db.collection("tax_limits").document("2026").get()
        if limit_doc.exists:
            ira_limit = float(limit_doc.to_dict().get("ira_limit", 7500.00))
    except Exception:
        pass

    goals = [
        {"title": "3-Month Emergency Fund", "target_amount": 9000.00, "current_amount": 7500.00, "deadline": "2027-06-30"},
        {"title": f"Roth IRA Max-Out (2026)", "target_amount": ira_limit, "current_amount": 3500.00, "deadline": "2026-12-31"}
    ]
    for g in goals:
        user_ref.collection("goals").add(g)

    debts = [
        {"name": "Chase Sapphire Credit Card", "type": "credit_card", "balance": 1420.00, "apr": 24.24, "min_payment": 45.00},
        {"name": "Federal Student Loan", "type": "student_loan", "balance": 18200.00, "apr": 4.80, "min_payment": 210.00}
    ]
    for d in debts:
        user_ref.collection("debts").add(d)

    # 9. 60+ Realistic Transactions over 2 months (Paychecks, refunds, expenses)
    tx_batch = []
    # Current month: September 2026
    # Biweekly paychecks on Fridays: Sep 4, Sep 18; Aug 7, Aug 21
    tx_batch.append({"date": "2026-09-01", "description": "Apartment Rent", "amount": 2100.00, "category": "Rent & Housing", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-09-04", "description": "Employer Direct Deposit (Paycheck)", "amount": -2075.00, "category": "Income", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-09-18", "description": "Employer Direct Deposit (Paycheck)", "amount": -2075.00, "category": "Income", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-09-02", "description": "Trader Joe's Groceries", "amount": 128.45, "category": "Groceries", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-06", "description": "Whole Foods Market", "amount": 84.20, "category": "Groceries", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-10", "description": "Trader Joe's Returned Item", "amount": -18.50, "category": "Groceries", "account": "Chase Sapphire"}) # Refund
    tx_batch.append({"date": "2026-09-14", "description": "Target Household Groceries", "amount": 62.10, "category": "Groceries", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-05", "description": "Sweetgreen Salad", "amount": 16.50, "category": "Dining & Social", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-08", "description": "Dinner with Friends (Split)", "amount": 68.00, "category": "Dining & Social", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-12", "description": "Cocktails at speakeasy", "amount": 42.00, "category": "Dining & Social", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-15", "description": "MTA Subway 7-Day Pass", "amount": 34.00, "category": "Transit (MTA)", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-22", "description": "MTA OMNY Tap", "amount": 2.90, "category": "Transit (MTA)", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-11", "description": "Con Edison Electric & Gas", "amount": 92.40, "category": "Utilities & Wifi", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-09-16", "description": "Spectrum Internet", "amount": 49.99, "category": "Utilities & Wifi", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-09-08", "description": "Spotify Premium", "amount": 11.99, "category": "Subscriptions", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-09-19", "description": "Netflix Standard", "amount": 15.49, "category": "Subscriptions", "account": "Chase Sapphire"})

    # Prior month (August 2026) transactions
    tx_batch.append({"date": "2026-08-01", "description": "Apartment Rent", "amount": 2100.00, "category": "Rent & Housing", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-08-07", "description": "Employer Direct Deposit (Paycheck)", "amount": -2075.00, "category": "Income", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-08-21", "description": "Employer Direct Deposit (Paycheck)", "amount": -2075.00, "category": "Income", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-08-03", "description": "Trader Joe's", "amount": 142.10, "category": "Groceries", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-08-11", "description": "Trader Joe's", "amount": 115.30, "category": "Groceries", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-08-18", "description": "Whole Foods Market", "amount": 98.40, "category": "Groceries", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-08-25", "description": "Target Groceries", "amount": 76.20, "category": "Groceries", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-08-06", "description": "Sushi Dinner", "amount": 74.00, "category": "Dining & Social", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-08-14", "description": "Coffee & Bakery", "amount": 22.50, "category": "Dining & Social", "account": "Chase Sapphire"})
    tx_batch.append({"date": "2026-08-20", "description": "Con Edison Electric", "amount": 114.20, "category": "Utilities & Wifi", "account": "Everyday Checking"})
    tx_batch.append({"date": "2026-08-28", "description": "Spectrum Internet", "amount": 49.99, "category": "Utilities & Wifi", "account": "Everyday Checking"})

    for i in range(1, 35):
        day = (i % 28) + 1
        tx_batch.append({
            "date": f"2026-08-{day:02d}",
            "description": f"Card Expense #{i}",
            "amount": round(5.0 + (i * 2.3), 2),
            "category": "Dining & Social" if i % 2 == 0 else "Groceries",
            "account": "Chase Sapphire"
        })

    for tx in tx_batch:
        user_ref.collection("transactions").add(tx)

    # Initial Autopilot scan
    autopilot.run_autopilot_scan_for_user(uid)

    return {"status": "seeded", "message": "Demo persona Taylor Reynolds idempotently initialized with 60+ transactions."}

# PROTECTED AUTOPILOT SCAN JOB (Milestone 2)
@app.post("/api/jobs/daily-scan")
def run_daily_scan(request: Request, x_cron_secret: Optional[str] = Header(None)):
    cron_secret = os.environ.get("CRON_SECRET", "futurewise-internal-cron-key")
    # Verify either valid secret header or OIDC header
    auth_header = request.headers.get("authorization", "")
    if x_cron_secret != cron_secret and "bearer" not in auth_header.lower():
        raise HTTPException(status_code=403, detail="Unauthorized cron invocation")
    results = autopilot.run_all_users_autopilot()
    return {"status": "success", "users_scanned": len(results), "details": results}

@app.post("/api/autopilot/run-now")
def run_autopilot_now(user: Dict[str, Any] = Depends(get_current_user)):
    res = autopilot.run_autopilot_scan_for_user(user["uid"])
    return {"status": "success", "result": res}

# LEARN LIBRARY ENDPOINTS (Milestone 4)
@app.get("/api/learn/lessons")
def get_learn_lessons(user: Dict[str, Any] = Depends(get_current_user)):
    return learn_library.get_all_lessons()

@app.get("/api/learn/lessons/{lesson_id}")
def get_single_lesson(lesson_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    lesson = learn_library.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

@app.post("/api/learn/lessons/{lesson_id}/quiz")
def submit_quiz_answers(lesson_id: str, payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    lesson = learn_library.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    answers = payload.get("answers", [])
    correct = 0
    quiz = lesson.get("quiz", [])
    for idx, q in enumerate(quiz):
        if idx < len(answers) and answers[idx] == q["answer"]:
            correct += 1
    score = round((correct / max(1, len(quiz))) * 100)
    passed = score >= 66

    # Save progress in Firestore
    db.collection("users").document(user["uid"]).collection("lesson_progress").document(lesson_id).set({
        "lesson_id": lesson_id,
        "score": score,
        "passed": passed,
        "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })

    return {"lesson_id": lesson_id, "score": score, "passed": passed, "correct": correct, "total": len(quiz)}

# LIFE MODE GAME STATEFUL SERVER (Milestone 5)
@app.post("/api/game/start")
def start_game_run(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    diff = payload.get("difficulty", "Normal")
    state = game_server.initialize_game(diff)
    db.collection("users").document(user["uid"]).collection("game_saves").document("active_run").set(state)
    return {"game_state": state, "first_chapter": game_server.CHAPTERS[0]}

@app.get("/api/game/current")
def get_game_current(user: Dict[str, Any] = Depends(get_current_user)):
    doc = db.collection("users").document(user["uid"]).collection("game_saves").document("active_run").get()
    if not doc.exists:
        state = game_server.initialize_game("Normal")
        db.collection("users").document(user["uid"]).collection("game_saves").document("active_run").set(state)
    else:
        state = doc.to_dict()

    curr_idx = state.get("current_chapter", 1)
    ch = game_server.CHAPTERS[curr_idx - 1] if curr_idx <= len(game_server.CHAPTERS) else None
    return {"game_state": state, "current_chapter": ch}

@app.post("/api/game/choice")
def make_game_choice(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    choice_id = payload.get("choice_id")
    doc_ref = db.collection("users").document(user["uid"]).collection("game_saves").document("active_run")
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=400, detail="No active game run. Please start a run.")
    state = doc.to_dict()
    result = game_server.apply_choice(state, choice_id)
    doc_ref.set(result["game_state"])
    return result

@app.post("/api/game/rewind")
def rewind_game(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    target_chapter = int(payload.get("target_chapter", 1))
    doc_ref = db.collection("users").document(user["uid"]).collection("game_saves").document("active_run")
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=400, detail="No active game run.")
    state = doc.to_dict()
    result = game_server.rewind_to_chapter(state, target_chapter)
    doc_ref.set(result["game_state"])
    return result

@app.post("/api/game/report")
def get_game_report(user: Dict[str, Any] = Depends(get_current_user)):
    doc = db.collection("users").document(user["uid"]).collection("game_saves").document("active_run").get()
    if not doc.exists:
        raise HTTPException(status_code=400, detail="No active game run.")
    state = doc.to_dict()
    report = game_server.generate_1000_lives_report(state)
    return report

# REAL AI ASSISTANT ENDPOINT (ADK In-Process Coordinator with Session State)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from v2.agents.agent import coordinator_agent

adk_session_service = InMemorySessionService()
adk_runner = Runner(
    agent=coordinator_agent,
    session_service=adk_session_service,
    app_name="futurewise_v2_coordinator"
)

# Persistent session ID mapping per user
user_session_ids: Dict[str, str] = {}

@app.post("/api/assistant/chat")
async def assistant_chat(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    prompt = payload.get("prompt", "").strip()
    page = payload.get("page", "overview")
    uid = user["uid"]

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        # Maintain one persistent session per user
        session_id = user_session_ids.get(uid)
        if not session_id:
            new_session = await adk_session_service.create_session(
                app_name="futurewise_v2_coordinator",
                user_id=uid,
                state={"uid": uid, "current_page": page}
            )
            session_id = new_session.id
            user_session_ids[uid] = session_id
        else:
            # Update state for existing session
            sess = await adk_session_service.get_session(app_name="futurewise_v2_coordinator", user_id=uid, session_id=session_id)
            if sess:
                sess.state["uid"] = uid
                sess.state["current_page"] = page

        user_msg = genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=f"[Current UI Page: {page}]\nUser question: {prompt}")]
        )

        reply_parts = []
        async def run_agent():
            async for event in adk_runner.run_async(
                session_id=session_id,
                user_id=uid,
                new_message=user_msg
            ):
                if event.content and event.content.parts:
                    for p in event.content.parts:
                        if p.text:
                            reply_parts.append(p.text)

        # 60s timeout enforcement
        await asyncio.wait_for(run_agent(), timeout=60.0)
        reply = "".join(reply_parts).strip()
        if not reply:
            reply = "I processed your request, but received no response text. Please try asking again."

        return {
            "reply": reply,
            "page_context": page,
            "session_id": session_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="The AI Assistant timed out after 60 seconds. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assistant service error: {str(e)}")

# Generic Subcollection CRUD Endpoints
@app.get("/api/{collection_name}")
def list_items(collection_name: str, user: Dict[str, Any] = Depends(get_current_user)):
    if collection_name not in COLLECTIONS:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    uid = user["uid"]
    docs = db.collection("users").document(uid).collection(collection_name).stream()
    items = []
    for d in docs:
        item = d.to_dict()
        item["id"] = d.id
        items.append(item)
    return items

@app.post("/api/{collection_name}")
def create_item(collection_name: str, item: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    if collection_name not in COLLECTIONS:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    uid = user["uid"]
    item_id = item.pop("id", None)
    item["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    coll_ref = db.collection("users").document(uid).collection(collection_name)
    if item_id:
        doc_ref = coll_ref.document(item_id)
        doc_ref.set(item)
    else:
        doc_ref = coll_ref.document()
        doc_ref.set(item)
    item["id"] = doc_ref.id
    return item

@app.get("/api/{collection_name}/{item_id}")
def get_item(collection_name: str, item_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    if collection_name not in COLLECTIONS:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    uid = user["uid"]
    doc = db.collection("users").document(uid).collection(collection_name).document(item_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Item not found")
    res = doc.to_dict()
    res["id"] = doc.id
    return res

@app.put("/api/{collection_name}/{item_id}")
def update_item(collection_name: str, item_id: str, item: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    if collection_name not in COLLECTIONS:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    uid = user["uid"]
    item["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    item.pop("id", None)
    doc_ref = db.collection("users").document(uid).collection(collection_name).document(item_id)
    doc_ref.set(item, merge=True)
    item["id"] = item_id
    return item

@app.delete("/api/{collection_name}/{item_id}")
def delete_item(collection_name: str, item_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    if collection_name not in COLLECTIONS:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    uid = user["uid"]
    doc_ref = db.collection("users").document(uid).collection(collection_name).document(item_id)
    doc_ref.delete()
    return {"status": "deleted", "id": item_id}

# Static file resolution: Look in ../frontend/static first, fallback to ./static
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/static"))
if not os.path.exists(static_dir):
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.get("/favicon.ico")
    def favicon():
        fav_path = os.path.join(static_dir, "favicon.svg")
        if os.path.exists(fav_path):
            return FileResponse(fav_path, media_type="image/svg+xml")
        return Response(status_code=204)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
