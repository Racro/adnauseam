const fs = require('fs').promises;
const puppeteer = require('puppeteer');
const yargs = require('yargs');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const puppeteerExtra = require('puppeteer-extra');

var arguments = yargs.argv;
// const arg_url = arguments.url;
const urls = JSON.parse(process.argv[2]);
const MAX_TRIES = 3;

// let keyword = '';
// if (arg_url.includes('http')) {
//     keyword = arg_url.split('://')[1].split('/')[0];
// } else {
//     keyword = arg_url.split('/')[0];
// }

// if (keyword.includes('www')) {
//     keyword = keyword.split('www.')[1];
// }

// Create a new Xvfb instance
// const xvfb = new Xvfb({
//     silent: true,
//     xvfb_args: ['-screen', '0', '1024x768x24', '-ac']
// });
// xvfb.startSync((err)=>{if (err) console.error(err)});

// Function to scroll and load more content
async function autoScroll(page) {
    await page.evaluate(async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if ((totalHeight >= scrollHeight) || (totalHeight >= 30000)) {
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}

// Update these paths as needed
const braveBinary = '../accads_crawler/chrome-linux/chrome';  // Path to your Brave browser binary
// const braveBinary = '/usr/bin/chromium-browser';  // Path to your Brave browser binary
const extensionPath = '../extensions/adnauseam_extn';  // Path to the AdNauseam extension directory
// const userProfileDir = 'temp_dir';  // Path to the user profile directory

let i = 0;

(async () => {
    if (urls.length === 0) {
        console.log("❌ No URLs received.");
        process.exit(1);
    }
    
    let tries = 0;

    while (tries < MAX_TRIES) {
        let browser;
    
        try{
            // Read website URLs from websites_1000.txt
            puppeteerExtra.default.use(StealthPlugin());
            const browser = await puppeteerExtra.default.launch({
            // const browser = await puppeteer.launch({
                executablePath: braveBinary,
                headless: false,
                args: [
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--start-maximized',
                    `--disable-extensions-except=${extensionPath}`,
                    `--load-extension=${extensionPath}`
                ]
            });

            const page = await browser.newPage();
            // websites = ['chrome://extensions']

            while (i<urls.length) {
                const url = urls[i];

                let keyword = '';
                if (url.includes('http')) {
                    keyword = url.split('://')[1].split('/')[0];
                } else {
                    keyword = url.split('/')[0];
                }

                if (keyword.includes('www')) {
                    keyword = keyword.split('www.')[1];
                }

                console.log(`🔗 Visiting (${i + 1}/${urls.length}): ${url}`);
                try {
                    await page.goto(url, { timeout: 60000, waitUntil: 'load' });
                    await new Promise(r => setTimeout(r, 2000));
                    tries = 0; // reset on success
                    i += 1;

                    try{
                        // Wait a few seconds to let the page load or for the extension to act
                        await page.screenshot({ path: `ss/${keyword}.png`});
                        await new Promise(r => setTimeout(r, 3000));
                        // await new Promise(r => setTimeout(r, 30000));
                        // console.log('111111111111111111');
                        await autoScroll(page);
                        // console.log('22222222222222222');
                
                        // await new Promise(r => setTimeout(r, 50000));
                        await new Promise(r => setTimeout(r, 2000));
                        
                    } catch (error) {
                        console.error(`Error with ${url}: ${error}`);
                    }

                } catch (err) {
                    console.error(`❌ Failed: ${url} | ${err.message}`);
                    throw err; // force browser restart
                }
            }

            await browser.close();
            console.log('✅ All URLs visited successfully.');
            return;

        } catch (err) {
            console.log(`💥 Browser crash or navigation failure. Error: ${err}. Retry #${tries + 1}`);
            await browser.close();
            tries += 1;
        } finally {
            if (browser) {
                try { await browser.close(); } catch (_) {}
            }
        }
    }

    console.log(`⚠️ Exiting after ${MAX_TRIES} retries.`);
})();
