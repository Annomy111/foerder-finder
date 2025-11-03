/**
 * Complete E2E Test: Application Creation + AI Draft Generation
 * Tests the full workflow from login to AI-generated draft
 */

const puppeteer = require('puppeteer');

(async () => {
  console.log('\n🚀 COMPLETE E2E TEST - Application + AI Draft\n');
  console.log('='.repeat(70));

  const browser = await puppeteer.launch({
    headless: false,
    args: ['--ignore-certificate-errors', '--disable-web-security', '--no-sandbox'],
    ignoreHTTPSErrors: true,
    defaultViewport: { width: 1400, height: 900 }
  });

  const page = await browser.newPage();
  let results = {
    passed: 0,
    failed: 0,
    tests: []
  };

  function logTest(name, passed, details = '') {
    const icon = passed ? '✅' : '❌';
    console.log(`${icon} ${name} ${details}`);
    results.tests.push({ name, passed, details });
    if (passed) results.passed++;
    else results.failed++;
  }

  try {
    // ====================================================================
    // STEP 1: Login
    // ====================================================================
    console.log('\n📝 STEP 1: LOGIN');
    console.log('-'.repeat(70));

    await page.goto('https://edufunds.org/login', { waitUntil: 'networkidle0', timeout: 30000 });
    await page.type('input[type="email"]', 'admin@gs-musterberg.de');
    await page.type('input[type="password"]', 'admin123');

    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);

    const isLoggedIn = page.url() === 'https://edufunds.org/';
    logTest('Login successful', isLoggedIn, `(URL: ${page.url()})`);

    if (!isLoggedIn) {
      throw new Error('Login failed - cannot proceed with tests');
    }

    await new Promise(resolve => setTimeout(resolve, 2000));

    // ====================================================================
    // STEP 2: Get Auth Token from LocalStorage
    // ====================================================================
    console.log('\n🔐 STEP 2: GET AUTH TOKEN');
    console.log('-'.repeat(70));

    const authData = await page.evaluate(() => {
      const authStorage = localStorage.getItem('auth-storage');
      if (!authStorage) return null;
      const parsed = JSON.parse(authStorage);
      return {
        token: parsed.state?.token,
        user: parsed.state?.user
      };
    });

    logTest('Auth token retrieved', !!authData?.token, `(User: ${authData?.user?.email})`);

    if (!authData?.token) {
      throw new Error('No auth token found - cannot proceed');
    }

    const TOKEN = authData.token;
    console.log('Token length:', TOKEN.length);

    // ====================================================================
    // STEP 3: Get Funding ID
    // ====================================================================
    console.log('\n💰 STEP 3: GET FUNDING OPPORTUNITY');
    console.log('-'.repeat(70));

    const fundingResponse = await page.evaluate(async (token) => {
      const response = await fetch('https://api.edufunds.org/api/v1/funding/?limit=1', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return {
        status: response.status,
        data: await response.json()
      };
    }, TOKEN);

    logTest('Funding list retrieved', fundingResponse.status === 200, `(Status: ${fundingResponse.status})`);

    const fundingId = fundingResponse.data[0]?.funding_id;
    const fundingTitle = fundingResponse.data[0]?.title;
    logTest('Funding ID extracted', !!fundingId, `(${fundingTitle})`);

    if (!fundingId) {
      throw new Error('No funding opportunities found');
    }

    // ====================================================================
    // STEP 4: Create Application
    // ====================================================================
    console.log('\n📄 STEP 4: CREATE APPLICATION');
    console.log('-'.repeat(70));

    const applicationData = {
      funding_id: fundingId,
      title: 'E2E Test: Digitalisierung im Mathematikunterricht',
      projektbeschreibung: 'Wir planen die Anschaffung von 30 Tablets für den digitalen Mathematikunterricht in den Klassen 3 und 4. Die Schüler sollen damit interaktive Lern-Apps nutzen und mathematische Konzepte besser verstehen können. Ziel ist die Verbesserung der MINT-Kompetenzen.'
    };

    const createResponse = await page.evaluate(async (token, data) => {
      try {
        const response = await fetch('https://api.edufunds.org/api/v1/applications/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });

        const text = await response.text();
        let jsonData;
        try {
          jsonData = JSON.parse(text);
        } catch (e) {
          jsonData = { error: text };
        }

        return {
          status: response.status,
          data: jsonData
        };
      } catch (error) {
        return {
          status: 0,
          error: error.message
        };
      }
    }, TOKEN, applicationData);

    logTest('Application creation request', createResponse.status === 201, `(Status: ${createResponse.status})`);

    if (createResponse.status !== 201) {
      console.log('Application creation failed:', createResponse);
      throw new Error(`Application creation failed with status ${createResponse.status}`);
    }

    const applicationId = createResponse.data.application_id;
    logTest('Application ID received', !!applicationId, `(ID: ${applicationId})`);

    console.log(`Created application: ${applicationData.title}`);

    // ====================================================================
    // STEP 5: Generate AI Draft
    // ====================================================================
    console.log('\n🤖 STEP 5: GENERATE AI DRAFT');
    console.log('-'.repeat(70));

    const draftRequest = {
      application_id: applicationId,
      funding_id: fundingId,
      user_query: applicationData.projektbeschreibung
    };

    const draftResponse = await page.evaluate(async (token, data) => {
      try {
        const response = await fetch('https://api.edufunds.org/api/v2/drafts/generate', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });

        const text = await response.text();
        let jsonData;
        try {
          jsonData = JSON.parse(text);
        } catch (e) {
          jsonData = { error: text };
        }

        return {
          status: response.status,
          data: jsonData
        };
      } catch (error) {
        return {
          status: 0,
          error: error.message
        };
      }
    }, TOKEN, draftRequest);

    logTest('AI draft generation request', draftResponse.status === 200 || draftResponse.status === 201, `(Status: ${draftResponse.status})`);

    if (draftResponse.status === 200 || draftResponse.status === 201) {
      const draftText = draftResponse.data.draft_text || draftResponse.data.generated_text;
      const draftLength = draftText?.length || 0;

      logTest('Draft text generated', draftLength > 100, `(${draftLength} characters)`);
      logTest('AI model info present', !!draftResponse.data.ai_model, `(Model: ${draftResponse.data.ai_model})`);

      console.log('\n📝 Generated Draft Preview:');
      console.log('-'.repeat(70));
      console.log(draftText?.substring(0, 300) + '...');
      console.log('-'.repeat(70));
    } else {
      console.log('AI draft generation response:', draftResponse);
      logTest('AI draft generation', false, `(Failed with status ${draftResponse.status})`);
    }

    // ====================================================================
    // STEP 6: Verify Application in List
    // ====================================================================
    console.log('\n📋 STEP 6: VERIFY APPLICATION IN LIST');
    console.log('-'.repeat(70));

    const listResponse = await page.evaluate(async (token) => {
      const response = await fetch('https://api.edufunds.org/api/v1/applications/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return {
        status: response.status,
        data: await response.json()
      };
    }, TOKEN);

    logTest('Application list retrieved', listResponse.status === 200, `(Status: ${listResponse.status})`);

    const appCount = listResponse.data.length;
    logTest('Created application in list', appCount > 0, `(${appCount} applications found)`);

    const createdApp = listResponse.data.find(app => app.application_id === applicationId);
    logTest('Correct application found', !!createdApp, `(Title: ${createdApp?.title})`);

  } catch (error) {
    console.error('\n❌ TEST ERROR:', error.message);
    logTest('Test execution', false, error.message);
    await page.screenshot({ path: 'test-ai-draft-error.png', fullPage: true });
  }

  // ====================================================================
  // FINAL RESULTS
  // ====================================================================
  console.log('\n' + '='.repeat(70));
  console.log('📊 FINAL TEST RESULTS');
  console.log('='.repeat(70));
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📈 Success Rate: ${Math.round(results.passed / (results.passed + results.failed) * 100)}%`);

  if (results.failed === 0) {
    console.log('\n🎉 🎉 🎉 ALL TESTS PASSED! APPLICATION + AI WORKING! 🎉 🎉 🎉\n');
  } else {
    console.log('\n⚠️  Some tests failed. Review the details above.\\n');
  }

  console.log('\n⏳ Keeping browser open for 10 seconds for inspection...');
  await new Promise(resolve => setTimeout(resolve, 10000));

  await browser.close();
  console.log('✅ Test suite completed!\n');
})();
