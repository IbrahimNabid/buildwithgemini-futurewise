# My agent: Futurewise

**One-liner:** A conversational personal finance agent that helps everyday people achieve financial stability through personalized daily briefs, grounded financial education, proactive trial/subscription guardrails, contextual economic news, and an interactive life simulator.

> **Disclaimer:** Futurewise is an educational application and does not provide certified financial, legal, or tax advice. All figures, simulations, and lessons are for educational purposes only.

---

## Tool Coverage

- **Memory (Memory Bank & Sessions):**
  - User financial profile: monthly income, pay schedule, savings goals, monthly baseline expenses.
  - User behavioral state: completed lessons, spending habits, and subscriptions the user explicitly intends to keep.
  - Cross-session memory: remembers previous simulations and financial stability progress over time.

- **Tools (Function Tools & Sub-Agents):**
  - **Firestore (keyed by User ID):**
    - `users/{userId}/trials`: Free trial tracker (service, platform, start date, trial end, renewal price, safe cancellation window, cancellation steps).
    - `users/{userId}/expenses`: Logged expenses and imported CSV transactions.
    - `users/{userId}/budgets`: Monthly budget limits by category.
    - `tax_limits/{taxYear}`: Contribution limits for HSA, FSA, 401(k), IRA with `tax_year` field.
    - `life_events_deck`: Firestore collection of life scenario cards for the simulation.
  - **RAG Engine (Vertex AI RAG / Agent Platform):**
    - Grounding corpus: IRS Publication 590-A (IRAs), IRS Publication 969 (HSAs & FSAs), CFPB "Your Money, Your Goals" toolkit.
  - **Google Search Sub-Agents:**
    - Trial Guard policy researcher: Searches for subscription cancellation terms, policy changes, and store-specific cancellation workflows (App Store, Google Play, direct web).
    - Economy News fetcher: Fetches latest economic indicators (interest rates, inflation, job reports, index movements) with publication dates and sources.
  - **Cloud Storage (GCS):**
    - Stores generated `.ics` calendar reminder files for free trial cancellation dates.
    - Stores generated chapter illustration images from `gemini-3.1-flash-lite-image`.

- **Catalog / UI (A2UI):**
  - **Money Brief Card:** Consolidated single-card dashboard containing upcoming trial expirations, current month budget burn rate, stability check indicators, and plain-English economic headline.
  - **Comparison Tables:** HSA vs FSA and Roth vs Traditional IRA side-by-side breakdowns.
  - **Trial Guard Table:** Active free trials with cancellation safety badges ("Safe to Cancel Now" vs "Cancel 2 Days Before").
  - **Simulation Scorecard:** Multi-chapter journey cards and 1,000-life Monte Carlo outcome distribution charts.

- **Image Gen:**
  - `gemini-3.1-flash-lite-image`: Generates thematic, text-free visual chapter header illustrations for the financial life simulator, uploaded to GCS.

- **Sandbox (Code Execution):**
  - Personal finance math: Computes personalized tax savings, compounding growth, and safe-to-spend weekly amounts.
  - CSV parser & categorizer: Parses bank export CSVs, categorizes spending, and flags recurring subscription charges.
  - Life Simulator engine: Advances financial state over 3-5 chapters factoring inflation, debt interest, and market returns with a fixed demo seed.
  - Monte Carlo engine: Simulates 1,000 alternative life paths based on user decisions to compute a decision quality score vs luck.

---

## Architecture: Five Connected Components

### 1. Money Brief
- Triggered on demand ("Show my brief" or greeting).
- Renders a single consolidated A2UI card with:
  - **Trials Ending Soon:** Alerts on any trial ending within 7 days.
  - **Budget Status:** Current month spending vs target, remaining safe-to-spend weekly allowance.
  - **Stability Check:** Emergency fund runway (months of expenses covered by savings), current savings rate (%), and high-interest debt balance.
  - **Economy in Plain English:** 1 curated headline with non-jargon explanation of what it means for everyday cash flow.

### 2. Learn (Grounded Education)
- Lessons: Roth vs Traditional IRA, 401(k) + employer match, HSA, Health & Dependent Care FSA, Emergency Funds, Credit Scores, APR & Debt Paydown, Compound Interest, Index Funds, and Tax Brackets.
- Grounded via RAG on:
  - IRS Publication 590-A (Contributions to IRAs)
  - IRS Publication 969 (Health Savings Accounts and Other Tax-Favored Health Plans)
  - CFPB "Your Money, Your Goals" toolkit
- Sandbox-powered calculations:
  - HSA vs FSA calculator (tax savings + rollover rules personalized to income).
  - Roth vs Traditional comparison (current marginal rate vs projected retirement tax rate).
