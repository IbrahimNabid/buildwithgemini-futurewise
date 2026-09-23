import random
from typing import Dict, Any, List

CHAPTERS = [
    {
        "chapter_index": 1,
        "age": 27,
        "title": "First Career Crossroads & Signing Bonus",
        "description": "You've been offered a new role with a $5,000 upfront signing bonus. But your apartment lease is also expiring with a $200/month rent bump.",
        "choices": [
            {
                "id": "fund_emergency",
                "text": "Stash $4,000 in your High-Yield Savings Account and move to a modest apartment.",
                "cash_change": 4000.0,
                "debt_change": 0.0,
                "net_worth_change": 4000.0,
                "credit_score_change": 5,
                "stress_change": -10,
                "happiness_change": 10,
                "lesson_unlocked": "hysa-vs-checking",
                "lesson_title": "High-Yield Savings vs Checking",
                "feedback": "Prudent move! You established a cash cushion before life threw its first curveball."
            },
            {
                "id": "lifestyle_upgrade",
                "text": "Splurge on a luxury high-rise apartment and buy new designer furniture with the bonus.",
                "cash_change": -1500.0,
                "debt_change": 2500.0,
                "net_worth_change": -4000.0,
                "credit_score_change": -10,
                "stress_change": 20,
                "happiness_change": 15,
                "lesson_unlocked": "paystub-basics",
                "lesson_title": "Paystub Basics & Fixed Costs",
                "feedback": "The apartment looks stunning on Instagram, but fixed monthly overhead is now squeezing your monthly cash flow."
            }
        ]
    },
    {
        "chapter_index": 2,
        "age": 29,
        "title": "The Healthcare Surprise: Emergency Room Bill",
        "description": "A bad fall during a weekend hike leaves you with an emergency room visit and an unexpected $3,200 out-of-pocket medical bill.",
        "choices": [
            {
                "id": "itemized_bill_hsa",
                "text": "Request an itemized bill, negotiate a 20% prompt-pay discount, and pay from your savings.",
                "cash_change": -2560.0,
                "debt_change": 0.0,
                "net_worth_change": -2560.0,
                "credit_score_change": 5,
                "stress_change": 5,
                "happiness_change": 0,
                "lesson_unlocked": "hsa-vs-fsa-rules",
                "lesson_title": "HSA vs FSA Triple Tax Advantage",
                "feedback": "Brilliant! Asking for an itemized bill caught billing errors and saved you over $600."
            },
            {
                "id": "credit_card_panic",
                "text": "Charge the full $3,200 bill to your high-interest credit card without questioning the charges.",
                "cash_change": 0.0,
                "debt_change": 3200.0,
                "net_worth_change": -3200.0,
                "credit_score_change": -25,
                "stress_change": 30,
                "happiness_change": -10,
                "lesson_unlocked": "credit-utilization-grace-periods",
                "lesson_title": "Credit Utilization & Statement Grace Periods",
                "feedback": "At 24.24% APR, that $3,200 bill will cost you over $1,100 in compounding interest if not paid quickly."
            }
        ]
    },
    {
        "chapter_index": 3,
        "age": 31,
        "title": "Tech Layoff Wave & Emergency Runway",
        "description": "Your company announces sudden restructuring and eliminates 20% of the department with 4 weeks severance.",
        "choices": [
            {
                "id": "frugal_pivot",
                "text": "Pause all discretionary subscriptions, file for unemployment immediately, and tap your emergency reserve.",
                "cash_change": -2000.0,
                "debt_change": 0.0,
                "net_worth_change": -2000.0,
                "credit_score_change": 0,
                "stress_change": 15,
                "happiness_change": -5,
                "lesson_unlocked": "sinking-funds-annual-bills",
                "lesson_title": "Sinking Funds & Essential Budgets",
                "feedback": "Your emergency fund did its exact job: kept a roof over your head and kept you debt-free during the transition."
            },
            {
                "id": "credit_card_stack",
                "text": "Maintain your current spending habits on credit cards while looking for an executive role.",
                "cash_change": 0.0,
                "debt_change": 6500.0,
                "net_worth_change": -6500.0,
                "credit_score_change": -35,
                "stress_change": 40,
                "happiness_change": -20,
                "lesson_unlocked": "debt-avalanche-vs-snowball",
                "lesson_title": "Debt Avalanche vs Snowball",
                "feedback": "Stacking debt during unemployment severely damages your debt-to-income ratio and financial flexibility."
            }
        ]
    },
    {
        "chapter_index": 4,
        "age": 33,
        "title": "The Crypto 'Guaranteed Returns' Scam",
        "description": "A close acquaintance invites you to a private Telegram channel promising guaranteed 15% monthly returns on a new DeFi staking pool.",
        "choices": [
            {
                "id": "pass_scam",
                "text": "Politely decline, report the scheme, and invest into your broad S&P 500 index fund instead.",
                "cash_change": -1000.0,
                "debt_change": 0.0,
                "net_worth_change": 500.0,
                "credit_score_change": 5,
                "stress_change": -5,
                "happiness_change": 10,
                "lesson_unlocked": "identity-theft-credit-freezes",
                "lesson_title": "Spotting Scams & Credit Freezes",
                "feedback": "Sharp instincts! Three weeks later, the anonymous pool admins pulled the liquidity and vanished."
            },
            {
                "id": "gamble_fund",
                "text": "Transfer $5,000 of your emergency savings into the token to chase quick gains.",
                "cash_change": -5000.0,
                "debt_change": 0.0,
                "net_worth_change": -5000.0,
                "credit_score_change": 0,
                "stress_change": 35,
                "happiness_change": -30,
                "lesson_unlocked": "index-funds-vs-stock-picking",
                "lesson_title": "Broad Index Funds vs Stock Speculation",
                "feedback": "The pool crashed to zero. High guaranteed returns without risk do not exist in finance."
            }
        ]
    },
    {
        "chapter_index": 5,
        "age": 35,
        "title": "The Employer 401(k) Match & Debt-Free Summit",
        "description": "At your new senior position, the company offers a 100% 401(k) match on up to 6% of your $95,000 salary.",
        "choices": [
            {
                "id": "maximize_match",
                "text": "Contribute the full 6% to capture the 100% employer match and allocate excess cash to payoff remaining loans.",
                "cash_change": 5700.0,
                "debt_change": -5000.0,
                "net_worth_change": 10700.0,
                "credit_score_change": 30,
                "stress_change": -25,
                "happiness_change": 25,
                "lesson_unlocked": "401k-match-free-money",
                "lesson_title": "401(k) Employer Match: Instant 100% Return",
                "feedback": "You captured $5,700 of 100% free employer money every year, accelerating your path to financial independence!"
            },
            {
                "id": "opt_out_match",
                "text": "Opt out of retirement to maximize your weekly paycheck and finance a sports car.",
                "cash_change": -3000.0,
                "debt_change": 15000.0,
                "net_worth_change": -18000.0,
                "credit_score_change": -15,
                "stress_change": 20,
                "happiness_change": 5,
                "lesson_unlocked": "roth-vs-traditional-ira",
                "lesson_title": "Roth vs Traditional IRA",
                "feedback": "Opting out left over $50,000 of compounded employer contributions on the table over the next decade."
            }
        ]
    },
    {
        "chapter_index": 6,
        "age": 38,
        "title": "Home Buying: 20% Down vs First-Time Buyer Program",
        "description": "You're ready to purchase your first home. A $350,000 townhouse is on the market. How do you finance it?",
        "choices": [
            {
                "id": "prudent_downpayment",
                "text": "Put down 10%, keep a 6-month emergency reserve untouched, and budget for maintenance.",
                "cash_change": -35000.0,
                "debt_change": 315000.0,
                "net_worth_change": 0.0,
                "credit_score_change": 10,
                "stress_change": 5,
                "happiness_change": 20,
                "lesson_unlocked": "standard-deduction-2026",
                "lesson_title": "Standard Deduction & Homeownership",
                "feedback": "Keeping your cash reserve intact protected you from unexpected water heater and HVAC replacement bills."
            },
            {
                "id": "drain_reserves",
                "text": "Drain every dollar of your savings and retirement to hit 20% down and avoid PMI.",
                "cash_change": -70000.0,
                "debt_change": 280000.0,
                "net_worth_change": 0.0,
                "credit_score_change": 0,
                "stress_change": 35,
                "happiness_change": -5,
                "lesson_unlocked": "sinking-funds-annual-bills",
                "lesson_title": "Emergency Reserves for Homeowners",
                "feedback": "House rich but cash poor! A leaky roof 2 months after move-in forced you back onto high-interest credit cards."
            }
        ]
    }
]

