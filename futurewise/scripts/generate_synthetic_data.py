"""Generate synthetic data for Futurewise:
1. Bank export CSV (2 months of transactions for 27yo in NYC earning $68k)
2. Free trials tracker (3 trials: App Store in 2d, Google Play in 5d, Website in 12d)
3. Life events deck (15 simulation events with 2-3 options and financial effects)
4. Contribution limits for IRAs, HSAs, FSAs, and 401(k)s with tax_year field
5. Seed lesson metadata for each Learn topic
"""

import csv
import json
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path("/config/Desktop/BuildWithGemini/futurewise/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Bank Export CSV
# -----------------------------------------------------------------------------
def generate_bank_csv():
    # 2-month span: 2026-07-24 to 2026-09-22
    # Starting balance on 2026-07-24 morning: $3,240.50
    transactions = [
        # Date, Description, Category, Amount (positive=credit/deposit, negative=debit/expense)
        # Payday 1
        ("2026-07-24", "PAYROLL DIRECT DEPOSIT TECHCORP NYC", "Income", 1982.40),
        ("2026-07-24", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -2.90),
        ("2026-07-25", "TRADER JOE'S #541 BROOKLYN NY", "Groceries", -84.32),
        ("2026-07-25", "SWEETGREEN DUMBO BROOKLYN NY", "Dining", -16.85),
        ("2026-07-26", "JOE COFFEE COMPANY NEW YORK NY", "Dining", -5.75),
        ("2026-07-27", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-07-28", "BLINK FITNESS RECURRING DUES", "Subscriptions", -28.00),
        ("2026-07-29", "CHIPOTLE ONLINE ORDER NEW YORK NY", "Dining", -14.20),
        ("2026-07-30", "TARGET STORE T-2412 BROOKLYN NY", "Groceries", -38.45),
        ("2026-07-31", "CITI BIKE RIDE SINGLE NYC", "Transit", -4.99),
        
        # August 1: Rent + recurring
        ("2026-08-01", "ACH DEBIT NORTHSIDE PROPERTY MGMT RENT", "Rent", -1850.00),
        ("2026-08-01", "APPLE.COM/BILL ICLOUD+ 50GB", "Subscriptions", -2.99),
        ("2026-08-02", "WHOLE FOODS MKT BROOKLYN NY", "Groceries", -62.10),
        ("2026-08-03", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-08-04", "CAFE GRUMPY GREENPOINT NY", "Dining", -6.25),
        ("2026-08-05", "SPOTIFY USA RECURRING SUBSCRIPTION", "Subscriptions", -11.99),
        ("2026-08-06", "CVS PHARMACY #0241 BROOKLYN NY", "Health", -23.40),
        
        # Payday 2
        ("2026-08-07", "PAYROLL DIRECT DEPOSIT TECHCORP NYC", "Income", 1982.40),
        ("2026-08-07", "XI'AN FAMOUS FOODS NEW YORK NY", "Dining", -18.50),
        ("2026-08-08", "TRADER JOE'S #541 BROOKLYN NY", "Groceries", -92.15),
        ("2026-08-09", "JOE'S PIZZA GREENWICH NEW YORK NY", "Dining", -11.00),
        ("2026-08-10", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-08-12", "NETFLIX.COM MONTHLY SUBSCRIPTION", "Subscriptions", -15.49),
        ("2026-08-13", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -2.90),
        ("2026-08-14", "BLUE BOTTLE COFFEE NEW YORK NY", "Dining", -7.50),
        ("2026-08-15", "KEY FOOD SUPERMARKET BROOKLYN NY", "Groceries", -46.80),
        ("2026-08-16", "LYFT RIDE WILLIAMSBURG BROOKLYN", "Transit", -26.40),
        ("2026-08-17", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-08-18", "CON EDISON NYC UTILITY BILL", "Utilities", -78.30),
        ("2026-08-20", "SWEETGREEN SOHO NEW YORK NY", "Dining", -17.25),
        
        # Payday 3
        ("2026-08-21", "PAYROLL DIRECT DEPOSIT TECHCORP NYC", "Income", 1982.40),
        ("2026-08-22", "TRADER JOE'S #541 BROOKLYN NY", "Groceries", -79.40),
        ("2026-08-23", "TACOS EL BRONCO BROOKLYN NY", "Dining", -22.00),
        ("2026-08-24", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-08-26", "DUANE READE STORE 1419 NEW YORK NY", "Health", -15.80),
        ("2026-08-28", "BLINK FITNESS RECURRING DUES", "Subscriptions", -28.00),
        ("2026-08-29", "UNION MARKET PARK SLOPE NY", "Groceries", -54.20),
        ("2026-08-30", "CITI BIKE RIDE SINGLE NYC", "Transit", -4.99),
        
        # September 1: Rent + recurring
        ("2026-09-01", "ACH DEBIT NORTHSIDE PROPERTY MGMT RENT", "Rent", -1850.00),
        ("2026-09-01", "APPLE.COM/BILL ICLOUD+ 50GB", "Subscriptions", -2.99),
        ("2026-09-02", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-09-03", "TRADER JOE'S #541 BROOKLYN NY", "Groceries", -88.90),
        
        # Payday 4
        ("2026-09-04", "PAYROLL DIRECT DEPOSIT TECHCORP NYC", "Income", 1982.40),
        ("2026-09-04", "DAILY PROVISIONS MANHATTAN NY", "Dining", -13.50),
        ("2026-09-05", "SPOTIFY USA RECURRING SUBSCRIPTION", "Subscriptions", -11.99),
        ("2026-09-06", "WHOLE FOODS MKT BROOKLYN NY", "Groceries", -58.40),
        ("2026-09-07", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -2.90),
        ("2026-09-08", "CHIPOTLE ONLINE ORDER BROOKLYN NY", "Dining", -15.10),
        ("2026-09-09", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-09-11", "UBER TRIP BROOKLYN NY", "Transit", -31.25),
        ("2026-09-12", "NETFLIX.COM MONTHLY SUBSCRIPTION", "Subscriptions", -15.49),
        ("2026-09-13", "TRADER JOE'S #541 BROOKLYN NY", "Groceries", -82.60),
        ("2026-09-14", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-09-16", "CON EDISON NYC UTILITY BILL", "Utilities", -84.15),
        ("2026-09-17", "SWEETGREEN BROOKLYN HEIGHTS NY", "Dining", -17.50),
        
        # Payday 5
        ("2026-09-18", "PAYROLL DIRECT DEPOSIT TECHCORP NYC", "Income", 1982.40),
        ("2026-09-19", "FARMERS MARKET GRAND ARMY PLAZA", "Groceries", -34.00),
        ("2026-09-20", "JOE COFFEE COMPANY NEW YORK NY", "Dining", -6.00),
        ("2026-09-21", "MTA*NYCT PAYGO OMNY NEW YORK NY", "Transit", -5.80),
        ("2026-09-22", "CORNER BODEGA CIDER & DELI BROOKLYN", "Dining", -8.50),
    ]

    csv_path = DATA_DIR / "bank_transactions_nyc_27yo.csv"
    balance = 3240.50
    rows = []
    
    for idx, (t_date, desc, cat, amt) in enumerate(transactions, start=1):
        balance += amt
        tx_type = "Credit" if amt > 0 else "Debit"
        rows.append({
            "Transaction ID": f"TXN-2026-{idx:04d}",
            "Date": t_date,
            "Description": desc,
            "Category": cat,
            "Amount": f"{amt:+.2f}",
            "Type": tx_type,
            "Running Balance": f"{balance:.2f}",
        })

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Transaction ID", "Date", "Description", "Category", "Amount", "Type", "Running Balance"
        ])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} transactions in {csv_path}")


# -----------------------------------------------------------------------------
# 2. Free Trials Tracker
# -----------------------------------------------------------------------------
def generate_free_trials():
    trials = [
        {
            "id": "trial_calm_app_store",
            "service_name": "Calm - Sleep & Meditation",
            "platform": "App Store",
            "category": "Health & Wellness",
            "start_date": "2026-09-10",
            "trial_end_date": "2026-09-24",
            "days_remaining": 2,
            "price_after_trial": "$69.99/year",
            "annualized_cost": 69.99,
            "billing_frequency": "annual",
            "cancellation_policy": {
                "cancel_window": "At least 24 hours before expiration (Apple requirement)",
                "access_after_cancellation": "Keeps access until trial expiration date (2026-09-24)",
                "urgency_badge": "Action Required: Ends in 2 Days"
            },
            "recommended_action": "Cancel now to prevent auto-renewal charge of $69.99. Access remains active until Sept 24.",
            "cancellation_steps": [
                "Open Settings on your iPhone/iPad",
                "Tap your Name / Apple ID banner at the top",
                "Tap 'Subscriptions'",
                "Select 'Calm'",
                "Tap 'Cancel Free Trial' and confirm"
            ]
        },
        {
            "id": "trial_duolingo_google_play",
            "service_name": "Duolingo Super",
            "platform": "Google Play",
            "category": "Education",
            "start_date": "2026-09-13",
            "trial_end_date": "2026-09-27",
            "days_remaining": 5,
            "price_after_trial": "$12.99/month",
            "annualized_cost": 155.88,
            "billing_frequency": "monthly",
            "cancellation_policy": {
                "cancel_window": "Anytime before renewal date",
                "access_after_cancellation": "Keeps full Super access until trial ends on Sept 27",
                "urgency_badge": "Review: Ends in 5 Days"
            },
            "recommended_action": "Decide whether to keep or cancel. If canceling, do so before Sept 26 to avoid monthly recurring $12.99.",
            "cancellation_steps": [
                "Open Google Play Store app",
                "Tap your profile icon in top right",
                "Tap 'Payments & subscriptions' -> 'Subscriptions'",
                "Tap 'Duolingo'",
                "Tap 'Cancel subscription' and follow prompts"
            ]
        },
        {
            "id": "trial_wsj_direct_website",
            "service_name": "The Wall Street Journal Digital",
            "platform": "Website",
            "category": "News & Media",
            "start_date": "2026-09-04",
            "trial_end_date": "2026-10-04",
            "days_remaining": 12,
            "price_after_trial": "$4.00/month for 1st year, then $38.99/month",
            "annualized_cost": 48.00,
            "billing_frequency": "monthly",
            "cancellation_policy": {
                "cancel_window": "At least 48 hours prior to billing cycle end date",
                "access_after_cancellation": "May vary; online cancellation or live chat during business hours",
                "urgency_badge": "Upcoming: Ends in 12 Days"
            },
            "recommended_action": "Mark calendar for Oct 2 (2 days before trial ends). Cancel online at customer.wsj.com to avoid step-up billing.",
            "cancellation_steps": [
                "Sign in to customer.wsj.com",
                "Navigate to 'Customer Center' -> 'Manage My Subscription'",
                "Click 'Cancel Subscription' or initiate Online Live Chat",
                "Save cancellation confirmation number"
            ]
        }
    ]

    out_path = DATA_DIR / "free_trials.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trials, f, indent=2)
    print(f"Generated {len(trials)} free trials in {out_path}")


# -----------------------------------------------------------------------------
# 3. Life Events Deck (15 scenario cards)
# -----------------------------------------------------------------------------
def generate_life_events_deck():
    events = [
        {
            "id": "evt_001_rent_hike",
            "title": "The NYC Lease Renewal Hike",
            "category": "Housing",
            "chapter": 1,
            "prompt": "Your Brooklyn landlord sends your lease renewal with a $200/month increase (from $1,850 to $2,050). You have 30 days to respond.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Absorb the increase and renew",
                    "description": "Stay in your familiar apartment. Avoid moving friction and moving costs.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -200.0,
                        "annual_impact": -2400.0,
                        "stability_impact": "Reduces monthly savings capacity by 10% unless discretionary dining/shopping is trimmed."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Negotiate for a 2-year lease at +$75/month",
                    "description": "Counter-offer a modest $75/month increase in exchange for signing a guaranteed 24-month lease.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -75.0,
                        "annual_impact": -900.0,
                        "stability_impact": "Saves $1,500/year compared to landlord's initial ask and locks in housing predictability."
                    }
                },
                {
                    "option_id": "C",
                    "label": "Move to Queens with a roommate ($1,400/mo share)",
                    "description": "Incur one-time moving costs ($1,100 for U-Haul, movers, security deposit shift), but drop rent to $1,400.",
                    "financial_effects": {
                        "immediate_cost": -1100.0,
                        "monthly_cash_flow_delta": 450.0,
                        "annual_impact": 4300.0,
                        "stability_impact": "Upfront hit to emergency fund, but frees up $5,400/year to accelerate retirement and emergency savings."
                    }
                }
            ]
        },
        {
            "id": "evt_002_job_offer_crossroads",
            "title": "Career Fork: Series B Startup vs. Corporate Firm",
            "category": "Career",
            "chapter": 1,
            "prompt": "You receive two job offers. A fast-growing fintech startup offers $82k base + stock options with high deductible health plans. A stable enterprise offers $74k base + 6% 401(k) match and comprehensive medical/HSA benefits.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Take the Series B Startup ($82k base + options)",
                    "description": "Maximize immediate cash salary and potential equity upside. Less generous health/retirement match.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 750.0,
                        "annual_impact": 9000.0,
                        "stability_impact": "Higher gross cash flow, but requires self-disciplined retirement investing without an employer match."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Take the Enterprise ($74k base + 6% 401(k) match + HSA seed)",
                    "description": "Guaranteed $4,440/yr employer match, lower health insurance premiums, and $1,000 employer HSA contribution.",
                    "financial_effects": {
                        "immediate_cost": 1000.0,
                        "monthly_cash_flow_delta": 480.0,
                        "annual_impact": 9880.0,
                        "stability_impact": "Total compensation equals startup once match ($4,440) and HSA ($1,000) are factored in, with higher stability."
                    }
                }
            ]
        },
        {
            "id": "evt_003_unexpected_er_visit",
            "title": "Emergency Room Sprained Ankle & CT Scan",
            "category": "Health",
            "chapter": 2,
            "prompt": "A bad slip while running leads to an emergency room visit, X-rays, and an ankle boot. You receive an explanation of benefits: your bill is $1,850 before your HDHP deductible is reached.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Pay in full from emergency savings",
                    "description": "Wipe out $1,850 of your cash cushion immediately to avoid dealing with billing administrators.",
                    "financial_effects": {
                        "immediate_cost": -1850.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -1850.0,
                        "stability_impact": "Drains emergency savings runway by ~1 month, leaving you vulnerable to secondary shocks."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Request itemized bill and 0% 12-month payment plan",
                    "description": "Request itemized billing to drop erroneous charges, then establish a 0% interest payment plan ($135/mo for 12 mos).",
                    "financial_effects": {
                        "immediate_cost": -230.0,
                        "monthly_cash_flow_delta": -135.0,
                        "annual_impact": -1620.0,
                        "stability_impact": "Keeps cash buffer liquid; itemization typically shaves $200-$300 off hospital facility fees."
                    }
                },
                {
                    "option_id": "C",
                    "label": "Pay using accumulated triple-tax-advantaged HSA funds",
                    "description": "Use pre-tax dollars saved in your HSA. Reimburses the bill with 100% tax-free dollars.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -1850.0,
                        "stability_impact": "Saves ~$550 in effective federal/state/FICA taxes compared to paying out of post-tax checking."
                    }
                }
            ]
        },
        {
            "id": "evt_004_work_laptop_failure",
            "title": "Freelance Work Laptop Dies",
            "category": "Emergency",
            "chapter": 2,
            "prompt": "Your primary laptop for side-gig design contracts suffers liquid damage. You need a replacement to fulfill $1,200/month of ongoing freelance design work.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Buy top-tier new M3 Pro MacBook on 24.99% Store Card ($2,400)",
                    "description": "Financed on a retail credit card with minimum payments.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -120.0,
                        "annual_impact": -2900.0,
                        "stability_impact": "Dangerous high-interest debt trap; accrues over $500 in interest over 18 months."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Buy certified refurbished MacBook ($1,150) in cash",
                    "description": "Purchase Apple Certified Refurbished with 1-year warranty using emergency cash reserve.",
                    "financial_effects": {
                        "immediate_cost": -1150.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -1150.0,
                        "stability_impact": "Temporary cash dip quickly recouped by ongoing $1,200/mo freelance revenue with zero debt interest."
                    }
                }
            ]
        },
        {
            "id": "evt_005_destination_wedding",
            "title": "Best Friend's Destination Wedding in Italy",
            "category": "Lifestyle",
            "chapter": 2,
            "prompt": "Your college roommate invites you to their wedding on Lake Como. Flights, lodging, attire, and gifts will run approximately $2,200.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Attend full week vacation ($2,200 charged to credit card)",
                    "description": "Carried over 6 months at 21% APR.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -390.0,
                        "annual_impact": -2450.0,
                        "stability_impact": "Significant social reward, but costs an extra $250 in interest and drains cash flow."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Attend weekend only, book flight points + budget hostel ($1,050 cash)",
                    "description": "Use travel credit card points, stay in a shared Airbnb with mutual friends, pay cash.",
                    "financial_effects": {
                        "immediate_cost": -1050.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -1050.0,
                        "stability_impact": "Maintains social connection while halving total out-of-pocket spend; zero debt burden."
                    }
                },
                {
                    "option_id": "C",
                    "label": "Politely decline in-person, send thoughtful $150 gift",
                    "description": "Prioritize financial foundation and emergency fund buildout.",
                    "financial_effects": {
                        "immediate_cost": -150.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -150.0,
                        "stability_impact": "Preserves over $2,000 for emergency savings, but with some social FOMO."
                    }
                }
            ]
        },
        {
            "id": "evt_006_401k_match_enrollment",
            "title": "Company 401(k) Auto-Enrollment Window",
            "category": "Retirement",
            "chapter": 3,
            "prompt": "Your employer auto-enrolls you at 3% contribution. Their policy offers a 100% match up to 5% of salary ($3,400/yr free match on your $68k salary).",
            "options": [
                {
                    "option_id": "A",
                    "label": "Leave at default 3% ($170/mo from paycheck)",
                    "description": "Captures $2,040 of match, leaving $1,360/year of employer match unclaimed.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -125.0,
                        "annual_impact": 4080.0,
                        "stability_impact": "Positive retirement start, but sacrifices $1,360/year of guaranteed 100% employer return."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Increase to 5% to capture 100% of employer match ($283/mo)",
                    "description": "Take full advantage of the 5% match. Paycheck drops by ~$205/mo after federal/state tax savings.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -205.0,
                        "annual_impact": 6800.0,
                        "stability_impact": "Maximizes guaranteed 100% immediate return on match; builds $6,800/yr in tax-advantaged wealth."
                    }
                },
                {
                    "option_id": "C",
                    "label": "Opt out completely to maximize take-home pay",
                    "description": "Receive extra $125/mo in paycheck, but forfeit $3,400/yr of free money.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 125.0,
                        "annual_impact": -3400.0,
                        "stability_impact": "Severe long-term opportunity loss; forfeit hundreds of thousands in 30-year compound growth."
                    }
                }
            ]
        },
        {
            "id": "evt_007_tax_refund_windfall",
            "title": "Surprise $2,800 Tax Refund & Bonus",
            "category": "Windfall",
            "chapter": 3,
            "prompt": "You file your taxes and receive a combined federal and NY state tax refund plus a performance spot bonus totaling $2,800.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Deposit 100% into High-Yield Savings Account (HYSA)",
                    "description": "Boost emergency fund from $3,200 to $6,000, achieving a full 3 months of basic NYC expenses.",
                    "financial_effects": {
                        "immediate_cost": 2800.0,
                        "monthly_cash_flow_delta": 10.5,
                        "annual_impact": 2925.0,
                        "stability_impact": "Major leap in financial stability; unlocks true baseline peace of mind."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Split: $1,400 to HYSA emergency fund, $1,400 to Roth IRA index fund",
                    "description": "Strengthen cash buffer while seeding long-term tax-free compound growth.",
                    "financial_effects": {
                        "immediate_cost": 2800.0,
                        "monthly_cash_flow_delta": 5.0,
                        "annual_impact": 2940.0,
                        "stability_impact": "Balanced approach advancing both short-term security and multi-decade wealth."
                    }
                },
                {
                    "option_id": "C",
                    "label": "Upgrade wardrobe & take weekend trip to Montauk ($2,800)",
                    "description": "Spend windfall entirely on lifestyle upgrades.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": 0,
                        "stability_impact": "Zero financial resilience gained; emergency fund remains dangerously lean."
                    }
                }
            ]
        },
        {
            "id": "evt_008_credit_card_debt_consolidation",
            "title": "Credit Card Balance & 0% Balance Transfer Offer",
            "category": "Debt",
            "chapter": 3,
            "prompt": "You have a lingering $3,500 credit card balance carrying 24.99% APR, costing you ~$73/month in pure interest. You receive an offer for a 0% APR balance transfer for 15 months (3% transfer fee).",
            "options": [
                {
                    "option_id": "A",
                    "label": "Accept 0% balance transfer and pay $240/month",
                    "description": "Pay $105 one-time transfer fee, then pay $240/mo to be completely debt-free in 15 months.",
                    "financial_effects": {
                        "immediate_cost": -105.0,
                        "monthly_cash_flow_delta": -240.0,
                        "annual_impact": 880.0,
                        "stability_impact": "Saves ~$980 in predatory interest charges; boosts credit score as utilization drops to zero."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Continue paying minimum payment (~$90/month) at 24.99%",
                    "description": "Make minimal dent in principal while paying majority to interest.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -90.0,
                        "annual_impact": -875.0,
                        "stability_impact": "Takes over 5 years to clear, costing more than $2,100 in cumulative interest."
                    }
                }
            ]
        },
        {
            "id": "evt_009_side_hustle_launch",
            "title": "Freelance Brand Consulting Opportunity",
            "category": "Career",
            "chapter": 4,
            "prompt": "A boutique marketing agency in Manhattan offers you an ongoing monthly retainer for 12 hours of weekend design work at $75/hour ($900/month gross).",
            "options": [
                {
                    "option_id": "A",
                    "label": "Accept retainer and allocate 30% to quarterly estimated taxes",
                    "description": "Earn $900/mo gross, save $270 for taxes, netting $630/mo pure additional cash flow.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 630.0,
                        "annual_impact": 7560.0,
                        "stability_impact": "Expands monthly savings rate by over 15%, greatly accelerating emergency fund and IRA targets."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Decline to protect weekend work-life balance and mental health",
                    "description": "Focus 100% on primary career advancement and skill-building.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": 0,
                        "stability_impact": "Preserves personal time and prevents burnout, but cash flow remains tightly bound to day job."
                    }
                }
            ]
        },
        {
            "id": "evt_010_hsa_open_enrollment",
            "title": "Benefits Open Enrollment: PPO vs. HDHP + HSA",
            "category": "Health",
            "chapter": 4,
            "prompt": "It's November open enrollment. You are healthy and visit the doctor 1-2 times a year. Plan A: PPO ($180/mo premium, $500 deductible). Plan B: HDHP ($75/mo premium, $1,650 deductible, employer contributes $600 to your HSA).",
            "options": [
                {
                    "option_id": "A",
                    "label": "Choose HDHP + HSA and contribute $150/month pre-tax",
                    "description": "Save $105/mo in payroll premiums, gain $600 free employer seed, and save ~$55/mo in taxes on HSA contributions.",
                    "financial_effects": {
                        "immediate_cost": 600.0,
                        "monthly_cash_flow_delta": -45.0,
                        "annual_impact": 2520.0,
                        "stability_impact": "Leverages the triple-tax advantage (pre-tax, tax-free growth, tax-free withdrawal for medical); builds healthcare nest egg."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Stick with traditional PPO for perceived peace of mind",
                    "description": "Pay $180/mo payroll deduction ($2,160/year) with no HSA vehicle.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -180.0,
                        "annual_impact": -2160.0,
                        "stability_impact": "Guarantees lower co-pays, but wastes ~$1,800/yr in higher premiums and forfeited employer HSA seed."
                    }
                }
            ]
        },
        {
            "id": "evt_011_market_dip_volatility",
            "title": "Stock Market Pullback: S&P 500 Dips 18%",
            "category": "Economy",
            "chapter": 4,
            "prompt": "Inflation concerns and interest rate volatility trigger a headline-dominating 18% market correction over 3 weeks. Your 401(k) and IRA show red balances.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Panic sell index fund holdings to cash to 'stop the bleeding'",
                    "description": "Convert paper losses into permanent realized losses.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -1800.0,
                        "stability_impact": "Locks in losses at market bottom; misses subsequent historical recoveries."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Stay the course and maintain automatic monthly dollar-cost averaging",
                    "description": "Do not alter your automated contributions. Buy index shares at an 18% discount.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": 0,
                        "stability_impact": "Classic evidence-based index investing practice; historically yields strong long-term upside."
                    }
                },
                {
                    "option_id": "C",
                    "label": "Trim $100 from monthly dining out to buy extra index fund shares",
                    "description": "Opportunistically buy low during market distress.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -100.0,
                        "annual_impact": 1200.0,
                        "stability_impact": "Boosts long-term wealth accumulation by acquiring undervalued equities with zero leverage."
                    }
                }
            ]
        },
        {
            "id": "evt_012_dental_crown_emergency",
            "title": "Unexpected Dental Crown",
            "category": "Health",
            "chapter": 5,
            "prompt": "A fractured molar requires a porcelain crown. Basic dental insurance covers 50%, leaving you with an out-of-pocket patient balance of $850.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Pay with HSA debit card",
                    "description": "Use pre-tax HSA funds accumulated earlier.",
                    "financial_effects": {
                        "immediate_cost": -850.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -850.0,
                        "stability_impact": "Zero impact on checking account or credit score; saves ~30% in effective income tax."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Ask dental office for 5% cash discount, pay from checking",
                    "description": "Most private dentists give 5-10% discount for cash/debit settlement in full ($780).",
                    "financial_effects": {
                        "immediate_cost": -780.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -780.0,
                        "stability_impact": "Mild hit to emergency fund, but captures instant $70 discount."
                    }
                }
            ]
        },
        {
            "id": "evt_013_subscription_audit",
            "title": "Trial Guard Subscription Audit",
            "category": "Budgeting",
            "chapter": 5,
            "prompt": "Futurewise flags 4 lingering subscriptions and forgotten auto-renewals (streaming services, premium apps, news tiers) totaling $78/month.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Audit and cancel unused subscriptions immediately",
                    "description": "Cancel 3 unused subscriptions, retaining only 1 core favorite. Saves $62/month.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 62.0,
                        "annual_impact": 744.0,
                        "stability_impact": "Recovers $744/year with zero change in quality of life; automatically redirected to savings."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Postpone decision ('I might watch that show next month')",
                    "description": "Keep all subscriptions active.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -744.0,
                        "stability_impact": "Quiet cash drain that bleeds over $700 annually on unused digital services."
                    }
                }
            ]
        },
        {
            "id": "evt_014_roommate_moving_out",
            "title": "Roommate Announces Sudden Relocation",
            "category": "Housing",
            "chapter": 5,
            "prompt": "Your roommate gives 30 days notice that they are moving to Los Angeles. You either need to find a vetted replacement or cover their $1,200 share until the lease expires in 3 months.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Vigorously interview and screen a replacement roommate",
                    "description": "List room on trusted housing boards. Find replacement with clean credit and background check within 3 weeks.",
                    "financial_effects": {
                        "immediate_cost": -100.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": -100.0,
                        "stability_impact": "Minor screening and posting expense avoids a disastrous $3,600 rent shortfall."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Cover the whole rent alone for 3 months ($3,600 total)",
                    "description": "Enjoy living alone for 90 days before lease ends.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": -1200.0,
                        "annual_impact": -3600.0,
                        "stability_impact": "Severely exhausts emergency fund; consumes nearly 50% of monthly net income."
                    }
                }
            ]
        },
        {
            "id": "evt_015_roth_ira_annual_milestone",
            "title": "Year-End Roth IRA Contribution Sprint",
            "category": "Retirement",
            "chapter": 5,
            "prompt": "It's December 15. You have contributed $4,500 of the $7,000 annual limit to your Roth IRA. You have $2,500 in excess checking beyond your 3-month emergency fund.",
            "options": [
                {
                    "option_id": "A",
                    "label": "Max out the full $7,000 limit with the remaining $2,500",
                    "description": "Fill your annual tax-free bucket completely before the April tax deadline.",
                    "financial_effects": {
                        "immediate_cost": -2500.0,
                        "monthly_cash_flow_delta": 0,
                        "annual_impact": 2500.0,
                        "stability_impact": "Compounds tax-free for the next 35 years; projected to grow to over $26,000 at historical 7% real returns."
                    }
                },
                {
                    "option_id": "B",
                    "label": "Keep the $2,500 in cash HYSA buffer",
                    "description": "Forego maxing out the tax-free vehicle to maintain an extra thick cash blanket.",
                    "financial_effects": {
                        "immediate_cost": 0,
                        "monthly_cash_flow_delta": 8.0,
                        "annual_impact": 96.0,
                        "stability_impact": "High nominal safety, but permanently forfeits this year's irreplaceable $2,500 tax-free capacity."
                    }
                }
            ]
        }
    ]

    out_path = DATA_DIR / "life_events_deck.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
    print(f"Generated {len(events)} life events in {out_path}")


