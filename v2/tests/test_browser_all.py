import sys
import time
from playwright.sync_api import sync_playwright

def run_full_browser_audit():
    print("==================================================")
    print("STARTING FULL HEADLESS BROWSER AUDIT OF ALL PAGES")
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
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text} ({msg.location})") if msg.type in ["error"] else None)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {str(err)}"))

        failed_requests = []
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.method} {req.url} - {req.failure}"))

        bad_responses = []
        page.on("response", lambda resp: bad_responses.append(f"{resp.status} {resp.url}") if resp.status >= 400 and not resp.url.endswith("favicon.ico") else None)

        # 1. Load Page
        print("\n1. Navigating to http://localhost:8081 ...")
        page.goto("http://localhost:8081", wait_until="networkidle", timeout=15000)
        page.wait_for_selector(".brand h1", timeout=5000)
        print("✓ Page loaded successfully.")

        # 1b. Check if Auth modal is visible, click Continue as Demo Persona
        skip_link = page.locator("#btn-auth-skip")
        if skip_link.is_visible():
            print("  Auth modal is visible. Clicking 'Continue as Demo Persona (Local Dev)'...")
            skip_link.click()
            page.wait_for_timeout(500)

        # 2. Demo Seeding
        print("\n2. Clicking 'Seed Demo Data' button...")
        seed_btn = page.locator("#btn-seed")
        seed_btn.click()
        page.wait_for_timeout(2000) # Wait for network requests & toasts
        print("✓ Demo seed completed.")

        # 3. Test Every Navigation Page
        nav_pages = [
            ("overview", "Overview"),
            ("accounts", "Accounts"),
            ("budget", "Budget"),
            ("trials", "Trial Guard"),
            ("debts", "Debt"),
            ("goals", "Goals"),
            ("autopilot", "Autopilot"),
            ("game", "Life Mode"),
            ("learn", "Knowledge"),
            ("settings", "Settings")
        ]

        for p_name, keyword in nav_pages:
            print(f"\n3. Navigating to page: #{p_name} ...")
            nav_item = page.locator(f".nav-item[data-page='{p_name}']")
            nav_item.click()
            page.wait_for_selector(".page-title", timeout=5000)

            title_text = page.locator(".page-title").inner_text()
            print(f"  Page title rendered: '{title_text}'")
            assert keyword.lower() in title_text.lower(), f"Expected keyword '{keyword}', got '{title_text}'"

            # Check specific page actions
            if p_name == "overview":
                cards = page.locator(".kpi-card").all()
                print(f"  Found {len(cards)} KPI cards.")
            elif p_name == "trials":
                cards = page.locator(".trial-card").all()
                print(f"  Found {len(cards)} active trial cards.")
            elif p_name == "debts":
                sched = page.locator(".plan-card").all()
                print(f"  Found {len(sched)} debt payoff plan comparisons.")
            elif p_name == "learn":
                lessons = page.locator(".lesson-card").all()
                print(f"  Found {len(lessons)} lesson modules in knowledge library.")

        # 4. Test Autopilot Run Button
        print("\n4. Triggering 'Run Autopilot' button...")
        auto_btn = page.locator("#btn-autopilot-run")
        auto_btn.click()
        page.wait_for_timeout(2000)
        print("✓ Autopilot scan triggered successfully.")

        # 5. Test AI Assistant Drawer
        print("\n5. Testing AI Assistant Drawer...")
        assistant_btn = page.locator("#btn-open-assistant")
        assistant_btn.click()
        page.wait_for_selector("#drawer.open", timeout=3000)
        print("  Drawer opened.")

        input_field = page.locator("#drawer-input")
        input_field.fill("Give me a quick 1-sentence money brief.")
        send_btn = page.locator("#btn-send-drawer")
        send_btn.click()
        print("  Sent question to AI assistant, waiting for response...")
        page.wait_for_selector(".msg-agent:not(:has(.skeleton))", timeout=55000)
        agent_reply = page.locator(".msg-agent").last.inner_text()
        print(f"  AI Assistant replied ({len(agent_reply)} chars):")
        print("  >", agent_reply[:180], "...")

        # Close drawer
        close_btn = page.locator("#btn-close-drawer")
        close_btn.click()
        print("  Drawer closed.")

        # 6. Verify Console Errors and Network Failures
        print("\n================ AUDIT SUMMARY ================")
        print(f"Total Console Errors: {len(console_errors)}")
        for e in console_errors:
            print("  [ERROR]:", e)
        print(f"Total Failed Requests: {len(failed_requests)}")
        for r in failed_requests:
            print("  [FAILED]:", r)
        print(f"Total Bad HTTP Responses (>=400): {len(bad_responses)}")
        for b in bad_responses:
            print("  [BAD STATUS]:", b)
        print("================================================")

        browser.close()

        if console_errors or failed_requests or bad_responses:
            print("\n❌ AUDIT FAILED WITH UNRESOLVED ISSUES.")
            sys.exit(1)
        else:
            print("\n✅ AUDIT PASSED 100%! ZERO CONSOLE ERRORS, ZERO NETWORK FAILURES.")

if __name__ == "__main__":
    run_full_browser_audit()
