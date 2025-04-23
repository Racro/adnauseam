// puppeteer_redirect.js
// Usage: xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" node puppeteer_redirect.js <url>

const puppeteer = require('puppeteer');

(async () => {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node puppeteer_redirect.js <url>');
    process.exit(1);
  }

  let trail = [];
  let finalUrl = url;

  try {
    // Launch headless Chromium (or visible for debugging)
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // Intercept navigation requests to build the redirect trail
    await page.setRequestInterception(true);
    page.on('request', req => {
      if (req.isNavigationRequest()) {
        trail.push(req.url());
      }
      req.continue();
    });

    // Navigate and capture final URL
    const response = await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    trail.push(response.url());
    finalUrl = response.url();

    await browser.close();
  } catch (err) {
    console.error('⮞ Puppeteer navigation failed:', err.message);
    throw err;
  }

  // Emit result JSON
  const hop_count = Math.max(0, trail.length - 1);
  console.log(JSON.stringify({
    hop_count,
    redirect_trail: trail.length ? trail : [url],
    final_url: finalUrl
  }));
  process.exit(0);
})();