def initialize_game(difficulty: str = "Normal") -> Dict[str, Any]:
    diff_multipliers = {
        "Easy": {"cash": 10000.0, "debt": 1000.0, "credit_score": 740, "stress": 15},
        "Normal": {"cash": 7190.0, "debt": 19620.0, "credit_score": 718, "stress": 25},
        "Hard": {"cash": 2500.0, "debt": 28000.0, "credit_score": 640, "stress": 45}
    }
    stats = diff_multipliers.get(difficulty, diff_multipliers["Normal"])
    return {
        "difficulty": difficulty,
        "current_chapter": 1,
        "stats": {
            "age": 27,
            "cash": stats["cash"],
            "debt": stats["debt"],
            "net_worth": stats["cash"] - stats["debt"],
            "credit_score": stats["credit_score"],
            "stress": stats["stress"],
            "happiness": 70
        },
        "history": [], # list of {chapter_index, choice_id, stats_after, unlocked_lesson}
        "is_finished": False
    }

def apply_choice(game_state: Dict[str, Any], choice_id: str) -> Dict[str, Any]:
    ch_idx = game_state["current_chapter"]
    if ch_idx > len(CHAPTERS):
        game_state["is_finished"] = True
        return game_state

    chapter = CHAPTERS[ch_idx - 1]
    choice = next((c for c in chapter["choices"] if c["id"] == choice_id), None)
    if not choice:
        raise ValueError(f"Invalid choice '{choice_id}' for chapter {ch_idx}")

    stats = game_state["stats"]
    stats["cash"] = round(stats["cash"] + choice["cash_change"], 2)
    stats["debt"] = round(max(0.0, stats["debt"] + choice["debt_change"]), 2)
    stats["net_worth"] = round(stats["cash"] - stats["debt"], 2)
    stats["credit_score"] = max(300, min(850, stats["credit_score"] + choice["credit_score_change"]))
    stats["stress"] = max(0, min(100, stats["stress"] + choice["stress_change"]))
    stats["happiness"] = max(0, min(100, stats["happiness"] + choice["happiness_change"]))
    stats["age"] += 2

    step = {
        "chapter_index": ch_idx,
        "chapter_title": chapter["title"],
        "choice_id": choice_id,
        "choice_text": choice["text"],
        "feedback": choice["feedback"],
        "unlocked_lesson": choice["lesson_unlocked"],
        "unlocked_lesson_title": choice["lesson_title"],
        "stats_after": dict(stats)
    }
    game_state["history"].append(step)
    game_state["current_chapter"] += 1
    if game_state["current_chapter"] > len(CHAPTERS):
        game_state["is_finished"] = True

    return {
        "step_result": step,
        "next_chapter": CHAPTERS[game_state["current_chapter"] - 1] if not game_state["is_finished"] else None,
        "game_state": game_state
    }

