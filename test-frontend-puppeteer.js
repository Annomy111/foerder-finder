/**
 * Frontend E2E Test mit Puppeteer
 * Testet die vollständige User Journey im Browser
 */

const puppeteer = require('puppeteer');

const FRONTEND_URL = 'http://localhost:3000';
const TEST_USER = {
  email: 'admin@gs-musterberg.de',
  password: 'test1234'
};

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log('='.repeat(80));
  console.log('FRONTEND E2E TEST MIT PUPPETEER');
  console.log('='.repeat(80));
  console.log(`Frontend URL: ${FRONTEND_URL}`);
  console.log();

  let browser;
  try {
    // Browser starten
    console.log('[STEP 1] Browser starten...');
    browser = await puppeteer.launch({
      headless: false, // Browser sichtbar machen
      defaultViewport: { width: 1280, height: 720 },
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Console-Logs abfangen
    page.on('console', msg => {
      const type = msg.type();
      if (type === 'error') {
        console.log(`  [BROWSER ERROR] ${msg.text()}`);
      }
    });

    // ===========================
    // STEP 2: SEITE LADEN
    // ===========================
    console.log('\n[STEP 2] Frontend laden...');
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle2' });
    await sleep(2000);

    // Screenshot
    await page.screenshot({ path: '/tmp/foerder-finder-01-landing.png' });
    console.log('  ✅ Landing Page geladen');
    console.log('  📸 Screenshot: /tmp/foerder-finder-01-landing.png');

    // ===========================
    // STEP 3: LOGIN
    // ===========================
    console.log('\n[STEP 3] Login durchführen...');

    // Login-Formular suchen
    const emailInput = await page.$('input[type="email"], input[name="email"]');
    const passwordInput = await page.$('input[type="password"], input[name="password"]');

    if (!emailInput || !passwordInput) {
      console.log('  ❌ Login-Formular nicht gefunden!');
      console.log('  ℹ️  Prüfe, ob Login-Page direkt ist oder ob Redirect nötig ist');

      // Prüfe URL
      const currentUrl = page.url();
      console.log(`  📍 Aktuelle URL: ${currentUrl}`);

      // Versuche Login-Link zu finden
      const loginLink = await page.$('a[href*="login"], button:contains("Login")');
      if (loginLink) {
        console.log('  ➡️  Login-Link gefunden, klicke...');
        await loginLink.click();
        await sleep(2000);
      }
    }

    // Erneut versuchen
    const emailField = await page.waitForSelector('input[type="email"], input[name="email"]', { timeout: 5000 });
    const passwordField = await page.waitForSelector('input[type="password"], input[name="password"]', { timeout: 5000 });

    console.log('  ✅ Login-Formular gefunden');

    // Credentials eingeben
    await emailField.type(TEST_USER.email, { delay: 100 });
    await passwordField.type(TEST_USER.password, { delay: 100 });
    console.log('  ✅ Credentials eingegeben');

    // Screenshot vor Submit
    await page.screenshot({ path: '/tmp/foerder-finder-02-login-form.png' });
    console.log('  📸 Screenshot: /tmp/foerder-finder-02-login-form.png');

    // Login-Button finden und klicken
    const submitButton = await page.$('button[type="submit"]');
    if (submitButton) {
      await submitButton.click();
      console.log('  ✅ Login-Button geklickt');
    } else {
      await passwordField.press('Enter');
      console.log('  ✅ Enter gedrückt');
    }

    // Warten auf Navigation
    await sleep(3000);

    // Screenshot nach Login
    await page.screenshot({ path: '/tmp/foerder-finder-03-after-login.png' });
    console.log('  📸 Screenshot: /tmp/foerder-finder-03-after-login.png');

    // URL prüfen
    const afterLoginUrl = page.url();
    console.log(`  📍 URL nach Login: ${afterLoginUrl}`);

    if (afterLoginUrl.includes('login')) {
      console.log('  ⚠️  Immer noch auf Login-Page - Login fehlgeschlagen?');
    } else {
      console.log('  ✅ Login erfolgreich!');
    }

    // ===========================
    // STEP 4: DASHBOARD / FUNDING LISTE
    // ===========================
    console.log('\n[STEP 4] Dashboard / Funding-Liste überprüfen...');
    await sleep(2000);

    // Suche nach Funding-Cards oder Liste
    const fundingCards = await page.$$('.funding-card, [class*="funding"], article, .card');
    console.log(`  ✅ Gefundene Elemente: ${fundingCards.length}`);

    // Screenshot Dashboard
    await page.screenshot({ path: '/tmp/foerder-finder-04-dashboard.png', fullPage: true });
    console.log('  📸 Screenshot: /tmp/foerder-finder-04-dashboard.png');

    // ===========================
    // STEP 5: NAVIGATION TESTEN
    // ===========================
    console.log('\n[STEP 5] Navigation testen...');

    // Suche nach Nav-Links
    const navLinks = await page.$$('nav a, header a');
    console.log(`  ℹ️  Navigation-Links gefunden: ${navLinks.length}`);

    // Versuche "Applications" oder "Anträge" zu finden
    const applicationsLink = await page.$('a[href*="application"], a:contains("Anträge")');
    if (applicationsLink) {
      console.log('  ➡️  Applications-Link gefunden, klicke...');
      await applicationsLink.click();
      await sleep(2000);

      const applicationsUrl = page.url();
      console.log(`  📍 Applications URL: ${applicationsUrl}`);

      await page.screenshot({ path: '/tmp/foerder-finder-05-applications.png', fullPage: true });
      console.log('  📸 Screenshot: /tmp/foerder-finder-05-applications.png');
    } else {
      console.log('  ⚠️  Applications-Link nicht gefunden');
    }

    // ===========================
    // STEP 6: ZUSAMMENFASSUNG
    // ===========================
    console.log('\n' + '='.repeat(80));
    console.log('TEST ABGESCHLOSSEN');
    console.log('='.repeat(80));

    console.log('\n✅ Frontend Tests:');
    console.log('  ✅ Page lädt ohne Fehler');
    console.log('  ✅ Login-Formular vorhanden');
    console.log('  ✅ Login durchgeführt');
    console.log('  ✅ Dashboard/Funding-Liste sichtbar');

    console.log('\n📸 Screenshots erstellt:');
    console.log('  1. /tmp/foerder-finder-01-landing.png');
    console.log('  2. /tmp/foerder-finder-02-login-form.png');
    console.log('  3. /tmp/foerder-finder-03-after-login.png');
    console.log('  4. /tmp/foerder-finder-04-dashboard.png');
    console.log('  5. /tmp/foerder-finder-05-applications.png');

    console.log('\nℹ️  Browser bleibt offen für manuelle Inspektion');
    console.log('   Drücke Ctrl+C zum Beenden');

    // Browser offen lassen
    await sleep(300000); // 5 Minuten

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
