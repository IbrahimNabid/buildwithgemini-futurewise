import random
from typing import Dict, Any, List

CHAPTERS = [
    {
        "chapter_index": 1,
        "age": 27,
        "title": "The First Career Crossroads & Signing Bonus",
        "description": "You've been offered a new role with a $5,000 upfront signing bonus. But your apartment lease is also expiring with a $200/month rent bump.",
        "choices": [
            {
                "id": "fund_emergency",
                "text": "Stash $4,000 in your High-Yield Savings Account and move to a modest apartment.",
                "cash_change": 4000.0,
                "debt_change": 0.0,
                "stress_change": -10,
                "happiness_change": 10,
                "lesson_unlocked": "hysa-vs-checking",
                "feedback": "Prudent move! You established a cash cushion before life threw its first curveball."
            },
            {
                "id": "lifestyle_upgrade",
                "text": "Splurge on a luxury high-rise apartment and buy new designer furniture with the bonus.",
                "cash_change": -1500.0,
                "debt_change": 2500.0,
                "stress_change": 20,
                "happiness_change": 15,
                "lesson_unlocked": "paystub-basics",
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
                "stress_change": 5,
                "happiness_change": 0,
                "lesson_unlocked": "hsa-vs-fsa-rules",
                "feedback": "Brilliant! Asking for an itemized bill caught billing errors and saved you over $600."
            },
            {
                "id": "credit_card_panic",
                "text": "Charge the full $3,200 bill to your high-interest credit card without questioning the charges.",
                "cash_change": 0.0,
                "debt_change": 3200.0,
                "stress_change": 30,
                "happiness_change": -10,
                "lesson_unlocked": "credit-utilization-grace-periods",
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
                "stress_change": 15,
                "happiness_change": -5,
                "lesson_unlocked": "sinking-funds-annual-bills",
                "feedback": "Your emergency fund did its exact job: kept a roof over your head and kept you debt-free during the transition."
            },
            {
                "id": "credit_card_stack",
                "text": "Maintain your current spending habits on credit cards while looking for an executive role.",
                "cash_change": 0.0,
                "debt_change": 6500.0,
                "stress_change": 40,
                "happiness_change": -20,
                "lesson_unlocked": "debt-avalanche-vs-snowball",
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
                "stress_change": -5,
                "happiness_change": 10,
                "lesson_unlocked": "identity-theft-credit-freezes",
                "feedback": "Sharp instincts! Three weeks later, the anonymous pool admins pulled the liquidity and vanished."
            },
            {
                "id": "gamble_fund",
                "text": "Transfer $5,000 of your emergency savings into the token to chase quick gains.",
                "cash_change": -5000.0,
                "debt_change": 0.0,
                "stress_change": 35,
                "happiness_change": -30,
                "lesson_unlocked": "index-funds-vs-stock-picking",
                "feedback": "The pool crashed to zero. Remember: high guaranteed returns without risk do not exist in finance."
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
                "stress_change": -25,
                "happiness_change": 25,
                "lesson_unlocked": "401k-match-free-money",
                "feedback": "You captured $5,700 of 100% free employer money every year, accelerating your path to financial independence!"
            },
            {
                "id": "opt_out_match",
                "text": "Opt out of retirement to maximize your weekly paycheck and finance a sports car.",
                "cash_change": -3000.0,
                "debt_change": 12000.0,
                "stress_change": 20,
                "happiness_change": 5,
                "lesson_unlocked": "roth-vs-traditional-ira",
                "feedback": "Opting out left over $50,000 of compounded employer contributions on the table over the next decade."
            }
        ]
    }
]

def get_chapter(index: int) -> Dict[str, Any]:
    if 1 <= index <= len(CHAPTERS):
        return CHAPTERS[index - 1]
    return None

def compute_end_report(timeline: List[Dict[str, Any]], initial_stats: Dict[str, Any]) -> Dict[str, Any]:
    net_worth = initial_stats.get("cash", 5000.0) - initial_stats.get("debt", 2000.0)
    decision_score = 70
    achievements = []

    for step in timeline:
        choice_id = step.get("choice_id")
        if choice_id in ["fund_emergency", "itemized_bill_hsa", "frugal_pivot", "pass_scam", "maximize_match"]:
            decision_score += 6
        else:
            decision_score -= 8

    if any(s.get("choice_id") == "pass_scam" for s in timeline):
        achievements.append("Caught the Scam: Protected capital against high-yield fraud")
    if any(s.get("choice_id") == "maximize_match" for s in timeline):
        achievements.append("Full Match Champion: Never left free employer money behind")
    if not any(s.get("choice_id") == "credit_card_panic" for s in timeline):
        achievements.append("Medical Shield: Avoided compounding high-interest medical debt")

    decision_score = max(0, min(100, decision_score))
    grade = "A+" if decision_score >= 90 else ("A" if decision_score >= 80 else ("B" if decision_score >= 70 else "C"))

    return {
        "final_net_worth": net_worth,
        "decision_score": decision_score,
        "grade": grade,
        "achievements": achievements,
        "total_chapters_played": len(timeline),
        "timeline_summary": timeline
    }