def rewind_to_chapter(game_state: Dict[str, Any], target_chapter: int) -> Dict[str, Any]:
    """Rewinds the timeline to before target_chapter was chosen (a real fork)."""
    if target_chapter < 1 or target_chapter >= game_state["current_chapter"]:
        raise ValueError("Invalid rewind target")

    # Find the history slice before target_chapter
    new_history = [h for h in game_state["history"] if h["chapter_index"] < target_chapter]
    if new_history:
        restored_stats = dict(new_history[-1]["stats_after"])
    else:
        # Initial stats
        init = initialize_game(game_state.get("difficulty", "Normal"))
        restored_stats = init["stats"]

    game_state["history"] = new_history
    game_state["stats"] = restored_stats
    game_state["current_chapter"] = target_chapter
    game_state["is_finished"] = False

    return {
        "rewound_to": target_chapter,
        "current_chapter_data": CHAPTERS[target_chapter - 1],
        "game_state": game_state
    }

def generate_1000_lives_report(game_state: Dict[str, Any]) -> Dict[str, Any]:
    history = game_state.get("history", [])
    prudent_choices = {"fund_emergency", "itemized_bill_hsa", "frugal_pivot", "pass_scam", "maximize_match", "prudent_downpayment"}
    
    user_prudent_count = sum(1 for h in history if h["choice_id"] in prudent_choices)
    decision_score = round((user_prudent_count / max(1, len(history))) * 100)

    # Monte Carlo simulation of 1,000 lives comparing this user's decision quality vs random
    simulated_net_worths = []
    for _ in range(1000):
        nw = game_state["stats"]["net_worth"]
        # Add market variance (-20% to +35%)
        market_luck = random.gauss(0.07, 0.15)
        simulated_net_worths.append(round(nw * (1.0 + market_luck), 2))
    
    simulated_net_worths.sort()
    p10 = simulated_net_worths[100]
    p50 = simulated_net_worths[500]
    p90 = simulated_net_worths[900]

    achievements = []
    if any(h["choice_id"] == "fund_emergency" for h in history):
        achievements.append("Emergency Fortress: Built a cash reserve before splurging")
    if any(h["choice_id"] == "pass_scam" for h in history):
        achievements.append("Scam Shield: Detected 15% monthly guaranteed return fraud")
    if any(h["choice_id"] == "maximize_match" for h in history):
        achievements.append("Free Money Hero: Captured 100% of employer 401(k) match")
    if not any(h["choice_id"] == "credit_card_panic" for h in history):
        achievements.append("Negotiation Master: Refused to panic-charge medical bills")

    best_decision = next((h["choice_text"] for h in history if h["choice_id"] in prudent_choices), "Consistent discipline")
    worst_decision = next((h["choice_text"] for h in history if h["choice_id"] not in prudent_choices), "None - flawless run!")

    grade = "A+" if decision_score >= 90 else ("A" if decision_score >= 80 else ("B" if decision_score >= 65 else "C"))

    return {
        "final_stats": game_state["stats"],
        "decision_score": decision_score,
        "grade": grade,
        "achievements": achievements,
        "best_decision": best_decision,
        "worst_decision": worst_decision,
        "monte_carlo_1000_lives": {
            "p10_bad_luck": p10,
            "p50_median": p50,
            "p90_good_luck": p90
        },
        "history": history
    }
