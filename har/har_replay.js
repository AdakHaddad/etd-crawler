const fs = require('fs');
const https = require('https');
const http = require('http');

// Read HAR file
const harFile = 'etd.intranet.lib.ugm_Archive [25-10-10 06-55-40].har';
const harData = JSON.parse(fs.readFileSync(harFile, 'utf8'));

// Extract cookies and headers from the first request
const firstEntry = harData.log.entries[0];
const cookies = [];
const headers = {};

// Extract cookies
if (firstEntry.request.headers) {
    firstEntry.request.headers.forEach(header => {
        if (header.name.toLowerCase() === 'cookie') {
            cookies.push(header.value);
        } else if (header.name.toLowerCase() !== 'host') {
            headers[header.name] = header.value;
        }
    });
}

// Extract login URL
const loginUrl = firstEntry.request.url;
console.log('Login URL:', loginUrl);
console.log('Cookies:', cookies.join('; '));
console.log('Headers:', JSON.stringify(headers, null, 2));

// Function to make a request with extracted session data
function makeRequest(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const isHttps = urlObj.protocol === 'https:';
        const client = isHttps ? https : http;
        
        const options = {
            hostname: urlObj.hostname,
            port: urlObj.port || (isHttps ? 443 : 80),
            path: urlObj.pathname + urlObj.search,
            method: method,
            headers: {
                ...headers,
                'Cookie': cookies.join('; ')
            }
        };
        
        if (data) {
            options.headers['Content-Length'] = Buffer.byteLength(data);
            options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
        }
        
        const req = client.request(options, (res) => {
            let responseData = '';
            res.on('data', chunk => responseData += chunk);
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    data: responseData
                });
            });
        });
        
        req.on('error', reject);
        
        if (data) {
            req.write(data);
        }
        
        req.end();
    });
}

// Export for use
module.exports = { makeRequest, cookies, headers, loginUrl };

// If run directly, show extracted session info
if (require.main === module) {
    console.log('\n=== HAR File Analysis ===');
    console.log('Total entries:', harData.log.entries.length);
    console.log('Page title:', harData.log.pages[0].title);
    console.log('Captured on:', harData.log.pages[0].startedDateTime);
    
    // Show unique domains
    const domains = [...new Set(harData.log.entries.map(entry => new URL(entry.request.url).hostname))];
    console.log('Domains accessed:', domains);
}

