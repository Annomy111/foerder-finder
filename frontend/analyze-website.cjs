const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  console.log('Navigating to https://658e43c1.edufunds.pages.dev...');

  try {
    await page.goto('https://658e43c1.edufunds.pages.dev', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // Take homepage screenshot
    await page.screenshot({ path: '/tmp/website-homepage.png', fullPage: true });
    console.log('✅ Homepage screenshot saved to /tmp/website-homepage.png');

    // Try to navigate to a funding detail page
    await page.waitForSelector('a[href*="/funding/"]', { timeout: 10000 });
    const fundingLinks = await page.$$('a[href*="/funding/"]');

    if (fundingLinks.length > 0) {
      // Click the first funding link
      await fundingLinks[0].click();
      await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });

      // Wait a bit for any dynamic content
      await page.waitForTimeout(2000);

      await page.screenshot({ path: '/tmp/website-detail.png', fullPage: true });
      console.log('✅ Detail page screenshot saved to /tmp/website-detail.png');

      // Analyze spacing issues
      console.log('\n📊 Analyzing layout issues...\n');

      const issues = await page.evaluate(() => {
        const problems = [];

        // Check for elements with excessive spacing
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
          const style = window.getComputedStyle(el);
          const marginTop = parseInt(style.marginTop);
          const marginBottom = parseInt(style.marginBottom);
          const paddingTop = parseInt(style.paddingTop);
          const paddingBottom = parseInt(style.paddingBottom);

          // Check for excessive margins
          if (marginTop > 100 || marginBottom > 100) {
            problems.push({
              type: 'Excessive Margin',
              element: el.tagName + (el.className ? '.' + el.className.split(' ')[0] : ''),
              marginTop,
              marginBottom
            });
          }

          // Check for excessive padding
          if (paddingTop > 100 || paddingBottom > 100) {
            problems.push({
              type: 'Excessive Padding',
              element: el.tagName + (el.className ? '.' + el.className.split(' ')[0] : ''),
              paddingTop,
              paddingBottom
            });
          }
        });

        // Check for empty sections
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
          const text = card.textContent.trim();
          if (text.length < 10) {
            problems.push({
              type: 'Empty/Short Card',
              element: `Card #${index + 1}`,
              content: text
            });
          }
        });

        // Check for whitespace-pre-wrap issues
        const preWrapElements = Array.from(document.querySelectorAll('*')).filter(el => {
          return window.getComputedStyle(el).whiteSpace === 'pre-wrap';
        });

        if (preWrapElements.length > 0) {
          problems.push({
            type: 'Whitespace Pre-wrap',
            count: preWrapElements.length,
            elements: preWrapElements.slice(0, 3).map(el =>
              el.tagName + (el.className ? '.' + el.className.split(' ')[0] : '')
            )
          });
        }

        return problems.slice(0, 20); // Limit to first 20 issues
      });

      if (issues.length > 0) {
        console.log('Found potential issues:');
        issues.forEach((issue, i) => {
          console.log(`\n${i + 1}. ${issue.type}`);
          console.log(`   Element: ${issue.element || issue.elements?.join(', ') || 'Multiple'}`);
          if (issue.marginTop) console.log(`   Margin Top: ${issue.marginTop}px`);
          if (issue.marginBottom) console.log(`   Margin Bottom: ${issue.marginBottom}px`);
          if (issue.paddingTop) console.log(`   Padding Top: ${issue.paddingTop}px`);
          if (issue.paddingBottom) console.log(`   Padding Bottom: ${issue.paddingBottom}px`);
          if (issue.content) console.log(`   Content: "${issue.content}"`);
          if (issue.count) console.log(`   Count: ${issue.count}`);
        });
      } else {
        console.log('✅ No major spacing issues detected!');
      }
    }
  } catch (error) {
    console.error('Error during analysis:', error.message);
  }

  await browser.close();
})();
