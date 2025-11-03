/**
 * KOMPLETTER FRONTEND WALKTHROUGH MIT SCREENSHOTS
 * Testet jeden einzelnen Screen und Feature
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const FRONTEND_URL = 'http://localhost:3000';
const TEST_USER = {
  email: 'admin@gs-musterberg.de',
  password: 'test1234'
};

const SCREENSHOT_DIR = '/tmp/foerder-finder-walkthrough';

// Screenshot-Verzeichnis erstellen
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function takeScreenshot(page, name, fullPage = false) {
  const filename = path.join(SCREENSHOT_DIR, `${name}.png`);
  await page.screenshot({ path: filename, fullPage });
  console.log(`  📸 Screenshot: ${name}.png`);
  return filename;
}

async function main() {
  console.log('═'.repeat(100));
  console.log('FRONTEND KOMPLETTER WALKTHROUGH MIT SCREENSHOTS');
  console.log('═'.repeat(100));
  console.log(`Frontend: ${FRONTEND_URL}`);
  console.log(`Screenshots: ${SCREENSHOT_DIR}`);
  console.log('');

  let browser;
  let screenshotCount = 0;

  try {
    // Browser starten
    console.log('[STEP 1] Browser starten...');
    browser = await puppeteer.launch({
      headless: false,
      defaultViewport: { width: 1920, height: 1080 },
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Console & Network Errors sammeln
    const errors = { console: [], network: [] };

    page.on('console', msg => {
      const type = msg.type();
      if (type === 'error') {
        errors.console.push(msg.text());
      }
    });

    page.on('response', response => {
      if (response.status() >= 400) {
        errors.network.push(`${response.status()} - ${response.url()}`);
      }
    });

    console.log('  ✅ Browser gestartet (1920x1080)');

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 2: LANDING PAGE
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 2] Landing Page laden...');

    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle2' });
    await sleep(2000);

    await takeScreenshot(page, '01-landing-page', true);
    screenshotCount++;

    // Titel prüfen
    const title = await page.title();
    console.log(`  ✅ Page Title: "${title}"`);

    // URL prüfen
    const url = page.url();
    console.log(`  📍 URL: ${url}`);

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 3: LOGIN FORMULAR
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 3] Login-Formular...');

    // Warte auf Login-Formular
    try {
      await page.waitForSelector('input[type="email"], input[name="email"]', { timeout: 5000 });
      console.log('  ✅ Login-Formular gefunden');
    } catch (e) {
      console.log('  ℹ️  Kein Login-Formular auf Landing Page');

      // Suche Login-Button/Link
      const loginButton = await page.$('a[href*="login"], button:has-text("Login"), a:has-text("Login")');
      if (loginButton) {
        console.log('  ➡️  Login-Link gefunden, klicke...');
        await loginButton.click();
        await sleep(2000);
        await takeScreenshot(page, '02-login-page-after-click', true);
        screenshotCount++;
      }
    }

    // Email & Password eingeben
    const emailInput = await page.waitForSelector('input[type="email"], input[name="email"]', { timeout: 5000 });
    const passwordInput = await page.waitForSelector('input[type="password"], input[name="password"]', { timeout: 5000 });

    await emailInput.type(TEST_USER.email, { delay: 50 });
    await passwordInput.type(TEST_USER.password, { delay: 50 });

    await takeScreenshot(page, '03-login-filled', true);
    screenshotCount++;

    console.log('  ✅ Credentials eingegeben');

    // Login absenden
    const submitButton = await page.$('button[type="submit"]');
    if (submitButton) {
      await submitButton.click();
    } else {
      await passwordInput.press('Enter');
    }

    console.log('  ✅ Login abgeschickt');
    await sleep(3000);

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 4: DASHBOARD / HOME NACH LOGIN
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 4] Dashboard nach Login...');

    await takeScreenshot(page, '04-dashboard-after-login', true);
    screenshotCount++;

    const afterLoginUrl = page.url();
    console.log(`  📍 URL nach Login: ${afterLoginUrl}`);

    if (afterLoginUrl.includes('login')) {
      console.log('  ⚠️  Immer noch auf Login-Page!');
    } else {
      console.log('  ✅ Login erfolgreich - Redirect erfolgt');
    }

    // UI-Elemente zählen
    const cards = await page.$$('.card, [class*="card"], article, [class*="funding"]');
    console.log(`  📊 UI-Elemente gefunden: ${cards.length}`);

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 5: NAVIGATION TESTEN
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 5] Navigation testen...');

    const navLinks = await page.$$('nav a, header a, [role="navigation"] a');
    console.log(`  🔗 Navigation-Links: ${navLinks.length}`);

    // Alle Nav-Links sammeln
    const navTexts = [];
    for (const link of navLinks) {
      const text = await page.evaluate(el => el.textContent?.trim(), link);
      if (text) {
        navTexts.push(text);
      }
    }
    console.log(`  📋 Nav-Items: ${navTexts.join(', ')}`);

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 6: FUNDING LISTE
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 6] Funding-Liste aufrufen...');

    // Versuche Funding-Link zu finden
    const fundingLink = await page.evaluateHandle(() => {
      const links = Array.from(document.querySelectorAll('a'));
      return links.find(link =>
        link.textContent?.toLowerCase().includes('förder') ||
        link.textContent?.toLowerCase().includes('funding') ||
        link.href?.includes('funding')
      );
    });

    if (fundingLink && fundingLink.asElement()) {
      await fundingLink.asElement().click();
      await sleep(2000);
      await takeScreenshot(page, '05-funding-list', true);
      screenshotCount++;
      console.log('  ✅ Funding-Liste geöffnet');
    } else {
      console.log('  ℹ️  Funding-Link nicht gefunden - eventuell bereits auf Liste');
      await takeScreenshot(page, '05-current-page', true);
      screenshotCount++;
    }

    // Funding-Cards zählen
    const fundingCards = await page.$$('[class*="funding"], .opportunity, article');
    console.log(`  📊 Funding-Cards: ${fundingCards.length}`);

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 7: FUNDING DETAIL
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 7] Funding-Detail aufrufen...');

    // Erste Funding-Card klicken
    if (fundingCards.length > 0) {
      await fundingCards[0].click();
      await sleep(2000);
      await takeScreenshot(page, '06-funding-detail', true);
      screenshotCount++;
      console.log('  ✅ Funding-Detail geöffnet');

      // Detail-Inhalt prüfen
      const detailContent = await page.$eval('body', el => el.textContent);
      const hasTitle = detailContent.includes('Titel') || detailContent.includes('Title');
      const hasProvider = detailContent.includes('Anbieter') || detailContent.includes('Provider');
      console.log(`  📋 Detail-Seite: Title=${hasTitle}, Provider=${hasProvider}`);
    } else {
      console.log('  ⚠️  Keine Funding-Cards gefunden zum Klicken');
    }

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 8: APPLICATIONS
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 8] Applications/Anträge...');

    // Navigate zu Applications
    const applicationsLink = await page.evaluateHandle(() => {
      const links = Array.from(document.querySelectorAll('a'));
      return links.find(link =>
        link.textContent?.toLowerCase().includes('anträge') ||
        link.textContent?.toLowerCase().includes('application') ||
        link.href?.includes('application')
      );
    });

    if (applicationsLink && applicationsLink.asElement()) {
      await applicationsLink.asElement().click();
      await sleep(2000);
      await takeScreenshot(page, '07-applications-list', true);
      screenshotCount++;
      console.log('  ✅ Applications-Seite geöffnet');

      // Unsere erstellte Application sollte hier sein
      const applicationCards = await page.$$('[class*="application"], .draft');
      console.log(`  📊 Application-Cards: ${applicationCards.length}`);

      // Erste Application klicken
      if (applicationCards.length > 0) {
        await applicationCards[0].click();
        await sleep(2000);
        await takeScreenshot(page, '08-application-detail', true);
        screenshotCount++;
        console.log('  ✅ Application-Detail geöffnet');
      }
    } else {
      console.log('  ℹ️  Applications-Link nicht gefunden');
    }

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 9: SEARCH / SUCHE
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 9] Search-Funktion...');

    const searchInput = await page.$('input[type="search"], input[placeholder*="Suche"], input[placeholder*="Search"]');

    if (searchInput) {
      await searchInput.type('Digitalisierung Grundschule', { delay: 100 });
      await sleep(1000);
      await takeScreenshot(page, '09-search-input', true);
      screenshotCount++;

      // Enter drücken oder Search-Button
      await searchInput.press('Enter');
      await sleep(2000);
      await takeScreenshot(page, '10-search-results', true);
      screenshotCount++;
      console.log('  ✅ Search durchgeführt');
    } else {
      console.log('  ℹ️  Search-Input nicht gefunden');
    }

    // ═══════════════════════════════════════════════════════════
    // SCHRITT 10: USER MENU / PROFILE
    // ═══════════════════════════════════════════════════════════
    console.log('\n[STEP 10] User Menu / Profile...');

    const userMenu = await page.$('[class*="user"], [class*="profile"], [class*="avatar"]');

    if (userMenu) {
      await userMenu.click();
      await sleep(1000);
      await takeScreenshot(page, '11-user-menu', true);
      screenshotCount++;
      console.log('  ✅ User-Menu geöffnet');
    } else {
      console.log('  ℹ️  User-Menu nicht gefunden');
    }

    // ═══════════════════════════════════════════════════════════
    // FINALE ZUSAMMENFASSUNG
    // ═══════════════════════════════════════════════════════════
    console.log('\n' + '═'.repeat(100));
    console.log('WALKTHROUGH ABGESCHLOSSEN');
    console.log('═'.repeat(100));

    console.log('\n📊 Statistik:');
    console.log(`   Screenshots: ${screenshotCount}`);
    console.log(`   Console Errors: ${errors.console.length}`);
    console.log(`   Network Errors: ${errors.network.length}`);

    if (errors.console.length > 0) {
      console.log('\n⚠️  Console Errors:');
      errors.console.forEach((err, idx) => {
        console.log(`   ${idx + 1}. ${err.substring(0, 100)}...`);
      });
    }

    if (errors.network.length > 0) {
      console.log('\n⚠️  Network Errors:');
      errors.network.forEach((err, idx) => {
        console.log(`   ${idx + 1}. ${err}`);
      });
    }

    console.log(`\n📁 Screenshots gespeichert in: ${SCREENSHOT_DIR}`);
    console.log('\nℹ️  Browser bleibt 60 Sekunden offen für manuelle Inspektion...');

    await sleep(60000);

  } catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error(error.stack);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

main();
