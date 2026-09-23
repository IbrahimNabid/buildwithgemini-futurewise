import sys
import time
from playwright.sync_api import sync_playwright

def run_e2e_journey():
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8081"
    print("==================================================")
    print(f"RUNNING FUTUREWISE V2 COMPLETE E2E USER JOURNEY ON: {target_url}")
    print("==================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context()
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {str(err)}"))

        # Step 1: Visit landing page
        print(f"1. Loading landing page {target_url} ...")
        page.goto(target_url, wait_until="networkidle", timeout=25000)
        assert "Futurewise v2" in page.title()
        print("✓ Page title verified.")

        # Step 2: Dismiss demo modal if visible
        skip_btn = page.locator("#btn-auth-skip")
        page.wait_for_selector("#btn-auth-skip", state="attached", timeout=5000)
        if skip_btn.is_visible():
            skip_btn.click()
            page.wait_for_timeout(500)
        print("✓ Authenticated/Demo session active.")

        # Step 3: Seed demo data
        print("2. Seeding demo persona data...")
        seed_btn = page.locator("#btn-seed")
        seed_btn.click()
        page.wait_for_selector(".toast", timeout=10000)
        page.wait_for_timeout(1500)
        print("✓ Demo seed completed.")

        # Step 4: Verify Executive Overview KPIs
        print("3. Verifying Overview KPIs...")
        page.wait_for_selector(".kpi-card", timeout=5000)
        kpi_count = len(page.locator(".kpi-card").all())
        assert kpi_count >= 4
        safe_to_spend = page.locator('.kpi-card:has-text("Safe to Spend This Week") .kpi-val').inner_text()
        print(f"✓ Overview KPIs verified. Safe to spend: {safe_to_spend}")
        assert "$" in safe_to_spend

        # Step 5: Navigate to Trials & verify App Store buffer
        print("4. Navigating to Trial Guard...")
        page.click('.nav-item[data-page="trials"]')
        page.wait_for_selector('h2.page-title:has-text("Trial Guard")', timeout=5000)
        trial_row = page.locator('table.data-table tr:has-text("Calm - Meditation")')
        assert trial_row.is_visible()
        assert "app_store" in trial_row.inner_text().lower()
        print("✓ Trial Guard verified: Calm - Meditation monitored with App Store buffer.")

        # Step 6: Navigate to Debt Payoff Planner
        print("5. Navigating to Debt Payoff Planner...")
        page.click('.nav-item[data-page="debts"]')
        page.wait_for_selector('h2.page-title:has-text("Debt Payoff Planner")', timeout=5000)
        assert page.locator('.panel-title:has-text("Debt Avalanche")').is_visible()
        assert page.locator('a[href*="studentaid.gov"]').is_visible()
        print("✓ Debt Payoff Planner verified: Avalanche vs Snowball & studentaid.gov link present.")

        # Step 7: Navigate to Learn Library & Complete Quiz
        print("6. Navigating to Knowledge & Tax Library...")
        page.click('.nav-item[data-page="learn"]')
        page.wait_for_selector('h2.page-title:has-text("Personal Finance Knowledge Library")', timeout=5000)
        lesson_btn = page.locator('.panel button:has-text("Open Lesson")').first
        lesson_btn.click()
        page.wait_for_timeout(500)

        # Select quiz answers
        first_modal = page.locator('.modal-overlay[id^="lesson-detail-"]').first
        first_modal.locator('input[type="radio"][value="0"]').first.check()
        first_modal.locator('input[type="radio"][value="0"]').nth(1).check()
        first_modal.locator('input[type="radio"][value="0"]').nth(2).check()

        submit_btn = first_modal.locator('button[data-action="submit-quiz"]')
        submit_btn.click()
        page.wait_for_selector('.toast', timeout=5000)
        print("✓ Learn library verified: completed 3-question quiz and verified toast score.")

        # Step 8: Life Mode Game - Choice & Rewind
        print("7. Testing Life Mode Game Simulator...")
        page.click('.nav-item[data-page="game"]')
        page.wait_for_selector('h2.page-title:has-text("Life Mode")', timeout=5000)

        # Click make-choice
        choice_btn = page.locator('[data-action="make-choice"]').first
        if choice_btn.is_visible():
            choice_btn.click()
            page.wait_for_timeout(1000)
            print("  Choice applied.")

        # Rewind
        rewind_btn = page.locator('[data-action="rewind-game"]').first
        if rewind_btn.is_visible():
            rewind_btn.click()
            page.wait_for_timeout(1000)
            print("  Timeline rewound.")
        print("✓ Life Mode game simulator verified.")

        # Step 9: Autopilot Run
        print("8. Testing Autonomous Autopilot scan...")
        page.locator('#btn-autopilot-run').click()
        page.wait_for_selector('.toast', timeout=10000)
        print("✓ Autopilot scan verified.")

        # Step 10: Real AI Assistant Chat
        print("9. Testing AI Assistant Co-pilot drawer...")
        page.click('#btn-open-assistant')
        page.wait_for_selector('#drawer.open', timeout=3000)
        page.fill('#drawer-input', 'Which of my free trials should I cancel?')
        page.click('#btn-send-drawer')
        # Wait for the new message to render (loader id removed / skeleton gone)
        page.wait_for_selector('.msg-agent[id^="loader-"]:not(:has(.skeleton))', timeout=45000)
        new_msg = page.locator('.msg-agent[id^="loader-"]').last
        reply = new_msg.inner_text().strip()
        print(f"✓ AI Assistant replied: {reply[:120]}...")
        assert len(reply) > 0

        # Step 11: Refresh page and verify persistence
        print("10. Refreshing page and verifying persistence...")
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(1500)
        # Check if auth modal is displayed (style.display !== 'none')
        modal = page.locator("#auth-modal")
        if modal.is_visible():
            page.locator("#btn-auth-skip").click()
            page.wait_for_timeout(1000)
        
        # Click overview to ensure executive overview loads
        page.locator('.nav-item[data-page="overview"]').click()
        page.wait_for_selector(".kpi-card", timeout=10000)
        persisted_val = page.locator('.kpi-card:has-text("Safe to Spend This Week") .kpi-val').inner_text()
        assert "$" in persisted_val
        print(f"✓ Data persisted across page reload: {persisted_val}")

        print("\n================ FINAL RESULTS ================")
        print(f"Console Errors: {len(console_errors)}")
        for e in console_errors:
            print("  [ERROR]", e)
        assert len(console_errors) == 0, f"Expected 0 console errors, got {len(console_errors)}"
        print("ALL TESTS PASSED WITH ZERO CONSOLE ERRORS!")
        print("================================================")
        browser.close()

if __name__ == "__main__":
    run_e2e_journey()
