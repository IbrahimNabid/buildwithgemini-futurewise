import sys
from playwright.sync_api import sync_playwright

def test_page_loads_cleanly():
    print("Launching Chromium headless...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context()
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text} ({msg.location})") if msg.type in ["error"] else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        all_responses = []
        page.on("response", lambda resp: all_responses.append(f"{resp.status} {resp.url}"))

        failed_requests = []
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.method} {req.url} - {req.failure}"))

        bad_responses = []
        page.on("response", lambda resp: bad_responses.append(f"{resp.status} {resp.url}") if resp.status >= 400 else None)

        print("Navigating to http://localhost:8081 ...")
        resp = page.goto("http://localhost:8081", wait_until="networkidle", timeout=15000)

        page.wait_for_selector(".brand h1", timeout=5000)
        print("Page loaded successfully! Title:", page.title())

        print(f"Console errors: {len(console_errors)}")
        for err in console_errors:
            print("  [CONSOLE ERROR]:", err)

        print(f"Failed requests: {len(failed_requests)}")
        for req in failed_requests:
            print("  [FAILED REQUEST]:", req)

        print(f"Bad responses (>=400): {len(bad_responses)}")
        for b in bad_responses:
            print("  [BAD RESPONSE]:", b)

        browser.close()

        if console_errors or failed_requests or bad_responses:
            print("FAILED: Found console errors or failed requests!")
            sys.exit(1)
        else:
            print("SUCCESS: Zero console errors, zero failed network requests!")

if __name__ == "__main__":
    test_page_loads_cleanly()
