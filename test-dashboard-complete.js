/**
 * Complete Dashboard Test - Waits for dashboard data to load
 */

const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Starting Complete Dashboard Test...\n');

  const browser = await puppeteer.launch({
    headless: false,
    args: ['--ignore-certificate-errors', '--disable-web-security', '--no-sandbox'],
    ignoreHTTPSErrors: true
  });

  const page = await browser.newPage();

  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`❌ Console Error: ${msg.text()}`);
    }
  });

  try {
    // Step 1: Login
    console.log('1️⃣  Logging in...');
    await page.goto('https://edufunds.org/login', { waitUntil: 'networkidle0' });
    await page.type('input[type="email"]', 'admin@gs-musterberg.de');
    await page.type('input[type="password"]', 'admin123');
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);
    console.log('✅ Logged in\n');

    // Step 2: Wait for dashboard heading or content to appear
    console.log('2️⃣  Waiting for dashboard content...');

    try {
      // Wait for either the dashboard heading or any stat card
      await page.waitForSelector('h1:has-text("Dashboard"), .card-interactive', { timeout: 15000 });
      console.log('✅ Dashboard content detected!\n');
    } catch (e) {
      console.log('⚠️  Dashboard content did not appear within 15 seconds\n');
    }

    // Step 3: Check what's actually on the page
    const pageContent = await page.evaluate(() => {
      const body = document.body;
      const hasLoadingSpinner = body.textContent.includes('Dashboard wird geladen') || body.textContent.includes('Loading');
      const hasDashboardHeading = !!document.querySelector('h1');
      const dashboardHeadingText = document.querySelector('h1')?.textContent || 'none';
      const hasStatCards = document.querySelectorAll('.card-interactive, .card').length > 0;
      const statCardsCount = document.querySelectorAll('.card-interactive, .card').length;

      return {
        url: window.location.href,
        hasLoadingSpinner,
        hasDashboardHeading,
        dashboardHeadingText,
        hasStatCards,
        statCardsCount,
        bodyTextPreview: body.textContent.substring(0, 300)
      };
    });

    console.log('📊 Page Analysis:');
    console.log('   URL:', pageContent.url);
    console.log('   Loading Spinner:', pageContent.hasLoadingSpinner ? '✅ Visible' : '❌ Not visible');
    console.log('   Dashboard Heading:', pageContent.hasDashboardHeading ? '✅ Present' : '❌ Missing');
    console.log('   Heading Text:', pageContent.dashboardHeadingText);
    console.log('   Stat Cards:', pageContent.hasStatCards ? `✅ ${pageContent.statCardsCount} found` : '❌ None found');
    console.log('   Body Text Preview:', pageContent.bodyTextPreview);

    // Step 4: Take screenshot
    await page.screenshot({ path: 'dashboard-complete-screenshot.png', fullPage: true });
    console.log('\n📸 Screenshot saved: dashboard-complete-screenshot.png');

    // Step 5: Final verdict
    if (pageContent.hasStatCards && pageContent.statCardsCount >= 3) {
      console.log('\n✅ ✅ ✅ DASHBOARD LOADED SUCCESSFULLY! ✅ ✅ ✅\n');
    } else if (pageContent.hasLoadingSpinner) {
      console.log('\n⚠️  Dashboard is stuck in loading state\n');
    } else {
      console.log('\n❌ Dashboard failed to load content\n');
    }

  } catch (error) {
    console.error('❌ ERROR:', error.message);
    await page.screenshot({ path: 'dashboard-error-screenshot.png', fullPage: true });
  }

  console.log('⏳ Keeping browser open for 10 seconds...');
  await new Promise(resolve => setTimeout(resolve, 10000));

  await browser.close();
  console.log('✅ Test completed!\n');
})();
