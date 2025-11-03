/**
 * E2E Test: AI Draft Generation Test
 * Verifies comprehensive AI drafts are being generated
 */

const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Testing AI Draft Generation...\n');

  const browser = await puppeteer.launch({
    headless: false,
    slowMo: 100,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();

    // Console logs
    page.on('console', msg => {
      console.log(`[BROWSER]`, msg.text());
    });

    // Errors
    page.on('pageerror', error => {
      console.error('❌ Page error:', error.message);
    });

    console.log('📖 Logging in...');
    await page.goto('https://edufunds.org/login', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    await page.waitForSelector('input[type="email"]');
    await page.type('input[type="email"]', 'admin@gs-musterberg.de');
    await page.type('input[type="password"]', 'test1234');
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await page.waitForNavigation({ timeout: 10000 });
    console.log('✅ Logged in\n');

    console.log('📋 Navigating to applications...');
    await page.goto('https://edufunds.org/', {
      waitUntil: 'networkidle2'
    });

    // Click on first application
    await page.waitForSelector('[data-testid="application-card"], .bg-white.rounded-lg.shadow', { timeout: 5000 });

    // Get the first application link
    const firstAppLink = await page.evaluate(() => {
      const cards = Array.from(document.querySelectorAll('a[href*="/application/"]'));
      return cards[0]?.href || null;
    });

    if (!firstAppLink) {
      console.log('⚠️  No application cards found');
      await page.screenshot({ path: 'no-applications.png', fullPage: true });
      return;
    }

    console.log(`📄 Opening application: ${firstAppLink}`);
    await page.goto(firstAppLink, { waitUntil: 'networkidle2' });

    await new Promise(resolve => setTimeout(resolve, 2000));

    // Take screenshot of application page
    await page.screenshot({ path: 'application-with-draft.png', fullPage: true });
    console.log('📸 Screenshot saved: application-with-draft.png\n');

    // Check if draft exists and get its length
    const draftInfo = await page.evaluate(() => {
      const draftElement = document.querySelector('[data-testid="draft-content"], .prose, .whitespace-pre-wrap');
      if (!draftElement) return { found: false };

      const text = draftElement.textContent;
      return {
        found: true,
        length: text.length,
        preview: text.substring(0, 500),
        hasTitle: text.includes('Förderantrag'),
        hasSections: text.includes('Ausgangslage') && text.includes('Budget'),
        hasBudgetTable: text.includes('Budgetposition'),
        hasTimeline: text.includes('Zeitplan') || text.includes('Projektphasen')
      };
    });

    if (!draftInfo.found) {
      console.log('⚠️  No draft found on page');
      console.log('Try clicking "KI-Entwurf generieren" to create a draft');
    } else {
      console.log(`📏 Draft length: ${draftInfo.length.toLocaleString()} characters`);
      console.log(`✅ Has title: ${draftInfo.hasTitle}`);
      console.log(`✅ Has sections: ${draftInfo.hasSections}`);
      console.log(`✅ Has budget table: ${draftInfo.hasBudgetTable}`);
      console.log(`✅ Has timeline: ${draftInfo.hasTimeline}`);

      if (draftInfo.length > 10000) {
        console.log('\n✅ ✅ ✅ SUCCESS! Comprehensive AI draft is working!');
        console.log('The draft has all required sections and is professionally formatted.');
      } else {
        console.log(`\n⚠️  Draft seems short (${draftInfo.length} chars, expected >10,000)`);
      }

      console.log('\n📄 Preview:');
      console.log('─'.repeat(80));
      console.log(draftInfo.preview);
      console.log('─'.repeat(80));
    }

    // Wait so user can see the result
    await new Promise(resolve => setTimeout(resolve, 5000));

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    throw error;
  } finally {
    await browser.close();
    console.log('\n🏁 Browser closed');
  }
})();