# -----------------------------------------------------------------------------
# 4. Tax Contribution Limits (2024, 2025, 2026)
# -----------------------------------------------------------------------------
def generate_tax_contribution_limits():
    limits = [
        {
            "tax_year": 2024,
            "ira": {
                "regular_contribution_limit": 7000,
                "catch_up_limit_age_50_plus": 1000,
                "total_limit_with_catch_up": 8000,
                "roth_magi_phaseout_single": {"start": 146000, "end": 161000},
                "roth_magi_phaseout_mfj": {"start": 230000, "end": 240000},
                "notes": "Roth contributions are made with after-tax dollars; growth and qualified withdrawals are 100% tax-free."
            },
            "hsa": {
                "individual_coverage_limit": 4150,
                "family_coverage_limit": 8300,
                "catch_up_limit_age_55_plus": 1000,
                "hdhp_min_deductible_individual": 1600,
                "hdhp_min_deductible_family": 3200,
                "hdhp_max_out_of_pocket_individual": 8050,
                "hdhp_max_out_of_pocket_family": 16100,
                "notes": "Triple tax advantage: pre-tax contributions, tax-free growth, tax-free withdrawals for qualified medical expenses."
            },
            "healthcare_fsa": {
                "employee_salary_reduction_limit": 3200,
                "max_carryover_to_next_year": 640,
                "notes": "Use-it-or-lose-it rule applies; employer plan may offer a grace period or up to $640 rollover."
            },
            "dependent_care_fsa": {
                "limit_single_or_mfj": 5000,
                "limit_married_filing_separately": 2500,
                "notes": "Pre-tax dollars for qualifying daycare, preschool, before/after school care for children under 13."
            },
            "retirement_401k_403b": {
                "employee_elective_deferral_limit": 23000,
                "catch_up_limit_age_50_plus": 7500,
                "total_employee_limit_with_catch_up": 30500,
                "combined_employer_employee_limit": 69000
            }
        },
        {
            "tax_year": 2025,
            "ira": {
                "regular_contribution_limit": 7000,
                "catch_up_limit_age_50_plus": 1000,
                "total_limit_with_catch_up": 8000,
                "roth_magi_phaseout_single": {"start": 150000, "end": 165000},
                "roth_magi_phaseout_mfj": {"start": 236000, "end": 246000},
                "notes": "Indexed for inflation. Contributions can be made up until the tax filing deadline."
            },
            "hsa": {
                "individual_coverage_limit": 4300,
                "family_coverage_limit": 8550,
                "catch_up_limit_age_55_plus": 1000,
                "hdhp_min_deductible_individual": 1650,
                "hdhp_min_deductible_family": 3300,
                "hdhp_max_out_of_pocket_individual": 8300,
                "hdhp_max_out_of_pocket_family": 16600,
                "notes": "Requires enrollment in an HSA-eligible High Deductible Health Plan (HDHP)."
            },
            "healthcare_fsa": {
                "employee_salary_reduction_limit": 3300,
                "max_carryover_to_next_year": 660,
                "notes": "Funds generally forfeit at plan year-end unless subject to 2.5 month grace period or carryover."
            },
            "dependent_care_fsa": {
                "limit_single_or_mfj": 5000,
                "limit_married_filing_separately": 2500,
                "notes": "Statutory limit set by Congress, not indexed for inflation."
            },
            "retirement_401k_403b": {
                "employee_elective_deferral_limit": 23500,
                "catch_up_limit_age_50_plus": 7500,
                "special_catch_up_ages_60_to_63": 11250,
                "total_employee_limit_with_catch_up": 31000,
                "combined_employer_employee_limit": 70000
            }
        },
        {
            "tax_year": 2026,
            "ira": {
                "regular_contribution_limit": 7500,
                "catch_up_limit_age_50_plus": 1000,
                "total_limit_with_catch_up": 8500,
                "roth_magi_phaseout_single": {"start": 153000, "end": 168000},
                "roth_magi_phaseout_mfj": {"start": 240000, "end": 250000},
                "notes": "IRA limits step up to $7,500 to keep pace with cost-of-living adjustments."
            },
            "hsa": {
                "individual_coverage_limit": 4450,
                "family_coverage_limit": 8900,
                "catch_up_limit_age_55_plus": 1000,
                "hdhp_min_deductible_individual": 1700,
                "hdhp_min_deductible_family": 3400,
                "hdhp_max_out_of_pocket_individual": 8550,
                "hdhp_max_out_of_pocket_family": 17100,
                "notes": "HSA funds roll over indefinitely and can be invested in mutual funds/ETFs for retirement."
            },
            "healthcare_fsa": {
                "employee_salary_reduction_limit": 3400,
                "max_carryover_to_next_year": 680,
                "notes": "Election is fixed during open enrollment unless a qualifying life event occurs."
            },
            "dependent_care_fsa": {
                "limit_single_or_mfj": 5000,
                "limit_married_filing_separately": 2500,
                "notes": "Not eligible for rollover; must be incurred during the plan year."
            },
            "retirement_401k_403b": {
                "employee_elective_deferral_limit": 24000,
                "catch_up_limit_age_50_plus": 8000,
                "special_catch_up_ages_60_to_63": 11500,
                "total_employee_limit_with_catch_up": 32000,
                "combined_employer_employee_limit": 71500
            }
        }
    ]

    out_path = DATA_DIR / "tax_contribution_limits.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(limits, f, indent=2)
    print(f"Generated {len(limits)} tax years in {out_path}")


