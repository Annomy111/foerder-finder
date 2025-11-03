/**
 * Comprehensive Feature Test for EduFunds Platform
 * Tests all major functionality end-to-end
 */

const puppeteer = require('puppeteer');

(async () => {
  console.log('\n🚀 COMPREHENSIVE FEATURE TEST - EduFunds Platform\n');
  console.log('='.repeat(70));

  const browser = await puppeteer.launch({
    headless: false,
    args: ['--ignore-certificate-errors', '--disable-web-security', '--no-sandbox'],
    ignoreHTTPSErrors: true,
    defaultViewport: { width: 1400, height: 900 }
  });

  const page = await browser.newPage();
  let testResults = {
    passed: 0,
    failed: 0,
    tests: []
  };

  function logTest(name, passed, details = '') {
    const icon = passed ? '✅' : '❌';
    console.log(`${icon} ${name} ${details}`);
    testResults.tests.push({ name, passed, details });
    if (passed) testResults.passed++;
    else testResults.failed++;
  }

  try {
    // ====================================================================
    // TEST 1: Login Functionality
    // ====================================================================
    console.log('\n📝 TEST 1: LOGIN FUNCTIONALITY');
    console.log('-'.repeat(70));

    await page.goto('https://edufunds.org/login', { waitUntil: 'networkidle0', timeout: 30000 });
    logTest('Login page loads', true);

    await page.type('input[type="email"]', 'admin@gs-musterberg.de');
    await page.type('input[type="password"]', 'admin123');
    logTest('Credentials entered', true);

    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);

    const isLoggedIn = page.url() === 'https://edufunds.org/';
    logTest('Login redirects to dashboard', isLoggedIn, `(URL: ${page.url()})`);

    await page.waitForTimeout(3000); // Wait for dashboard to load

    // ====================================================================
    // TEST 2: Dashboard Display
    // ====================================================================
    console.log('\n📊 TEST 2: DASHBOARD DISPLAY');
    console.log('-'.repeat(70));

    const dashboardContent = await page.evaluate(() => {
      const heading = document.querySelector('h1');
      const statCards = document.querySelectorAll('.card-interactive, .card');
      const fundingSection = document.body.textContent.includes('Neue Fördermittel');

      return {
        hasHeading: !!heading,
        headingText: heading?.textContent || '',
        statCardsCount: statCards.length,
        hasFundingSection: fundingSection
      };
    });

    logTest('Dashboard heading present', dashboardContent.hasHeading, `("${dashboardContent.headingText}")`);
    logTest('Stat cards rendered', dashboardContent.statCardsCount >= 3, `(${dashboardContent.statCardsCount} cards)`);
    logTest('Funding section visible', dashboardContent.hasFundingSection);

    await page.screenshot({ path: 'test-dashboard.png' });
    console.log('📸 Screenshot saved: test-dashboard.png');

    // ====================================================================
    // TEST 3: Fördermittel List Page
    // ====================================================================
    console.log('\n📋 TEST 3: FÖRDERMITTEL LIST PAGE');
    console.log('-'.repeat(70));

    await page.click('a[href="/funding"]');
    await page.waitForTimeout(2000);

    const fundingListUrl = page.url();
    logTest('Navigate to Fördermittel page', fundingListUrl.includes('/funding'), `(${fundingListUrl})`);

    const fundingList = await page.evaluate(() => {
      const heading = document.querySelector('h1')?.textContent || '';
      const fundingCards = document.querySelectorAll('.card, [class*="funding"]');
      return {
        heading,
        fundingCount: fundingCards.length
      };
    });

    logTest('Fördermittel page loads', fundingList.heading.toLowerCase().includes('förder'), `("${fundingList.heading}")`);
    logTest('Funding opportunities displayed', fundingList.fundingCount > 0, `(${fundingList.fundingCount} items)`);

    await page.screenshot({ path: 'test-funding-list.png' });
    console.log('📸 Screenshot saved: test-funding-list.png');

    // ====================================================================
    // TEST 4: Fördermittel Detail Page
    // ====================================================================
    console.log('\n🔍 TEST 4: FÖRDERMITTEL DETAIL PAGE');
    console.log('-'.repeat(70));

    // Click on first funding opportunity
    const firstFundingLink = await page.$('a[href^="/funding/"]');
    if (firstFundingLink) {
      await firstFundingLink.click();
      await page.waitForTimeout(2000);

      const detailUrl = page.url();
      logTest('Navigate to funding detail', detailUrl.includes('/funding/'), `(${detailUrl})`);

      const detailContent = await page.evaluate(() => {
        const title = document.querySelector('h1, h2')?.textContent || '';
        const hasContent = document.body.textContent.length > 500;
        return { title, hasContent };
      });

      logTest('Funding detail page loads', detailContent.hasContent, `("${detailContent.title.substring(0, 50)}...")`);

      await page.screenshot({ path: 'test-funding-detail.png' });
      console.log('📸 Screenshot saved: test-funding-detail.png');
    } else {
      logTest('Navigate to funding detail', false, '(No funding links found)');
    }

    // ====================================================================
    // TEST 5: Applications Page
    // ====================================================================
    console.log('\n📄 TEST 5: APPLICATIONS PAGE');
    console.log('-'.repeat(70));

    await page.goto('https://edufunds.org/applications', { waitUntil: 'networkidle0' });
    await page.waitForTimeout(2000);

    const applicationsPage = await page.evaluate(() => {
      const heading = document.querySelector('h1')?.textContent || '';
      const emptyState = document.body.textContent.includes('Noch keine Anträge') ||
                        document.body.textContent.includes('keine Anträge');
      return { heading, emptyState };
    });

    logTest('Applications page loads', applicationsPage.heading.toLowerCase().includes('antrag') ||
            applicationsPage.heading.toLowerCase().includes('application'),
            `("${applicationsPage.heading}")`);
    logTest('Empty state shown (no applications)', applicationsPage.emptyState);

    await page.screenshot({ path: 'test-applications.png' });
    console.log('📸 Screenshot saved: test-applications.png');

    // ====================================================================
    // TEST 6: Navigation & Logout
    // ====================================================================
    console.log('\n🧭 TEST 6: NAVIGATION & USER INFO');
    console.log('-'.repeat(70));

    const userInfo = await page.evaluate(() => {
      const userEmail = document.body.textContent.match(/admin@gs-musterberg\.de/);
      const logoutButton = document.body.textContent.includes('Logout');
      const nav = document.querySelector('nav, header');
      return {
        hasUserEmail: !!userEmail,
        hasLogoutButton: logoutButton,
        hasNavigation: !!nav
      };
    });

    logTest('User email displayed', userInfo.hasUserEmail);
    logTest('Logout button present', userInfo.hasLogoutButton);
    logTest('Navigation menu present', userInfo.hasNavigation);

  } catch (error) {
    console.error('\n❌ TEST ERROR:', error.message);
    logTest('Test execution', false, error.message);
    await page.screenshot({ path: 'test-error.png' });
  }

  // ====================================================================
  // TEST 7: API Health Check (Direct)
  // ====================================================================
  console.log('\n🔌 TEST 7: API HEALTH CHECK');
  console.log('-'.repeat(70));

  try {
    const apiResponse = await page.evaluate(async () => {
      const response = await fetch('https://api.edufunds.org/api/v1/health');
      return {
        status: response.status,
        data: await response.json()
      };
    });

    logTest('API health endpoint', apiResponse.status === 200, `(Status: ${apiResponse.status})`);
    logTest('API returns valid JSON', !!apiResponse.data.status, `(Status: ${apiResponse.data.status})`);
    logTest('Advanced RAG enabled', apiResponse.data.advanced_rag === 'enabled');
  } catch (error) {
    logTest('API health check', false, error.message);
  }

  // ====================================================================
  // FINAL RESULTS
  // ====================================================================
  console.log('\n' + '='.repeat(70));
  console.log('📊 FINAL TEST RESULTS');
  console.log('='.repeat(70));
  console.log(`✅ Passed: ${testResults.passed}`);
  console.log(`❌ Failed: ${testResults.failed}`);
  console.log(`📈 Success Rate: ${Math.round(testResults.passed / (testResults.passed + testResults.failed) * 100)}%`);

  if (testResults.failed === 0) {
    console.log('\n🎉 🎉 🎉 ALL TESTS PASSED! PLATFORM FULLY OPERATIONAL! 🎉 🎉 🎉\n');
  } else {
    console.log('\n⚠️  Some tests failed. Review the details above.\n');
  }

  console.log('\n⏳ Keeping browser open for 10 seconds for inspection...');
  await page.waitForTimeout(10000);

  await browser.close();
  console.log('✅ Test suite completed!\n');
})();
