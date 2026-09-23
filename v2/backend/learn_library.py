from typing import List, Dict, Any

LESSONS: List[Dict[str, Any]] = [
    # 1. Getting Paid
    {
        "id": "paystub-basics",
        "category": "Getting Paid",
        "title": "Decoding Your Paystub & Gross vs Net",
        "tax_year": 2026,
        "why_it_matters": "Gross pay is what you earn on paper; net take-home is what actually lands in your checking account after mandatory taxes and elected benefits.",
        "common_mistake": "Budgeting off your annual salary divided by 12 without accounting for federal, FICA (Social Security & Medicare), and state deductions.",
        "what_to_do_next": "Review line items on your most recent paystub to confirm correct withholding and voluntary deductions.",
        "quiz": [
            {"q": "What is FICA tax composed of?", "options": ["Social Security and Medicare", "State tax and Federal tax", "Sales tax and property tax"], "answer": 0},
            {"q": "Does a gross salary of $60k mean you take home $5,000/month?", "options": ["Yes, exactly", "No, deductions reduce take-home pay", "Only in zero-tax states"], "answer": 1},
            {"q": "Where should you check voluntary deductions?", "options": ["Paystub benefits section", "Credit report", "Bank statement"], "answer": 0}
        ]
    },
    {
        "id": "w4-withholding",
        "category": "Getting Paid",
        "title": "W-4 Withholding: Large Refund vs Breaking Even",
        "tax_year": 2026,
        "why_it_matters": "A huge tax refund means you gave the federal government an interest-free loan all year instead of putting that money into a 4-5% HYSA or paying bills.",
        "common_mistake": "Treating a tax refund as 'free money' or bonus savings rather than your own delayed earnings.",
        "what_to_do_next": "Use the IRS Tax Withholding Estimator at irs.gov to update your W-4 with your employer if your refund was over $1,000.",
        "quiz": [
            {"q": "A large tax refund means:", "options": ["You made free profit", "You overpaid your taxes throughout the year", "Your employer gave you a gift"], "answer": 1},
            {"q": "The ideal tax return outcome for cash flow is:", "options": ["Owing $50,000", "Getting $10,000 back", "Close to $0 refunded or owed"], "answer": 2},
            {"q": "Where do you adjust your paycheck tax withholding?", "options": ["Form W-4 with HR", "Form 1040", "Credit bureau"], "answer": 0}
        ]
    },
    {
        "id": "biweekly-3-paycheck-months",
        "category": "Getting Paid",
        "title": "Biweekly Pay & The 3-Paycheck Magic Months",
        "tax_year": 2026,
        "why_it_matters": "Biweekly pay yields 26 paychecks a year. Because standard months have 2 paychecks (24 total), two months each year contain 3 paychecks.",
        "common_mistake": "Budgeting each month based on 2.16 paychecks and spending the extra third paycheck on impulse purchases.",
        "what_to_do_next": "Identify your two 3-paycheck months on the calendar and allocate that entire 3rd check to sinking funds, debt payoff, or IRA investments.",
        "quiz": [
            {"q": "How many paychecks do you receive per year on a biweekly schedule?", "options": ["24", "26", "52"], "answer": 1},
            {"q": "How many months per year have 3 paychecks on a biweekly schedule?", "options": ["1", "2", "4"], "answer": 1},
            {"q": "What is the best use of a third paycheck in a month?", "options": ["Extra debt payoff or savings", "Ignore it", "Spend immediately on lifestyle inflation"], "answer": 0}
        ]
    },

    # 2. Taxes
    {
        "id": "marginal-tax-brackets",
        "category": "Taxes",
        "title": "Marginal vs Effective Tax Rates: A Raise Never Hurts You",
        "tax_year": 2026,
        "why_it_matters": "The US tax system is progressive. Moving into a higher tax bracket ONLY taxes the dollars earned *above* the bracket threshold at the higher rate, never your entire income.",
        "common_mistake": "Turning down a promotion, raise, or bonus fearing that 'moving into a higher tax bracket' will decrease total take-home pay.",
        "what_to_do_next": "Always accept raises and promotions; calculate your effective (average) tax rate rather than just looking at your top marginal bracket.",
        "quiz": [
            {"q": "If you move into the 24% tax bracket from 22%, which income is taxed at 24%?", "options": ["All of your income", "Only dollars earned above the 24% threshold", "None of it"], "answer": 1},
            {"q": "Can getting a pay raise cause you to take home less total money overall?", "options": ["Yes, always", "No, because only extra dollars are taxed at the higher marginal rate", "Only on Mondays"], "answer": 1},
            {"q": "What is your effective tax rate?", "options": ["Total tax paid divided by total income", "Your highest tax bracket", "Your state sales tax"], "answer": 0}
        ]
    },
    {
        "id": "standard-deduction-2026",
        "category": "Taxes",
        "title": "Standard Deduction & Deductions vs Credits",
        "tax_year": 2026,
        "why_it_matters": "The standard deduction (approx. $15,000 for single filers in tax year 2026) reduces your taxable income dollar-for-dollar without needing receipts.",
        "common_mistake": "Confusing a tax deduction (reduces taxable income) with a tax credit (reduces final tax liability dollar-for-dollar).",
        "what_to_do_next": "Determine whether your itemized deductions exceed the standard deduction threshold before spending time tracking itemized receipts.",
        "quiz": [
            {"q": "A $1,000 tax credit saves you:", "options": ["$1,000 directly off your taxes owed", "$1,000 off taxable income", "$240"], "answer": 0},
            {"q": "Do most Americans take the standard deduction?", "options": ["Yes, over 85%", "No, almost no one", "Only corporations"], "answer": 0},
            {"q": "A tax deduction reduces:", "options": ["Your tax bill directly", "The amount of income subject to tax", "Your credit card debt"], "answer": 1}
        ]
    },

    # 3. Banking
    {
        "id": "hysa-vs-checking",
        "category": "Banking",
        "title": "High-Yield Savings (HYSA) vs Checking Accounts",
        "tax_year": 2026,
        "why_it_matters": "Traditional big banks pay ~0.01% APY on savings, while online FDIC-insured HYSAs pay 4.0% - 5.0% APY. On a $10,000 emergency fund, that is $500/year vs $1.",
        "common_mistake": "Leaving all cash sitting in a checking account where it earns 0% and is vulnerable to debit card fraud or accidental spending.",
        "what_to_do_next": "Open an FDIC-insured HYSA (e.g. Marcus, Ally, Capital One) and keep 1-2 months of living expenses in checking and the rest in HYSA.",
        "quiz": [
            {"q": "How much does $10,000 earn at 4.5% APY over one year?", "options": ["$450", "$45", "$4.50"], "answer": 0},
            {"q": "Are high-yield savings accounts FDIC insured up to $250,000?", "options": ["Yes, at member banks", "No, they are crypto", "Only in Europe"], "answer": 0},
            {"q": "What is the primary role of a checking account?", "options": ["Day-to-day transactions and paying bills", "Growing long-term wealth", "Stock trading"], "answer": 0}
        ]
    },
    {
        "id": "sinking-funds-annual-bills",
        "category": "Banking",
        "title": "Sinking Funds: Taming Irregular and Annual Bills",
        "tax_year": 2026,
        "why_it_matters": "Car insurance, holiday gifts, and Amazon Prime are predictable irregular expenses. Sinking funds divide annual costs into equal monthly savings.",
        "common_mistake": "Treating annual car insurance or holiday spending as an unexpected 'emergency' that forces you onto high-interest credit cards.",
        "what_to_do_next": "Add up all non-monthly bills, divide by 12, and set an automatic monthly transfer into dedicated sub-savings buckets.",
        "quiz": [
            {"q": "What is a sinking fund?", "options": ["Saving a monthly portion for a known future expense", "A failing investment", "A loan from the bank"], "answer": 0},
            {"q": "If car insurance is $600 every 6 months, how much should you save monthly?", "options": ["$100", "$600", "$50"], "answer": 0},
            {"q": "Should a predictable annual expense come out of your emergency fund?", "options": ["No, it should be planned via a sinking fund", "Yes, always", "Only if you have no credit"], "answer": 0}
        ]
    },

    # 4. Credit & Debt
    {
        "id": "credit-utilization-grace-periods",
        "category": "Credit",
        "title": "Credit Utilization & The Statement Grace Period",
        "tax_year": 2026,
        "why_it_matters": "Paying your full statement balance every month avoids 100% of interest charges. Keeping credit utilization under 30% (ideally under 10%) protects your credit score.",
        "common_mistake": "Believing the myth that carrying a monthly revolving balance on a credit card 'builds your credit score'.",
        "what_to_do_next": "Set all credit cards to Auto-Pay 'Full Statement Balance' so you never pay interest or incur late fees.",
        "quiz": [
            {"q": "Do you need to carry a balance and pay interest to build credit?", "options": ["No, paying in full every month builds credit without paying interest", "Yes, you must pay interest", "Only for the first 6 months"], "answer": 0},
            {"q": "What is the recommended maximum credit utilization ratio?", "options": ["Under 30% (ideally under 10%)", "95%", "100%"], "answer": 0},
            {"q": "What happens when you pay your statement balance in full before the due date?", "options": ["You owe $0 interest", "You owe 24% interest", "Your card is closed"], "answer": 0}
        ]
    },
    {
        "id": "debt-avalanche-vs-snowball",
        "category": "Debt",
        "title": "Debt Avalanche vs Debt Snowball Payoff",
        "tax_year": 2026,
        "why_it_matters": "The Avalanche method (paying highest interest rate first) saves the most money mathematically. The Snowball method (paying smallest balance first) builds behavioral motivation.",
        "common_mistake": "Paying random amounts across multiple cards without a unified priority strategy.",
        "what_to_do_next": "List all non-mortgage debts by interest rate and balance, choose Avalanche or Snowball, and put all excess payments toward the top target.",
        "quiz": [
            {"q": "Which debt payoff method minimizes total interest paid mathematically?", "options": ["Debt Avalanche (highest interest rate first)", "Debt Snowball (lowest balance first)", "Random selection"], "answer": 0},
            {"q": "Which debt payoff method provides the fastest psychological wins?", "options": ["Debt Snowball (lowest balance first)", "Debt Avalanche", "Minimum payments"], "answer": 0},
            {"q": "In both methods, what do you do with all other debts?", "options": ["Pay minimum payments on time", "Stop paying them", "Consolidate into crypto"], "answer": 0}
        ]
    },
    {
        "id": "student-loans-rules",
        "category": "Debt",
        "title": "Navigating Federal Student Loans & IDR Plans",
        "tax_year": 2026,
        "why_it_matters": "Federal student loans offer protections (income-driven repayment, forgiveness programs, deferment) not available on private refinance loans. Rules change frequently.",
        "common_mistake": "Refinancing low-interest federal loans into private commercial loans and forfeiting federal hardship protections.",
        "what_to_do_next": "Always check your official loan servicer details directly at studentaid.gov before making major repayment or consolidation choices.",
        "quiz": [
            {"q": "Where is the official source for federal student loan policies?", "options": ["studentaid.gov", "commercial bank ads", "social media forums"], "answer": 0},
            {"q": "If you refinance federal student loans with a private lender, do you keep federal protections?", "options": ["No, you permanently forfeit federal benefits and repayment plans", "Yes, always", "Only for 1 year"], "answer": 0},
            {"q": "What is an IDR plan?", "options": ["Income-Driven Repayment plan based on discretionary income", "Immediate Debt Relief", "Interest Doubling Rule"], "answer": 0}
        ]
    },

    # 5. Workplace Benefits & Retirement
    {
        "id": "401k-match-free-money",
        "category": "Workplace Benefits",
        "title": "401(k) Employer Match: Instant 100% Return",
        "tax_year": 2026,
        "why_it_matters": "An employer match (e.g. 50% or 100% match up to 5% of salary) is an instant guaranteed return on your investment and part of your total compensation package.",
        "common_mistake": "Contributing less than the match threshold while prioritizing other investments or speculative assets.",
        "what_to_do_next": "Log into your company benefits portal and set your 401(k) contribution to at least the full employer match percentage immediately.",
        "quiz": [
            {"q": "If your employer matches 100% up to 4% of salary, what is your immediate return?", "options": ["100% guaranteed return on that 4%", "4%", "0%"], "answer": 0},
            {"q": "Should you contribute to your 401(k) up to the match before funding individual stocks?", "options": ["Yes, never leave employer match on the table", "No, individual stocks are better", "Only when near retirement"], "answer": 0},
            {"q": "What does a vesting schedule determine?", "options": ["When you own employer-matched contributions", "Your tax rate", "Your retirement age"], "answer": 0}
        ]
    },
    {
        "id": "hsa-vs-fsa-rules",
        "category": "Workplace Benefits",
        "title": "HSA vs FSA: Triple Tax Advantage vs Use-It-Or-Lose-It",
        "tax_year": 2026,
        "why_it_matters": "In tax year 2026, HSA contribution limit is $4,300 (individual) / $8,550 (family). HSAs require an HDHP, roll over forever, and offer a triple tax advantage. FSAs are use-it-or-lose-it.",
        "common_mistake": "Overfunding an FSA thinking it acts like an investment account, then losing unspent funds at year-end.",
        "what_to_do_next": "If enrolled in an eligible HDHP, open and fund an HSA; if using an FSA, only contribute what you are certain you will spend on healthcare this plan year.",
        "quiz": [
            {"q": "What is the key difference between an HSA and an FSA?", "options": ["HSA funds roll over indefinitely and can be invested; FSA funds are generally use-it-or-lose-it", "They are identical", "FSAs are only for dental"], "answer": 0},
            {"q": "What is the 'triple tax advantage' of an HSA?", "options": ["Tax-deductible contributions, tax-free growth, and tax-free medical withdrawals", "Triple the interest rate", "Three free doctor visits"], "answer": 0},
            {"q": "Can you open an HSA with any health insurance plan?", "options": ["No, you must be enrolled in a qualified High Deductible Health Plan (HDHP)", "Yes, any plan qualifies", "Only with Medicare"], "answer": 0}
        ]
    },
    {
        "id": "roth-vs-traditional-ira",
        "category": "Workplace Benefits",
        "title": "Roth IRA vs Traditional IRA (2026 Limit: $7,000)",
        "tax_year": 2026,
        "why_it_matters": "In tax year 2026, IRA limit is $7,000 ($8,000 if age 50+). Roth IRAs are funded with after-tax money and grow 100% tax-free forever. Traditional IRAs offer upfront tax deduction.",
        "common_mistake": "Thinking you can contribute $7,000 to Roth AND $7,000 to Traditional—the $7,000 limit is shared across all IRAs per year.",
        "what_to_do_next": "If you are early in your career or expect higher taxes later, open a Roth IRA at Fidelity, Vanguard, or Schwab and set up automatic monthly contributions.",
        "quiz": [
            {"q": "What is the 2026 contribution limit for an IRA (under age 50)?", "options": ["$7,000", "$10,000", "$3,500"], "answer": 0},
            {"q": "How is a Roth IRA taxed in retirement?", "options": ["Qualified withdrawals are 100% tax-free", "Taxed as regular income", "Taxed at 50%"], "answer": 0},
            {"q": "Can you withdraw original Roth IRA contributions (not earnings) penalty-free anytime?", "options": ["Yes, original direct contributions can be withdrawn anytime without tax or penalty", "No, locked until 59.5", "Only with a doctor note"], "answer": 0}
        ]
    },

    # 6. Investing Basics & Protection
    {
        "id": "index-funds-vs-stock-picking",
        "category": "Investing Basics",
        "title": "Broad Index Funds vs Stock Picking & Market Timing",
        "tax_year": 2026,
        "why_it_matters": "Over 90% of professional fund managers fail to beat the S&P 500 or total market index over a 15-year period after fees. Low-cost index funds provide instant diversification.",
        "common_mistake": "Panic selling during standard market corrections or trying to time market tops and bottoms.",
        "what_to_do_next": "Automate recurring investments into broad low-cost index funds (e.g. Total US or World Stock Market ETFs) and leave them untouched for decades.",
        "quiz": [
            {"q": "Why are low-cost index funds favored by long-term investors?", "options": ["Instant diversification and lower expense ratios beating most active managers", "Guaranteed daily profits", "No risk of market fluctuations"], "answer": 0},
            {"q": "What typically happens when retail investors try to 'time the market'?", "options": ["They underperform due to missing the best market recovery days", "They consistently double their returns", "Zero effect"], "answer": 0},
            {"q": "What is the best reaction during a routine stock market downturn for long-term goals?", "options": ["Stay invested and stick to your regular contribution schedule", "Sell everything to cash immediately", "Take out high-interest loans"], "answer": 0}
        ]
    },
    {
        "id": "identity-theft-credit-freezes",
        "category": "Protection",
        "title": "Free Credit Freezes & Spotting Financial Scams",
        "tax_year": 2026,
        "why_it_matters": "Freezing your credit at Equifax, Experian, and TransUnion is 100% free by federal law and stops identity thieves from opening loans or cards in your name.",
        "common_mistake": "Believing credit monitoring prevents identity theft; monitoring only alerts you *after* a fraudulent account is already opened.",
        "what_to_do_next": "Visit the three major credit bureau websites and place a freeze on your credit reports today. Unfreeze temporarily only when applying for a loan.",
        "quiz": [
            {"q": "How much does it cost by law to freeze and unfreeze your credit reports?", "options": ["$0 (Free by federal law)", "$30 per bureau", "$100 yearly fee"], "answer": 0},
            {"q": "Will the IRS or CFPB ever call you demanding payment via gift cards or crypto?", "options": ["No, that is always an immediate red-flag scam", "Yes, if overdue", "Only on holidays"], "answer": 0},
            {"q": "Does a credit freeze hurt your existing credit score?", "options": ["No, it has zero impact on your score or existing cards", "Yes, drops it 50 points", "Yes, closes your accounts"], "answer": 0}
        ]
    }
]

def get_all_lessons() -> List[Dict[str, Any]]:
    return LESSONS

def get_lesson_by_id(lesson_id: str) -> Dict[str, Any]:
    for l in LESSONS:
        if l["id"] == lesson_id:
            return l
    return None