- Firestore integration: Contribution limits indexed under `tax_limits` with `tax_year`.

### 3. Budget + Trial Guard
- **Expense Logging:** Natural language chat logging ("Spent $42 on groceries") + bank CSV file upload.
- **Code Sandbox Analysis:** Categorizes spending, compares against monthly budget targets, detects recurring billing cadences, and computes weekly safe-to-spend amount.
- **Trial Guard Tracking:**
  - Fields: `service`, `platform` (`App Store` | `Google Play` | `Website`), `start_date`, `trial_end`, `price_after_trial`.
  - Cancellation Intelligence: Distinguishes between services where canceling immediately preserves access until period ends vs services where canceling ends access instantly (recommends canceling 2 days before renewal). Defaults to 2-day warning if policy is uncertain.
  - Cancellation Steps: Clear walkthrough per platform.
  - Cost Warning: Total projected annual cost if forgotten.
  - Calendar Export: Generates `.ics` file stored in Cloud Storage with downloadable link.
  - Policy Sub-Agent: Google Search sub-agent looks up active cancellation policies.

### 4. Money News
- Sub-agent powered by Google Search fetches verified macroeconomic updates:
  - Federal Reserve interest rate decisions
  - CPI / Inflation reports
  - Jobs / Unemployment statistics
  - Major market index movements (S&P 500, etc.)
- Strict Guardrails: Translates news strictly to everyday personal impact (e.g. mortgage rates, savings yields, grocery prices). Never recommends buying, selling, or timing specific stocks or securities.

### 5. Play (Financial Life Simulator)
- 3 to 5 interactive narrative chapters starting from user's actual baseline numbers.
- Dynamic chapter draws from Firestore `life_events_deck`.
- User choices (A/B/C) evaluated in Code Sandbox:
  - Models compounding investment returns, wage growth, inflation, and debt interest.
  - Uses fixed demo seed for reproducible test scenarios.
  - Interweaves contextual lessons when user encounters instruments like HSAs or 401(k) matches.
- Visuals: Header image generated per chapter using `gemini-3.1-flash-lite-image` (saved to GCS, prompt constrained to contain zero text/letters).
- Final Analysis (Monte Carlo):
  - Runs 1,000 simulated iterations of the user's strategy across random market/life distributions.
  - Computes a Decision Quality Score isolating strategic sound choices from market luck.

---

## Must-Haves vs Stretch Menu

### Core Rails & Must-Haves (Build First)
1. **Sessions & Memory Bank:** Persistent user financial profile, subscriptions, and lesson progress.
2. **Firestore Database:** User data keyed by `userId`, `tax_limits` by year, and `life_events_deck`.
3. **RAG Grounding:** IRS 590-A, IRS 969, and CFPB toolkit document corpus.
4. **Code Sandbox Calculations:** Budget analyzer, safe-to-spend calculation, HSA/FSA comparison, and life simulator game math.
5. **A2UI Visual Presentation:** Money Brief card, comparison tables, and Trial Guard alert cards.
6. **Sub-Agent Search:** Trial cancellation policy lookup and economy news fetcher.
7. **Cloud Storage (GCS):** Storage for `.ics` calendar reminders and generated chapter illustrations (`gemini-3.1-flash-lite-image`).
8. **Compliance Guardrail:** Clear educational disclaimer; strict prohibition on investment advice.

### Stretch Menu (Pick Later)
- Interactive knowledge check quizzes at the end of Learn modules.
- Video/Audio Omni trailer summarizing the user's financial simulation journey.
- Community / cohort shared leaderboard for simulator decision scores.
- Real-time stock ticker quotes.
- Push / email notification hooks for subscription renewals.

---

## First Eval Question
**Scenario:**
A 27-year-old user earning $68,000/year asks:
*"I have $3,000 in savings and just started a job offering an HDHP with an HSA and a 4% 401(k) match. How should I prioritize my next $300/month, and when should I cancel my 14-day gym trial?"*

**Evaluation Criteria for a Good Response:**
1. **Mathematical Accuracy & Order of Operations:** Directs money to the 401(k) match first (guaranteed 100% return on match), then builds starter emergency fund / leverages HSA triple-tax advantage. Computes exact tax savings via Code Sandbox using current tax limits.
2. **Grounding:** Accurately cites HSA eligibility rules from IRS Publication 969 without hallucinations.
3. **Trial Guard Actionability:** Identifies gym trial cancellation policy, calculates potential cost of missing deadline, provides exact platform cancel steps, recommends canceling 2 days before end date if unsure, and offers a calendar reminder.
4. **Tone & Compliance:** Plain English, empathetic, structured as an A2UI card/table, clearly stating it is educational guidance, not certified financial advice.
