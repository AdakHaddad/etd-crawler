const { makeRequest, cookies, headers, loginUrl } = require('./har_replay');

async function replaySession() {
    console.log('🔄 Replaying UGM Intranet session...\n');
    
    try {
        // Try to access the main page first
        const mainUrl = 'http://etd.intranet.lib.ugm/';
        console.log(`📡 Making request to: ${mainUrl}`);
        
        const response = await makeRequest(mainUrl);
        
        console.log(`✅ Response Status: ${response.statusCode}`);
        console.log(`📄 Response Headers:`, Object.keys(response.headers));
        
        // Check if we got redirected or if session is still valid
        if (response.statusCode === 200) {
            console.log('🎉 Session appears to be valid! You can access the site.');
            
            // Save response to file for inspection
            require('fs').writeFileSync('response.html', response.data);
            console.log('📁 Response saved to response.html');
            
        } else if (response.statusCode === 302 || response.statusCode === 301) {
            console.log('🔄 Redirected - checking redirect location...');
            console.log('Location:', response.headers.location);
        } else {
            console.log('❌ Session may have expired or requires re-authentication');
        }
        
    } catch (error) {
        console.error('❌ Error replaying session:', error.message);
    }
}

// Run if called directly
if (require.main === module) {
    replaySession();
}

module.exports = replaySession;

