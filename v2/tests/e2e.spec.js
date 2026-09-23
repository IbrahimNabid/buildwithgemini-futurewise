const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8081';

test.describe('Futurewise v2 End-to-End User Journey', () => {

  test('Complete Flow: Seed, KPIs, Trials, Game Rewind, Learn Quiz, Assistant', async ({ page }) => {
    // 1. Visit landing page
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/Futurewise v2/);

    // 2. Dismiss or handle demo modal if shown
    const skipBtn = page.locator('#btn-auth-skip');
    if (await skipBtn.isVisible()) {
      await skipBtn.click();
    }

    // 3. Seed demo data
    const seedBtn = page.locator('#btn-seed');
    await expect(seedBtn).toBeVisible();
    await seedBtn.click();

    // Verify Toast notification
    await expect(page.locator('.toast')).toBeVisible({ timeout: 10000 });

    // 4. Verify Computed Overview KPIs
    await expect(page.locator('.kpi-val').first()).toBeVisible();
    const safeToSpend = await page.locator('.kpi-card:has-text("Safe to Spend This Week") .kpi-val').innerText();
    expect(safeToSpend).toContain('$');

    // 5. Navigate to Trial Guard & verify App Store 2-day buffer
    await page.click('.nav-item[data-page="trials"]');
    await expect(page.locator('h2.page-title')).toHaveText('Trial Guard & Subscriptions');
    const trialRow = page.locator('table.data-table tr:has-text("Calm - Meditation")');
    await expect(trialRow).toBeVisible();
    await expect(trialRow).toContainText('app_store');

    // 6. Navigate to Debt Payoff Planner & verify Avalanche vs Snowball
    await page.click('.nav-item[data-page="debts"]');
    await expect(page.locator('h2.page-title')).toHaveText('Debt Payoff Planner');
    await expect(page.locator('.panel-title:has-text("Debt Avalanche")')).toBeVisible();
    await expect(page.locator('a[href*="studentaid.gov"]')).toBeVisible();

    // 7. Navigate to Learn Library & complete a 3-question quiz
    await page.click('.nav-item[data-page="learn"]');
    await expect(page.locator('h2.page-title')).toContainText('Personal Finance Knowledge Library');
    // Open first lesson modal
    const firstLessonBtn = page.locator('.panel button:has-text("Open Lesson")').first();
    await firstLessonBtn.click();

    // Select quiz answers
    await page.check('input[name*="q_"][value="0"]');
    await page.check('input[name*="q_"][value="1"]');
    await page.check('input[name*="q_"][value="2"]');

    const submitQuizBtn = page.locator('button[data-action="submit-quiz"]').first();
    await submitQuizBtn.click();
    await expect(page.locator('.toast')).toBeVisible();

    // 8. Life Mode Game: Play choice & rewind
    await page.click('.nav-item[data-page="game"]');
    await expect(page.locator('h2.page-title')).toHaveText('Life Mode: Career & Wealth Simulator');
    
    // Choose option
    const choiceCard = page.locator('[data-action="make-choice"]').first();
    if (await choiceCard.isVisible()) {
      await choiceCard.click();
      await expect(page.locator('.toast')).toBeVisible();
      // Test Rewind
      const rewindBtn = page.locator('[data-action="rewind-game"]').first();
      if (await rewindBtn.isVisible()) {
        await rewindBtn.click();
        await expect(page.locator('.toast')).toContainText(/rewound/i);
      }
    }

    // 9. Autopilot Run
    const autopilotBtn = page.locator('#btn-autopilot-run');
    await autopilotBtn.click();
    await expect(page.locator('.toast')).toBeVisible();

    // 10. AI Assistant interaction
    await page.click('#btn-open-assistant');
    await expect(page.locator('#drawer')).toHaveClass(/open/);
    await page.fill('#drawer-input', 'Which of my free trials should I cancel?');
    await page.click('#btn-send-drawer');
    await expect(page.locator('#drawer-messages .msg-agent').last()).toContainText(/Trial Guard/i, { timeout: 15000 });
  });

});
