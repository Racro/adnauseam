const fs = require('fs').promises;
const puppeteer = require('puppeteer');
const Xvfb = require('xvfb');
const yargs = require('yargs');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const puppeteerExtra = require('puppeteer-extra');

var arguments = yargs.argv;
const arg_url = arguments.url;

let keyword = '';
if (arg_url.includes('http')) {
    keyword = arg_url.split('://')[1].split('/')[0];
} else {
    keyword = arg_url.split('/')[0];
}

if (keyword.includes('www')) {
    keyword = keyword.split('www.')[1];
}

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

(async () => {
    // Update these paths as needed
    const braveBinary = '../accads_crawler/chrome-linux/chrome';  // Path to your Brave browser binary
    // const braveBinary = '/usr/bin/chromium-browser';  // Path to your Brave browser binary
    const extensionPath = '/home/ritik/Downloads/adnauseam.chromium';  // Path to the AdNauseam extension directory
    const userProfileDir = 'temp_dir';  // Path to the user profile directory

    // if (arg_headless == 'true'){
    // xvfb.startSync((err)=>{if (err) console.error(err)});
    // pup_args.push(`--display=${arg_display}`);
    // console.error(`\nXVFB: ${xvfb._display}\n`)
    // }

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
            `--load-extension=${extensionPath}`,
            `--user-data-dir=${userProfileDir}`
        ]
    });

    const page = await browser.newPage();
    // websites = ['chrome://extensions']
    try {
        console.log(`Navigating to: ${arg_url}`);
        await page.setViewport({ width: 1920, height: 1080 });
        await page.goto(arg_url, { waitUntil: 'load' });
    } catch (error) {
        console.error(`Error with ${arg_url}: ${error}`);
    }

    try{
        // Wait a few seconds to let the page load or for the extension to act
        await page.screenshot({ path: `ss/${keyword}.png`});
        await new Promise(r => setTimeout(r, 3000));
        // await new Promise(r => setTimeout(r, 30000));
        // console.log('111111111111111111');
        await autoScroll(page);
        // console.log('22222222222222222');

        await new Promise(r => setTimeout(r, 1000));
        
    } catch (error) {
        console.error(`Error with ${arg_url}: ${error}`);
    }
    
    await browser.close();

    // xvfb.stopSync();
})();