const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  console.log('📸 Navigating to deployed site: https://f72756da.edufunds.pages.dev...');

  try {
    await page.goto('https://f72756da.edufunds.pages.dev', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // Take homepage screenshot
    await page.screenshot({
      path: '/tmp/deployed-homepage.png',
      fullPage: true
    });
    console.log('✅ Homepage screenshot saved to /tmp/deployed-homepage.png');

    // Wait a bit and check for any console errors
    const logs = [];
    page.on('console', msg => logs.push(msg.text()));

    await page.waitForTimeout(2000);

    if (logs.length > 0) {
      console.log('\n📋 Console logs:');
      logs.forEach(log => console.log('  ', log));
    }

    console.log('\n✅ Deployment verification complete');
    console.log('   URL: https://f72756da.edufunds.pages.dev');
    console.log('   Screenshot: /tmp/deployed-homepage.png');

  } catch (e) {
    console.error('❌ Error:', e.message);
  }

  await browser.close();
})();
