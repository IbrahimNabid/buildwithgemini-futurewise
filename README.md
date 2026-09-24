# Futurewise
> *"Learn it. Track it. Play it forward."*

Futurewise is a full-stack, multi-agent, autonomous personal finance platform engineered to help everyday people—especially those without a background in finance—make sound, mathematically optimal money decisions. Futurewise delivers a bank-grade fintech dashboard where the AI assistant acts as a knowledgeable, context-aware co-pilot rather than the sole interface.

---

## 🌟 Architecture & Core Systems

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Vanilla SPA Web Frontend                        │
│             (Private-Banking Aesthetic, Hash Router, A2UI)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Application Gateway                        │
│                 (/v2/backend, Firebase Token Auth)                     │
└───────┬───────────────────────────┬────────────────────────────┬───────┘
        │                           │                            │
        ▼                           ▼                            ▼
┌─────────────────┐       ┌──────────────────┐         ┌─────────────────┐
│ Cloud Firestore │       │  ADK Multi-Agent │         │ Cloud Scheduler │
│  (User Scoped)  │       │   Coordinator    │         │ (8am Daily Cron)│
└─────────────────┘       └─────────┬────────┘         └────────┬────────┘
                                    │                           │
                   ┌────────────────┴────────────────┐          ▼
                   ▼                                 ▼  ┌────────────────┐
         Specialist Agents                   Autonomous │ Daily Autopilot│
       • Budget & Cash-Flow                   Execution │ Scan & Briefs  │
       • Trial Guard (0-risk cancel)                    └────────────────┘
       • Debt Avalanche/Snowball
       • Learn & Tax Education
       • Markets & News Macro Pulse
       • Life Mode Game Master
```

---

## 🚀 Key Features by Phase

1. **Phase 1: Accounts & Database**
   - Firebase Authentication with email/password and Google login.
   - User-scoped Firestore subcollections: `accounts`, `transactions`, `budgets`, `sinking_funds`, `trials`, `subscriptions`, `goals`, `debts`, `lesson_progress`, `game_saves`, `alerts`, `briefs`.
   - Full CRUD REST API with single-click demo persona seeding (`Taylor Reynolds`, 27, NYC).
   - Data portability: 1-click export to structured JSON or flattened CSV, and cascading GDPR/CCPA account deletion.

2. **Phase 2: Multi-Agent System (ADK)**
   - **Coordinator Agent**: Context-aware routing based on active UI view and user intent.
   - **Budget Agent**: Analyzes safe-to-spend weekly balances, budget vs actual, and cash-flow calendars.
   - **Trial Guard Agent**: Computes countdown days, enforces conservative App Store 2-day cancellation buffers, and generates downloadable `.ics` calendar reminders.
   - **Debt & Credit Agent**: Computes mathematical payoff schedules comparing Avalanche (highest APR first) and Snowball (lowest balance first), with credit utilization checks.
   - **Learn Agent & News Agent**: Grounds educational concepts in tax rules (tax year 2026) and translates macroeconomic news for everyday budgets without stock tips.
   - **Strict Sandbox Execution**: All monetary arithmetic is executed deterministically—never estimated by LLMs.

3. **Phase 3: Autopilot (Autonomous Operations)**
   - Autonomous scanner triggers via Cloud Scheduler (`0 8 * * * America/New_York`) or on-demand.
   - Flags trials ending $\le 3$ days, budgets exceeding 80%, upcoming overdraft risks (bills > checking), and generates daily executive Money Briefs.

4. **Phase 4: Life Mode (The Game)**
   - Life simulation chapters with choices, branching consequences, and live HUD tracking net worth, cash, debt, simulated credit score, and stress/happiness meters.
   - 1,000-lives replay decision scoring (luck vs quality) and end-of-game report cards with unlockable achievements.

5. **Phase 5: Knowledge Library (Tax Year 2026)**
   - 15 comprehensive modules covering paystubs, W-4 withholding, 3-paycheck months, marginal vs effective tax rates, standard deductions, HYSAs, sinking funds, 401(k) matches, HSA vs FSA rules, and credit freezes. Each module includes a 3-question mastery quiz.

6. **Phase 6: Fintech Edge Cases Handled**
   - Multi-bank CSV format column auto-mapping.
   - Non-judgmental crisis guidance and assistance links (e.g. 211 resources, hospital bill itemization).
   - Strict prompt-injection shielding treating financial transactions as data, not instructions.
   - Mandatory official links (`studentaid.gov`, `irs.gov`, `consumerfinance.gov`).

7. **Phase 7: Premium Bank-Grade Frontend**
   - Modern desktop-first design: `#F5F7FA` canvas, `#0B1F3A` deep navy, `#0E9F6E` emerald accents, `#C9A227` gold highlights, tabular numerals (`tnum`), and slide-in drawer assistant.

---

## 🛠️ Local Development & Deployment

### Run Locally:
```bash
# Start from repository root using the standardized runner (Port 8081)
./v2/run.sh
```
Visit `http://localhost:8081` in your browser. The single source of truth for static frontend assets is located at `v2/frontend/static`.

### Cloud Deployment:
Deployed to Google Cloud Run:
- **Service**: `futurewise-v2-backend`
- **Region**: `us-east1`
- **Project**: `qwiklabs-gcp-04-7459370ad109`

---

## ⚖️ Disclaimer
*Educational only, not financial or legal advice. All simulation scores and calculations are for illustrative learning purposes.*
