/**
 * Enhanced Dashboard Debug Test - Captures network errors and console logs
 */

const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Starting Dashboard Debug Test...\n');

  const browser = await puppeteer.launch({
    headless: false,
    args: [
      '--ignore-certificate-errors',
      '--disable-web-security',
      '--no-sandbox',
    ],
    ignoreHTTPSErrors: true
  });

  const page = await browser.newPage();

  // Capture all console messages
  const consoleMessages = [];
  page.on('console', msg => {
    const text = msg.text();
    consoleMessages.push({ type: msg.type(), text });
    console.log(`[${msg.type().toUpperCase()}] ${text}`);
  });

  // Capture network failures
  const failedRequests = [];
  page.on('requestfailed', request => {
    const failure = {
      url: request.url(),
      method: request.method(),
      error: request.failure().errorText
    };
    failedRequests.push(failure);
    console.log(`❌ NETWORK FAILED: ${request.method()} ${request.url()}`);
    console.log(`   Error: ${request.failure().errorText}\n`);
  });

  // Capture successful requests
  page.on('response', response => {
    if (response.url().includes('/api/v1/')) {
      console.log(`✅ API Response: ${response.status()} ${response.url()}`);
    }
  });

  try {
    // Step 1: Login
    console.log('1️⃣  Visiting login page...');
    await page.goto('https://edufunds.org/login', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    await page.waitForSelector('input[type="email"]');
    await page.type('input[type="email"]', 'admin@gs-musterberg.de');
    await page.type('input[type="password"]', 'admin123');

    console.log('2️⃣  Logging in...');
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);

    const currentUrl = page.url();
    console.log(`✅ Logged in, current URL: ${currentUrl}\n`);

    // Step 2: Wait longer for dashboard to load
    console.log('3️⃣  Waiting 30 seconds for dashboard to load...\n');
    await page.waitForTimeout(30000);

    // Step 3: Check page state
    const pageState = await page.evaluate(() => {
      return {
        url: window.location.href,
        hasLoadingSpinner: !!document.querySelector('.loading-spinner') || document.body.textContent.includes('Dashboard wird geladen'),
        bodyText: document.body.textContent.substring(0, 500),
        authStorage: localStorage.getItem('auth-storage')
      };
    });

    console.log('\n📊 Page State After 30s:');
    console.log('   URL:', pageState.url);
    console.log('   Has Loading Spinner:', pageState.hasLoadingSpinner);
    console.log('   Auth Storage:', pageState.authStorage ? '✅ Present' : '❌ Missing');
    console.log('   Body Text Preview:', pageState.bodyText.substring(0, 200));

    // Step 4: Take final screenshot
    await page.screenshot({ path: 'dashboard-debug-screenshot.png', fullPage: true });
    console.log('\n📸 Screenshot saved: dashboard-debug-screenshot.png');

    // Step 5: Summary
    console.log('\n\n📋 SUMMARY:');
    console.log('='.repeat(60));
    console.log(`Console Messages: ${consoleMessages.length}`);
    consoleMessages.forEach((msg, i) => {
      console.log(`  ${i+1}. [${msg.type}] ${msg.text}`);
    });

    console.log(`\nFailed Requests: ${failedRequests.length}`);
    failedRequests.forEach((req, i) => {
      console.log(`  ${i+1}. ${req.method} ${req.url}`);
      console.log(`     Error: ${req.error}`);
    });

    console.log('='.repeat(60));

  } catch (error) {
    console.error('❌ ERROR:', error.message);
    await page.screenshot({ path: 'dashboard-error-screenshot.png', fullPage: true });
  }

  console.log('\n⏳ Keeping browser open for 10 seconds...');
  await page.waitForTimeout(10000);

  await browser.close();
  console.log('✅ Test completed!\n');
})();
