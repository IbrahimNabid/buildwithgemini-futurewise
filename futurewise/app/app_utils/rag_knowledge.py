"""IRS Pub 969, Pub 590-A, and CFPB toolkit reference knowledge for Futurewise Learn topics."""

import re
from typing import Dict, Any, List

KNOWLEDGE_BASE = {
    "hsa_vs_fsa": {
        "publication": "IRS Publication 969 (Health Savings Accounts and Other Tax-Favored Health Plans)",
        "content": (
            "According to IRS Publication 969:\n"
            "- Health Savings Account (HSA): Requires coverage under a High Deductible Health Plan (HDHP). "
            "Contributions are 100% tax-deductible (pre-tax via payroll), investment earnings grow tax-free, "
            "and distributions used for qualified medical expenses are completely tax-free (triple tax advantage). "
            "Crucially, all unspent HSA funds roll over from year to year indefinitely—there is NO 'use-it-or-lose-it' rule. "
            "The account is portable and stays with you regardless of employer changes or retirement.\n"
            "- Flexible Spending Arrangement (FSA): An employer-established benefit. Contributions are pre-tax, "
            "but funds are generally subject to the 'use-it-or-lose-it' rule where unused amounts at the end of the plan "
            "year are forfeited, unless the employer adopts a 2.5-month grace period or a limited rollover amount "
            "(up to $660 in 2025/2026). FSAs are not investable and generally do not stay with you if you leave the employer."
        )
    },
    "roth_vs_traditional_ira": {
        "publication": "IRS Publication 590-A (Contributions to Individual Retirement Arrangements)",
        "content": (
            "According to IRS Publication 590-A:\n"
            "- Traditional IRA: Contributions may be tax-deductible in the year you make them (subject to income "
            "limits if covered by an employer retirement plan). Investments grow tax-deferred. Distributions in retirement "
            "are taxed as ordinary income, and Required Minimum Distributions (RMDs) begin at age 73.\n"
            "- Roth IRA: Contributions are made with after-tax dollars (no upfront deduction), subject to Modified "
            "Adjusted Gross Income (MAGI) phaseout limits. Earnings grow completely tax-free, and qualified distributions "
            "in retirement are 100% tax-free. Original contributions can be withdrawn at any time penalty-free and tax-free. "
            "There are no RMDs during the original owner's lifetime."
        )
    },
    "401k_and_match": {
        "publication": "CFPB 'Your Money, Your Goals' Financial Empowerment Toolkit & IRS Pub 590-A",
        "content": (
            "According to the CFPB 'Your Money, Your Goals' toolkit:\n"
            "- Employer 401(k) Match: An employer match is an immediate 100% (or 50%) guaranteed return on your money. "
            "Always contribute at least enough to capture the full employer match before allocating savings elsewhere. "
            "Vesting schedules dictate when employer contributions become yours to keep."
        )
    },
    "emergency_fund_and_credit": {
        "publication": "CFPB 'Your Money, Your Goals' Financial Empowerment Toolkit",
        "content": (
            "According to the CFPB 'Your Money, Your Goals' toolkit:\n"
            "- Emergency Savings: A foundational buffer of 3 to 6 months of essential living expenses (rent, groceries, utilities, debt minimums) "
            "kept in an accessible, liquid High Yield Savings Account (HYSA). Protects against unexpected shocks without resorting to high-interest credit.\n"
            "- Credit Scores & APR: Credit scores range from 300 to 850. Payment history (35%) and credit utilization (30%) make up the bulk of the score. "
            "APR represents the annualized cost of borrowing; high APR credit card balances compound rapidly and should be prioritized for payoff."
        )
    }
}


def consult_learn_rag(query: str) -> Dict[str, Any]:
    """Retrieves verified guidance on financial topics naming the official publication used.

    Sources: IRS Publication 969, IRS Publication 590-A, CFPB 'Your Money, Your Goals'.

    Args:
        query: The user's question or topic (e.g. 'difference between HSA and FSA', 'Roth IRA rules').

    Returns:
        A dictionary with the publication name and grounded factual text.
    """
    q = query.lower()
    if "hsa" in q or "fsa" in q:
        data = KNOWLEDGE_BASE["hsa_vs_fsa"]
    elif "roth" in q or "traditional" in q or "ira" in q:
        data = KNOWLEDGE_BASE["roth_vs_traditional_ira"]
    elif "401k" in q or "match" in q or "employer" in q:
        data = KNOWLEDGE_BASE["401k_and_match"]
    else:
        data = KNOWLEDGE_BASE["emergency_fund_and_credit"]

    return {
        "publication_used": data["publication"],
        "grounded_guidance": data["content"],
    }
