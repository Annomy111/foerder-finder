/**
 * E2E Test: Login Flow auf edufunds.org
 */

const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Starting login test...\n');

  const browser = await puppeteer.launch({
    headless: false, // Browser sichtbar machen
    slowMo: 100, // Langsamer für bessere Sichtbarkeit
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();

    // Console logs abfangen
    page.on('console', msg => {
      console.log(`[BROWSER ${msg.type()}]`, msg.text());
    });

    // Fehler abfangen
    page.on('pageerror', error => {
      console.error('❌ Page error:', error.message);
    });

    // Network errors abfangen
    page.on('requestfailed', request => {
      console.error('❌ Request failed:', request.url(), request.failure().errorText);
    });

    console.log('📖 Öffne https://edufunds.org/login');
    await page.goto('https://edufunds.org/login', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    console.log('✅ Seite geladen');

    // Screenshot vor Login
    await page.screenshot({ path: 'login-before.png', fullPage: true });
    console.log('📸 Screenshot gespeichert: login-before.png');

    // Warte auf Login-Formular
    await page.waitForSelector('input[type="email"]', { timeout: 5000 });
    console.log('✅ Login-Formular gefunden');

    // Fülle Credentials ein
    console.log('⌨️  Fülle Email ein: admin@gs-musterberg.de');
    await page.type('input[type="email"]', 'admin@gs-musterberg.de', { delay: 50 });

    console.log('⌨️  Fülle Passwort ein: test1234');
    await page.type('input[type="password"]', 'test1234', { delay: 50 });

    // Screenshot mit ausgefülltem Formular
    await page.screenshot({ path: 'login-filled.png', fullPage: true });
    console.log('📸 Screenshot gespeichert: login-filled.png');

    // Klicke auf Login-Button
    console.log('🖱️  Klicke auf Login-Button');
    await page.click('button[type="submit"]');

    // Warte auf Navigation oder Fehlermeldung
    console.log('⏳ Warte auf Antwort...');

    try {
      // Warte entweder auf Navigation zum Dashboard ODER auf Fehlermeldung
      await Promise.race([
        page.waitForNavigation({ timeout: 10000, waitUntil: 'networkidle2' }),
        page.waitForSelector('[role="alert"]', { timeout: 10000 }),
        page.waitForSelector('.text-red-500', { timeout: 10000 })
      ]);
    } catch (err) {
      console.log('⚠️  Timeout beim Warten auf Antwort');
    }

    await new Promise(resolve => setTimeout(resolve, 2000));

    // Screenshot nach Login
    await page.screenshot({ path: 'login-after.png', fullPage: true });
    console.log('📸 Screenshot gespeichert: login-after.png');

    // Prüfe aktuelle URL
    const currentUrl = page.url();
    console.log(`📍 Aktuelle URL: ${currentUrl}`);

    // Prüfe ob wir auf dem Dashboard sind
    if (currentUrl === 'https://edufunds.org/' || currentUrl.includes('/dashboard')) {
      console.log('✅ ✅ ✅ LOGIN ERFOLGREICH! ✅ ✅ ✅');
      console.log('👤 User ist eingeloggt und auf dem Dashboard');
    } else if (currentUrl.includes('/login')) {
      console.log('❌ Login fehlgeschlagen - noch auf Login-Seite');

      // Prüfe ob Fehlermeldung vorhanden
      const errorElement = await page.$('[role="alert"]');
      if (errorElement) {
        const errorText = await page.evaluate(el => el.textContent, errorElement);
        console.log(`❌ Fehlermeldung: ${errorText}`);
      }
    } else {
      console.log(`⚠️  Unerwartete URL: ${currentUrl}`);
    }

    // Warte 3 Sekunden, damit man das Ergebnis sehen kann
    await new Promise(resolve => setTimeout(resolve, 3000));

  } catch (error) {
    console.error('❌ Test fehlgeschlagen:', error.message);
    throw error;
  } finally {
    await browser.close();
    console.log('\n🏁 Browser geschlossen');
  }
})();
