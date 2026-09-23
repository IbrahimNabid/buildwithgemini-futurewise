import os
import io
import csv
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

import firebase_admin
from firebase_admin import auth as fb_auth
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"
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

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token format. Expected 'Bearer <token>'")
    token = parts[1]
    
    if token.startswith("demo-token-"):
        uid = token.replace("demo-token-", "")
        return {"uid": uid, "email": f"{uid}@demo.futurewise.internal", "name": "Demo Persona"}
        
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
    return {"status": "ok", "project": PROJECT_ID, "timestamp": datetime.now(timezone.utc).isoformat()}

# User Profile endpoints
@app.get("/api/profile")
def get_profile(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        default_data = {
            "uid": uid,
            "email": user.get("email", ""),
            "name": user.get("name", "User"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "monthly_income": 0.0,
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
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    db.collection("users").document(uid).set(data, merge=True)
    return {"status": "success", "profile": data}

# Specific Settings Endpoints placed BEFORE generic subcollection endpoints
@app.get("/api/settings/export")
def export_user_data(format: str = Query("json", enum=["json", "csv"]), user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    export_payload = {"uid": uid, "exported_at": datetime.now(timezone.utc).isoformat()}
    
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

# Load Demo Data
@app.post("/api/demo/seed")
def seed_demo_data(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["uid"]
    now_iso = datetime.now(timezone.utc).isoformat()
    
    user_ref = db.collection("users").document(uid)
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

    accounts = [
        {"name": "Everyday Checking", "type": "checking", "balance": 2840.50, "institution": "Chase"},
        {"name": "High-Yield Savings (HYSA)", "type": "savings", "balance": 4350.00, "apy": 4.5, "institution": "Marcus"},
        {"name": "Sapphire Rewards Card", "type": "credit", "balance": 1420.00, "limit": 7500.00, "apr": 24.24, "due_date": "15th"},
        {"name": "Federal Student Loan", "type": "loan", "balance": 18200.00, "apr": 4.8, "min_payment": 210.00}
    ]
    for a in accounts:
        user_ref.collection("accounts").document().set(a)

    budgets = [
        {"category": "Rent & Housing", "allocated": 2100.00, "spent": 2100.00, "period": "monthly"},
        {"category": "Groceries", "allocated": 600.00, "spent": 425.30, "period": "monthly"},
        {"category": "Dining & Social", "allocated": 400.00, "spent": 385.40, "period": "monthly"},
        {"category": "Transit (MTA)", "allocated": 150.00, "spent": 127.00, "period": "monthly"},
        {"category": "Utilities & Wifi", "allocated": 180.00, "spent": 142.10, "period": "monthly"}
    ]
    for b in budgets:
        user_ref.collection("budgets").document().set(b)

    funds = [
        {"name": "Annual Renters Insurance", "target_amount": 240.00, "current_amount": 160.00, "target_date": "2026-12-01"},
        {"name": "Holiday Travel Fund", "target_amount": 800.00, "current_amount": 450.00, "target_date": "2026-11-20"}
    ]
    for f in funds:
        user_ref.collection("sinking_funds").document().set(f)

    trials = [
        {"service": "Calm - Meditation", "platform": "app_store", "days_left": 2, "cost_if_forgotten": 69.99, "cancel_by_date": "2026-09-24", "status": "active"},
        {"service": "Duolingo Super", "platform": "google_play", "days_left": 5, "cost_if_forgotten": 12.99, "cancel_by_date": "2026-09-27", "status": "active"},
        {"service": "Wall Street Journal Digital", "platform": "website", "days_left": 12, "cost_if_forgotten": 38.99, "cancel_by_date": "2026-10-04", "status": "active"}
    ]
    for t in trials:
        user_ref.collection("trials").document().set(t)

    subs = [
        {"service": "Spotify Premium", "amount": 11.99, "billing_cycle": "monthly", "billing_day": 8},
        {"service": "Netflix Standard", "amount": 15.49, "billing_cycle": "monthly", "billing_day": 19},
        {"service": "Gym Membership (Equinox)", "amount": 185.00, "billing_cycle": "monthly", "billing_day": 1}
    ]
    for s in subs:
        user_ref.collection("subscriptions").document().set(s)

    goals = [
        {"title": "3-Month Emergency Fund", "target_amount": 9000.00, "current_amount": 4350.00, "deadline": "2027-06-30"},
        {"title": "Roth IRA Max-Out (2026)", "target_amount": 7000.00, "current_amount": 2500.00, "deadline": "2026-12-31"}
    ]
    for g in goals:
        user_ref.collection("goals").document().set(g)

    debts = [
        {"name": "Chase Sapphire Credit Card", "type": "credit_card", "balance": 1420.00, "apr": 24.24, "min_payment": 45.00},
        {"name": "Federal Student Loan", "type": "student_loan", "balance": 18200.00, "apr": 4.80, "min_payment": 210.00}
    ]
    for d in debts:
        user_ref.collection("debts").document().set(d)

    user_ref.collection("alerts").document().set({
        "type": "warning",
        "title": "Calm Trial Renews in 2 Days",
        "message": "Cancel before September 24 to prevent an annual renewal charge of $69.99.",
        "created_at": now_iso
    })
    user_ref.collection("briefs").document().set({
        "title": "Welcome to Futurewise v2",
        "summary": "Your financial accounts and trials are loaded. Emergency runway is currently at 1.4 months with a 21.6% savings rate.",
        "created_at": now_iso
    })

    return {"status": "seeded", "message": "Demo persona Taylor Reynolds successfully populated."}

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
    item["created_at"] = datetime.now(timezone.utc).isoformat()
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
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
