/**
 * Puppeteer Login Test - Testet Login mit selbst-signiertem SSL-Zertifikat
 *
 * Installation: npm install -g puppeteer
 * Ausführung: node test-login.js
 */

const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Starte Puppeteer Login Test...\n');

  const browser = await puppeteer.launch({
    headless: false, // Browser sichtbar machen
    args: [
      '--ignore-certificate-errors',
      '--ignore-certificate-errors-spki-list',
      '--disable-web-security',
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ],
    ignoreHTTPSErrors: true // Wichtig für selbst-signierte Zertifikate!
  });

  const page = await browser.newPage();

  // Console Logs abfangen
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    if (type === 'error') {
      console.log('❌ Browser Error:', text);
    } else if (type === 'warning') {
      console.log('⚠️  Browser Warning:', text);
    }
  });

  // Network Fehler abfangen
  page.on('requestfailed', request => {
    console.log('❌ Network Failed:', request.url(), request.failure().errorText);
  });

  try {
    // Schritt 1: API Health Check (akzeptiert SSL-Zertifikat automatisch)
    console.log('1️⃣  Besuche API Health Endpoint (akzeptiere SSL-Zertifikat)...');
    await page.goto('https://api.edufunds.org/api/v1/health', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });
    console.log('✅ API Health Check erfolgreich\n');

    // Schritt 2: Login-Seite öffnen
    console.log('2️⃣  Öffne Login-Seite...');
    await page.goto('https://edufunds.org/login', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });
    console.log('✅ Login-Seite geladen\n');

    // Schritt 3: Warte auf Login-Formular
    console.log('3️⃣  Warte auf Login-Formular...');
    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    console.log('✅ Login-Formular gefunden\n');

    // Schritt 4: Credentials eingeben
    console.log('4️⃣  Gebe Credentials ein...');
    await page.type('input[type="email"]', 'admin@gs-musterberg.de', { delay: 50 });
    await page.type('input[type="password"]', 'admin123', { delay: 50 });
    console.log('✅ Credentials eingegeben\n');

    // Schritt 5: Login-Button klicken
    console.log('5️⃣  Klicke Login-Button...');

    // Warte auf Navigation nach Login
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);

    console.log('✅ Login-Request abgeschickt\n');

    // Schritt 6: Überprüfe URL nach Login
    const currentUrl = page.url();
    console.log('6️⃣  Aktuelle URL:', currentUrl);

    if (currentUrl === 'https://edufunds.org/' || currentUrl === 'https://edufunds.org/dashboard') {
      console.log('✅ LOGIN ERFOLGREICH! Weiterleitung zum Dashboard funktioniert!\n');

      // Schritt 7: Screenshot machen
      await page.screenshot({ path: 'dashboard-screenshot.png', fullPage: true });
      console.log('📸 Screenshot gespeichert: dashboard-screenshot.png\n');

      // Schritt 8: Überprüfe ob User-Daten im LocalStorage sind
      const authStorage = await page.evaluate(() => {
        return localStorage.getItem('auth-storage');
      });

      if (authStorage) {
        const authData = JSON.parse(authStorage);
        console.log('✅ Auth-Daten im LocalStorage gefunden:');
        console.log('   - User ID:', authData.state?.user?.user_id);
        console.log('   - Email:', authData.state?.user?.email);
        console.log('   - Role:', authData.state?.user?.role);
        console.log('   - Token:', authData.state?.token ? '✅ Vorhanden' : '❌ Fehlt');
      }

    } else if (currentUrl === 'https://edufunds.org/login') {
      console.log('❌ LOGIN FEHLGESCHLAGEN! Noch auf Login-Seite.\n');

      // Überprüfe ob Fehlermeldung sichtbar ist
      const errorText = await page.evaluate(() => {
        const errorEl = document.querySelector('.error, .alert, [role="alert"]');
        return errorEl ? errorEl.textContent : null;
      });

      if (errorText) {
        console.log('⚠️  Fehlermeldung:', errorText);
      }

      // Screenshot für Debugging
      await page.screenshot({ path: 'login-failed-screenshot.png', fullPage: true });
      console.log('📸 Fehler-Screenshot gespeichert: login-failed-screenshot.png\n');
    } else {
      console.log('⚠️  Unerwartete URL:', currentUrl);
    }

  } catch (error) {
    console.error('❌ FEHLER:', error.message);
    await page.screenshot({ path: 'error-screenshot.png', fullPage: true });
    console.log('📸 Fehler-Screenshot gespeichert: error-screenshot.png\n');
  }

  // Browser offen lassen für manuelle Inspektion (10 Sekunden)
  console.log('⏳ Browser bleibt 10 Sekunden offen für Inspektion...');
  await new Promise(resolve => setTimeout(resolve, 10000));

  await browser.close();
  console.log('✅ Test abgeschlossen!\n');
})();