# -----------------------------------------------------------------------------
# 5. Seed Lesson Metadata for Learn Topics
# -----------------------------------------------------------------------------
def generate_learn_lessons():
    lessons = [
        {
            "topic_id": "roth_vs_trad_ira",
            "title": "Roth vs. Traditional IRA: Pay Taxes Now or Later?",
            "category": "Retirement & Taxes",
            "estimated_minutes": 6,
            "prerequisites": [],
            "grounding_source": {
                "document": "IRS Publication 590-A",
                "title": "Contributions to Individual Retirement Arrangements (IRAs)",
                "sections": ["What Is a Traditional IRA?", "What Is a Roth IRA?", "Income Phaseout Limits"]
            },
            "summary": "Understand the core distinction between Traditional IRAs (pre-tax deduction now, taxed on withdrawal) and Roth IRAs (pay taxes today, 100% tax-free growth and withdrawals forever). Learn how marginal tax brackets guide the choice.",
            "key_takeaways": [
                "Traditional IRAs lower your taxable income in the year you contribute.",
                "Roth IRAs are funded with after-tax dollars, but your investment growth and future retirement distributions are 100% tax-free.",
                "If you expect your tax rate to be higher in retirement than today (common for young professionals in early career stages), a Roth IRA is mathematically superior.",
                "Contributions (your principal) to a Roth IRA can be withdrawn at any time penalty-free."
            ],
            "interactive_calculator_type": "roth_vs_trad_comparator",
            "sandbox_script_hook": "compare_roth_vs_traditional(current_income, projected_retirement_bracket)"
        },
        {
            "topic_id": "401k_and_employer_match",
            "title": "401(k) & Employer Match: Don't Leave Free Money Behind",
            "category": "Retirement & Investing",
            "estimated_minutes": 5,
            "prerequisites": [],
            "grounding_source": {
                "document": "CFPB 'Your Money, Your Goals' Toolkit",
                "title": "Saving for Retirement & Long-Term Goals",
                "sections": ["Employer-Sponsored Plans", "Understanding the Match"]
            },
            "summary": "Demystify employer 401(k) plans, automated payroll deductions, and how an employer match represents an immediate guaranteed 50% to 100% return on your dollars.",
            "key_takeaways": [
                "An employer match is literally part of your negotiated total compensation; skipping it is equivalent to turning down a raise.",
                "Common match structures include 100% match up to 3-5% of salary, or 50% match up to 6%.",
                "Contributions reduce your current federal and state tax withholding directly on your paystub.",
                "Understand the company vesting schedule to know when matched funds belong to you 100%."
            ],
            "interactive_calculator_type": "match_maximizer_calculator",
            "sandbox_script_hook": "calculate_401k_match_and_tax_shield(salary, match_percent, contribution_percent)"
        },
        {
            "topic_id": "hsa_triple_tax_advantage",
            "title": "Health Savings Account (HSA): The Triple-Tax Secret Weapon",
            "category": "Healthcare & Investing",
            "estimated_minutes": 7,
            "prerequisites": [],
            "grounding_source": {
                "document": "IRS Publication 969",
                "title": "Health Savings Accounts and Other Tax-Favored Health Plans",
                "sections": ["HSA Eligibility", "Qualifying HDHP Requirements", "Distributions"]
            },
            "summary": "Discover why the HSA is often called the most tax-efficient account in the U.S. tax code. Learn about the triple-tax advantage, eligibility criteria under High Deductible Health Plans (HDHP), and how to invest HSA funds for healthcare in retirement.",
            "key_takeaways": [
                "Triple tax advantage: 1. Tax-deductible going in (payroll deduction skips FICA too). 2. Growth is tax-free. 3. Withdrawals for qualified medical expenses are tax-free.",
                "Unlike FSAs, HSA balances never expire and roll over year after year indefinitely.",
                "Once your cash buffer covers your deductible, excess HSA dollars can be invested in low-cost index funds.",
                "After age 65, HSA funds can be withdrawn for non-medical expenses with no penalty (taxed just like a Traditional IRA)."
            ],
            "interactive_calculator_type": "hsa_vs_fsa_comparator",
            "sandbox_script_hook": "compare_hsa_vs_fsa_savings(salary, medical_spend, plan_type)"
        },
        {
            "topic_id": "health_and_dependent_care_fsa",
            "title": "Health & Dependent Care FSAs: The 'Use-It-or-Lose-It' Rules",
            "category": "Healthcare & Budgeting",
            "estimated_minutes": 5,
            "prerequisites": [],
            "grounding_source": {
                "document": "IRS Publication 969",
                "title": "Flexible Spending Arrangements (FSAs)",
                "sections": ["Healthcare FSA Rules", "Grace Periods & Carryovers", "Dependent Care Limits"]
            },
            "summary": "Learn how Flexible Spending Accounts (FSAs) save 25-35% on predictable out-of-pocket medical, dental, vision, or daycare expenses, while guarding against the strict 'use-it-or-lose-it' deadline trap.",
            "key_takeaways": [
                "FSAs allow you to contribute pre-tax dollars to cover known medical, dental, vision, and child care expenses.",
                "Full Healthcare FSA annual election is available on day 1 of the plan year.",
                "Most unspent funds forfeit at the end of the year unless your plan has a $640+ carryover or a 2.5-month grace period.",
                "Never over-elect in an FSA; budget only for predictable, high-probability expenses."
            ],
            "interactive_calculator_type": "fsa_tax_savings_estimator",
            "sandbox_script_hook": "calculate_fsa_tax_savings(anticipated_expenses, tax_bracket)"
        },
        {
            "topic_id": "emergency_funds",
            "title": "Emergency Funds: Your First Defense Against High-Interest Debt",
            "category": "Financial Stability",
            "estimated_minutes": 4,
            "prerequisites": [],
            "grounding_source": {
                "document": "CFPB 'Your Money, Your Goals' Toolkit",
                "title": "Building Savings & Managing Cash Flow",
                "sections": ["Emergency Savings Target", "Choosing a Safe Account"]
            },
            "summary": "Why saving 3 to 6 months of baseline living expenses in a High-Yield Savings Account (HYSA) separates people who survive financial emergencies with zero debt from those who get trapped by 25% APR credit cards.",
            "key_takeaways": [
                "Baseline expenses are your 'survival budget' (rent, groceries, basic utilities, minimum debt payments), not full discretionary spending.",
                "Keep emergency cash in a liquid High-Yield Savings Account (HYSA) separate from checking to avoid temptation.",
                "A starter buffer of $1,000 to 1 month of expenses provides immediate psychological relief before tackling debt.",
                "Replenishing an emergency fund takes precedence after an unexpected expense occurs."
            ],
            "interactive_calculator_type": "emergency_fund_runway_calculator",
            "sandbox_script_hook": "calculate_emergency_runway(current_cash, monthly_baseline_expenses)"
        },
        {
            "topic_id": "credit_scores_and_health",
            "title": "Credit Scores Demystified: The Hidden Cost of Low Credit",
            "category": "Credit & Borrowing",
            "estimated_minutes": 6,
            "prerequisites": [],
            "grounding_source": {
                "document": "CFPB 'Your Money, Your Goals' Toolkit",
                "title": "Understanding Credit Reports and Scores",
                "sections": ["What Makes Up a Score", "Disputing Errors", "Rebuilding Credit"]
            },
            "summary": "Break down the FICO formula (payment history 35%, credit utilization 30%, length of history 15%, new credit 10%, credit mix 10%). Learn how credit scores dictate apartment approvals, auto loans, and mortgage rates.",
            "key_takeaways": [
                "Payment history (35%) is king: one 30-day late payment can drop an excellent score by 60-100 points.",
                "Credit utilization (30%) is the ratio of balance to limit; keeping it under 10-30% on each card boosts scores rapidly.",
                "Never pay credit card interest to 'build credit'—paying in full every month builds an identical top-tier score with $0 in interest.",
                "Check free credit reports annually via annualcreditreport.com to catch identity theft or errors."
            ],
            "interactive_calculator_type": "credit_utilization_simulator",
            "sandbox_script_hook": "simulate_credit_utilization(card_balances, card_limits)"
        },
        {
            "topic_id": "apr_and_debt_paydown",
            "title": "APR & Debt Elimination: Debt Avalanche vs. Debt Snowball",
            "category": "Debt Management",
            "estimated_minutes": 6,
            "prerequisites": [],
            "grounding_source": {
                "document": "CFPB 'Your Money, Your Goals' Toolkit",
                "title": "Dealing with Debt",
                "sections": ["Debt Paydown Strategies", "Avalanche vs. Snowball", "Negotiating Rates"]
            },
            "summary": "Understand how Annual Percentage Rate (APR) compounds against you. Compare the mathematically optimal Debt Avalanche method (highest APR first) against the behavioral Debt Snowball method (smallest balance first).",
            "key_takeaways": [
                "Credit card debt at 20-29% APR is a financial emergency that out-costs almost all market investment returns.",
                "Debt Avalanche pays minimums on all debts, putting all surplus toward the highest interest rate—saving the most money.",
                "Debt Snowball targets the smallest dollar balance first for rapid psychological wins.",
                "0% balance transfer cards and personal consolidation loans can halt interest accrual if paired with strict spending discipline."
            ],
            "interactive_calculator_type": "debt_paydown_comparator",
            "sandbox_script_hook": "compare_debt_avalanche_vs_snowball(debts_list, extra_monthly_payment)"
        },
        {
            "topic_id": "compound_interest",
            "title": "The Power of Compound Interest & Time Horizons",
            "category": "Investing Fundamentals",
            "estimated_minutes": 5,
            "prerequisites": [],
            "grounding_source": {
                "document": "CFPB 'Your Money, Your Goals' Toolkit",
                "title": "The Rule of 72 and Compounding",
                "sections": ["Exponential Growth", "The Cost of Waiting"]
            },
            "summary": "See how compound interest turns small recurring monthly savings into massive wealth over 10, 20, and 30 years. Learn why starting at age 25 vs. age 35 can double your retirement nest egg with less out-of-pocket money.",
            "key_takeaways": [
                "Compound interest earns interest on your interest, creating an exponential growth curve over decades.",
                "Rule of 72: Divide 72 by the annual return rate to approximate how many years it takes your money to double.",
                "Saving $200/month starting at age 25 at 7% real returns yields ~$240,000+ by age 55, with only $72,000 deposited.",
                "Time in the market beats timing the market every single time."
            ],
            "interactive_calculator_type": "compound_interest_visualizer",
            "sandbox_script_hook": "calculate_compound_growth(initial_deposit, monthly_addition, years, annual_return)"
        },
        {
            "topic_id": "low_cost_index_funds",
            "title": "Index Funds & Passive Investing: Owning the Entire Economy",
            "category": "Investing Fundamentals",
            "estimated_minutes": 6,
            "prerequisites": ["compound_interest"],
            "grounding_source": {
                "document": "CFPB 'Your Money, Your Goals' Toolkit",
                "title": "Investment Basics for Long-Term Security",
                "sections": ["Mutual Funds & ETFs", "The Impact of Expense Ratios"]
            },
            "summary": "Why trying to pick individual winning stocks fails 90% of professional hedge fund managers. Learn how broad-market index funds (like S&P 500 or Total Stock Market) give you instant diversification for pennies in fees.",
            "key_takeaways": [
                "An index fund buys a slice of hundreds or thousands of leading public companies in one single basket.",
                "Low expense ratios (0.03% to 0.10%) ensure your investment returns stay in your pocket rather than going to financial brokers.",
                "A 1% management fee can eat up over 25-30% of your total lifetime retirement portfolio value over 35 years.",
                "Dollar-cost averaging: invest an automatic fixed amount each month regardless of whether headlines say the market is up or down."
            ],
            "interactive_calculator_type": "fee_drag_calculator",
            "sandbox_script_hook": "calculate_fee_drag(portfolio_size, horizon_years, low_fee_pct, high_fee_pct)"
        },
        {
            "topic_id": "tax_brackets_explained",
            "title": "Tax Brackets: Marginal vs. Effective Rates Demystified",
            "category": "Taxes & Planning",
            "estimated_minutes": 5,
            "prerequisites": [],
            "grounding_source": {
                "document": "IRS Publication 590-A & Federal Tax Code",
                "title": "Understanding Progressive Tax Rates and Deductions",
                "sections": ["Progressive Brackets", "Standard Deduction", "Marginal Tax Calculation"]
            },
            "summary": "Clear up the widespread misconception that 'getting a raise into a higher tax bracket reduces your take-home pay.' Master the difference between your marginal tax rate (tax on your last dollar) and effective tax rate (average tax on all dollars).",
            "key_takeaways": [
                "The U.S. uses progressive tax brackets; only the income within that specific bracket is taxed at the higher percentage rate.",
                "Getting a raise will NEVER cause you to take home less money overall.",
                "Standard deduction (over $14,600+ for single filers) means your first chunk of earned income is taxed at 0%.",
                "Pre-tax deductions (401k, HSA, Traditional IRA) reduce income from your highest marginal bracket first, maximizing immediate cash savings."
            ],
            "interactive_calculator_type": "tax_bracket_breakdown_calculator",
            "sandbox_script_hook": "calculate_marginal_vs_effective_rate(income, filing_status, pre_tax_deductions)"
        }
    ]

    out_path = DATA_DIR / "learn_lessons_metadata.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(lessons, f, indent=2)
    print(f"Generated {len(lessons)} lessons in {out_path}")


if __name__ == "__main__":
    generate_bank_csv()
    generate_free_trials()
    generate_life_events_deck()
    generate_tax_contribution_limits()
    generate_learn_lessons()
    print("\nAll synthetic data generated successfully in futurewise/data/!")
