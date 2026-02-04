# Manual Browser Setup for HAR Replay

## Option 1: Chrome Developer Tools
1. Open Chrome and press F12
2. Go to **Application** tab → **Cookies**
3. Manually add the cookies from your HAR file:
   - Name: `JSESSIONID`
   - Value: `9FA04892334589095A62EC14A55E3172`
   - Domain: `sso.ugm.ac.id`

## Option 2: Import HAR into Network Tab
1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Click the **Import HAR** button (download icon)
4. Select your HAR file
5. Right-click on any request → "Replay XHR" or "Copy as cURL"

## Option 3: Using cURL Commands
```bash
# Extract the main request from HAR and convert to cURL
curl -X POST "https://sso.ugm.ac.id/cas/login?service=http%3A%2F%2Fetd.intranet.lib.ugm%2Fsignin%2F" \
  -H "Cookie: JSESSIONID=9FA04892334589095A62EC14A55E3172" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"
```

## Option 4: Browser Extension
1. Install "HAR Replay" extension
2. Import your HAR file
3. Click "Replay All" to replay the session

## Important Notes:
- ⚠️ The session may have expired (captured on 2025-10-10)
- 🔐 You may need to re-authenticate if the session is invalid
- 🌐 The site appears to be `etd.intranet.lib.ugm` (UGM intranet)
- 📝 Original session was from Firefox, but can be replayed in any browser

