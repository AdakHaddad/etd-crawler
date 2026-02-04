const puppeteer = require('puppeteer');
const fs = require('fs');

async function replayWithBrowser() {
    console.log('🚀 Starting browser session replay...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    try {
        // Read HAR file and extract cookies
        const harFile = 'etd.intranet.lib.ugm_Archive [25-10-10 06-55-40].har';
        const harData = JSON.parse(fs.readFileSync(harFile, 'utf8'));
        
        // Extract cookies from HAR
        const cookies = [];
        harData.log.entries.forEach(entry => {
            if (entry.response && entry.response.cookies) {
                entry.response.cookies.forEach(cookie => {
                    cookies.push({
                        name: cookie.name,
                        value: cookie.value,
                        domain: cookie.domain,
                        path: cookie.path,
                        expires: cookie.expires ? cookie.expires / 1000 : undefined,
                        httpOnly: cookie.httpOnly || false,
                        secure: cookie.secure || false
                    });
                });
            }
        });
        
        // Set cookies in browser
        if (cookies.length > 0) {
            await page.setCookie(...cookies);
            console.log(`🍪 Set ${cookies.length} cookies`);
        }
        
        // Navigate to the site
        const targetUrl = 'http://etd.intranet.lib.ugm/';
        console.log(`🌐 Navigating to: ${targetUrl}`);
        
        await page.goto(targetUrl, { waitUntil: 'networkidle2' });
        
        console.log('✅ Page loaded successfully!');
        console.log('📄 Current URL:', page.url());
        console.log('📋 Page title:', await page.title());
        
        // Wait for user interaction
        console.log('\n🎯 Browser is ready! You can now interact with the site.');
        console.log('Press Ctrl+C to close the browser when done.');
        
        // Keep browser open
        await new Promise(() => {});
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        // await browser.close();
    }
}

// Install puppeteer if not available
async function ensurePuppeteer() {
    try {
        require('puppeteer');
        return true;
    } catch (error) {
        console.log('📦 Installing puppeteer...');
        const { execSync } = require('child_process');
        execSync('npm install puppeteer', { stdio: 'inherit' });
        return true;
    }
}

if (require.main === module) {
    ensurePuppeteer().then(() => {
        replayWithBrowser().catch(console.error);
    });
}

module.exports = replayWithBrowser;
