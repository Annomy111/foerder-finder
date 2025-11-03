const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  console.log('🔍 Comprehensive Website Review for edufunds.org\n');
  console.log('=' .repeat(80));

  try {
    // Navigate to live site
    console.log('\n📍 Navigating to https://edufunds.org...');
    await page.goto('https://edufunds.org', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // Take screenshot
    await page.screenshot({
      path: '/tmp/edufunds-homepage.png',
      fullPage: true
    });
    console.log('✅ Homepage screenshot saved: /tmp/edufunds-homepage.png');

    // Analyze page structure
    console.log('\n📊 Page Analysis:');

    // Check for broken images
    const images = await page.$$eval('img', imgs =>
      imgs.map(img => ({
        src: img.src,
        alt: img.alt,
        loaded: img.complete && img.naturalHeight !== 0
      }))
    );

    const brokenImages = images.filter(img => !img.loaded);
    if (brokenImages.length > 0) {
      console.log(`\n⚠️  Found ${brokenImages.length} broken images:`);
      brokenImages.forEach(img => console.log(`   - ${img.src}`));
    } else {
      console.log('   ✅ All images loaded successfully');
    }

    // Check for console errors
    const consoleErrors = [];
    const consoleWarnings = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
      if (msg.type() === 'warning') consoleWarnings.push(msg.text());
    });

    // Wait a bit to collect console messages
    await new Promise(resolve => setTimeout(resolve, 3000));

    if (consoleErrors.length > 0) {
      console.log(`\n❌ Console Errors (${consoleErrors.length}):`);
      consoleErrors.slice(0, 5).forEach(err => console.log(`   - ${err}`));
    }

    if (consoleWarnings.length > 0) {
      console.log(`\n⚠️  Console Warnings (${consoleWarnings.length}):`);
      consoleWarnings.slice(0, 3).forEach(warn => console.log(`   - ${warn}`));
    }

    // Check for network errors
    const failedRequests = [];
    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        failure: request.failure().errorText
      });
    });

    if (failedRequests.length > 0) {
      console.log(`\n❌ Failed Requests (${failedRequests.length}):`);
      failedRequests.forEach(req => console.log(`   - ${req.url}: ${req.failure}`));
    }

    // Analyze text elements for spacing issues
    console.log('\n📐 Spacing Analysis:');

    const spacingIssues = await page.evaluate(() => {
      const issues = [];

      // Check for elements with excessive padding/margin
      const allElements = document.querySelectorAll('*');
      allElements.forEach(el => {
        const styles = window.getComputedStyle(el);
        const padding = parseInt(styles.paddingTop) + parseInt(styles.paddingBottom);
        const margin = parseInt(styles.marginTop) + parseInt(styles.marginBottom);

        if (padding > 100) {
          issues.push(`Excessive padding (${padding}px) on ${el.tagName}.${el.className}`);
        }
        if (margin > 100) {
          issues.push(`Excessive margin (${margin}px) on ${el.tagName}.${el.className}`);
        }
      });

      return issues.slice(0, 5); // Return top 5 issues
    });

    if (spacingIssues.length > 0) {
      console.log('   ⚠️  Potential spacing issues:');
      spacingIssues.forEach(issue => console.log(`   - ${issue}`));
    } else {
      console.log('   ✅ No excessive spacing detected');
    }

    // Check accessibility
    console.log('\n♿ Accessibility Check:');

    const a11yIssues = await page.evaluate(() => {
      const issues = [];

      // Check for images without alt text
      const imgsWithoutAlt = document.querySelectorAll('img:not([alt])');
      if (imgsWithoutAlt.length > 0) {
        issues.push(`${imgsWithoutAlt.length} images missing alt text`);
      }

      // Check for buttons without accessible names
      const buttonsWithoutLabel = Array.from(document.querySelectorAll('button')).filter(btn => {
        return !btn.textContent.trim() && !btn.getAttribute('aria-label');
      });
      if (buttonsWithoutLabel.length > 0) {
        issues.push(`${buttonsWithoutLabel.length} buttons without accessible names`);
      }

      // Check for proper heading hierarchy
      const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
      const headingLevels = headings.map(h => parseInt(h.tagName[1]));
      let hierarchyIssue = false;
      for (let i = 1; i < headingLevels.length; i++) {
        if (headingLevels[i] - headingLevels[i-1] > 1) {
          hierarchyIssue = true;
          break;
        }
      }
      if (hierarchyIssue) {
        issues.push('Heading hierarchy skips levels');
      }

      return issues;
    });

    if (a11yIssues.length > 0) {
      console.log('   ⚠️  Accessibility issues found:');
      a11yIssues.forEach(issue => console.log(`   - ${issue}`));
    } else {
      console.log('   ✅ No major accessibility issues detected');
    }

    // Performance metrics
    console.log('\n⚡ Performance Metrics:');
    const metrics = await page.metrics();
    console.log(`   - JS Heap Size: ${(metrics.JSHeapUsedSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   - DOM Nodes: ${metrics.Nodes}`);
    console.log(`   - Event Listeners: ${metrics.JSEventListeners}`);

    // Check page load time
    const performanceTiming = JSON.parse(
      await page.evaluate(() => JSON.stringify(window.performance.timing))
    );
    const loadTime = performanceTiming.loadEventEnd - performanceTiming.navigationStart;
    console.log(`   - Page Load Time: ${(loadTime / 1000).toFixed(2)}s`);

    // Mobile responsiveness check
    console.log('\n📱 Mobile Responsiveness:');
    await page.setViewport({ width: 375, height: 667 });
    await page.screenshot({
      path: '/tmp/edufunds-mobile.png',
      fullPage: true
    });
    console.log('   ✅ Mobile screenshot saved: /tmp/edufunds-mobile.png');

    // Check for horizontal scrolling on mobile
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });

    if (hasHorizontalScroll) {
      console.log('   ⚠️  Horizontal scrolling detected on mobile');
    } else {
      console.log('   ✅ No horizontal scrolling on mobile');
    }

    // Final recommendations
    console.log('\n\n' + '='.repeat(80));
    console.log('📋 RECOMMENDATIONS:');
    console.log('='.repeat(80));

    const recommendations = [];

    if (brokenImages.length > 0) recommendations.push('Fix broken images');
    if (consoleErrors.length > 0) recommendations.push('Resolve console errors');
    if (spacingIssues.length > 0) recommendations.push('Review spacing consistency');
    if (a11yIssues.length > 0) recommendations.push('Improve accessibility');
    if (hasHorizontalScroll) recommendations.push('Fix mobile horizontal scrolling');
    if (loadTime > 3000) recommendations.push('Optimize page load time');

    if (recommendations.length === 0) {
      console.log('\n🎉 Excellent! No major issues found.');
      console.log('The site looks great and is production-ready!\n');
    } else {
      console.log('');
      recommendations.forEach((rec, i) => {
        console.log(`${i + 1}. ${rec}`);
      });
      console.log('');
    }

  } catch (e) {
    console.error('\n❌ Error during analysis:', e.message);
  }

  await browser.close();
})();
