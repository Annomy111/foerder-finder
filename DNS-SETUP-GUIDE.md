# DNS Setup Guide for edufunds.org

## ✅ Cloudflare Dashboard Opened

I've opened the Cloudflare dashboard for you in your browser. Follow these steps to complete the DNS configuration.

---

## Step 1: Add Custom Domain to Cloudflare Pages

**In the Cloudflare Pages tab that just opened:**

1. Click on the **"Custom domains"** tab
2. Click the **"Set up a custom domain"** button
3. Enter: `edufunds.org`
4. Click **"Continue"**
5. Cloudflare will automatically:
   - Create DNS records
   - Provision SSL certificate
   - Activate the domain (takes 5-60 minutes)

**Result:** ✅ https://edufunds.org will serve your frontend

---

## Step 2: Add API Subdomain DNS Record

**In the Cloudflare main dashboard:**

1. Click on **"edufunds.org"** domain (if it exists in your account)
   - If edufunds.org is not yet in Cloudflare, you need to add it first:
     - Go to "Add a Site"
     - Enter "edufunds.org"
     - Choose Free plan
     - Update your domain nameservers at your registrar

2. Once domain is added, go to **DNS** > **Records**

3. Click **"Add record"** and configure:
   ```
   Type: A
   Name: api
   IPv4 address: 130.61.76.199
   Proxy status: ☁️ Proxied (orange cloud ON)
   TTL: Auto
   ```

4. Click **"Save"**

**Result:** ✅ https://api.edufunds.org will proxy to your backend

---

## Step 3: (Optional) Add www Redirect

**To make www.edufunds.org work:**

1. In DNS Records, click **"Add record"** again
2. Configure:
   ```
   Type: CNAME
   Name: www
   Target: edufunds.org
   Proxy status: ☁️ Proxied
   TTL: Auto
   ```
3. Click **"Save"**

**Result:** ✅ https://www.edufunds.org redirects to https://edufunds.org

---

## Step 4: Configure SSL/TLS Settings

1. Go to **SSL/TLS** tab in Cloudflare dashboard
2. Set encryption mode to **"Flexible"**
   - This allows HTTPS on frontend while backend uses HTTP
   - Cloudflare handles SSL termination

**Why Flexible?**
- Your backend doesn't have SSL certificate
- Cloudflare provides SSL to users
- Backend communication is over HTTP (proxied through Cloudflare)

---

## Step 5: Verify Configuration

After DNS propagation (5-60 minutes), test these URLs:

### Frontend Test
```bash
curl -I https://edufunds.org
# Should return: 200 OK with SSL certificate
```

### API Test
```bash
curl https://api.edufunds.org/api/v1/health
# Should return: {"status":"healthy","database":"sqlite (dev)","chromadb":"not configured","mode":"development"}
```

### Login Test
Open browser:
```
https://edufunds.org
Login: admin@gs-musterberg.de / admin123
```

---

## DNS Propagation Check

Check if DNS has propagated:

```bash
# Check main domain
dig edufunds.org

# Check API subdomain
dig api.edufunds.org

# Check from multiple locations
https://dnschecker.org/#A/api.edufunds.org
```

**Expected Results:**
- `edufunds.org` → Points to Cloudflare Pages (multiple IPs)
- `api.edufunds.org` → Points to `130.61.76.199` (via Cloudflare proxy)

---

## Troubleshooting

### Issue: Domain not in Cloudflare account

**Solution:** Add domain to Cloudflare first
1. Go to https://dash.cloudflare.com
2. Click "Add a Site"
3. Enter "edufunds.org"
4. Select Free plan
5. Update nameservers at your domain registrar:
   - Point to Cloudflare's nameservers (provided in setup)
   - Wait 24-48 hours for nameserver propagation

### Issue: SSL certificate error

**Solution:**
- Wait 15 minutes for SSL provisioning
- Check SSL/TLS mode is set to "Flexible"
- Verify domain is in "Active" status in Cloudflare

### Issue: API returns 522 error

**Solution:**
```bash
# Check backend is running
ssh -i ~/.ssh/be-api-direct opc@130.61.76.199 "sudo systemctl status foerder-api"

# Restart if needed
ssh -i ~/.ssh/be-api-direct opc@130.61.76.199 "sudo systemctl restart foerder-api"
```

### Issue: Frontend shows 404

**Solution:**
- Check custom domain was added correctly in Pages
- Verify DNS CNAME record points to edufunds.pages.dev
- Clear browser cache

---

## Quick Reference

### Your Deployment URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend (Temp) | https://68fd435a.edufunds.pages.dev | ✅ Active |
| Frontend (Prod) | https://edufunds.org | ⏳ Pending DNS |
| API | https://api.edufunds.org/api/v1 | ⏳ Pending DNS |
| Backend (Direct) | http://130.61.76.199:8009/api/v1 | ✅ Active |

### Backend IP Address
```
130.61.76.199:8009
```

### Cloudflare Account
```
Account ID: a867271c1fc772b3fbd26f1c347892ff
Email: dieter.meier82@gmail.com
```

---

## Alternative: Automated Script

Run this script for guided setup:
```bash
cd "/Users/winzendwyers/Papa Projekt"
./setup-dns-cloudflare.sh
```

This script will:
- Open Cloudflare dashboard automatically
- Provide step-by-step instructions
- Test configuration after setup

---

## After DNS is Configured

Once DNS is working:

1. **Test complete flow:**
   - Visit https://edufunds.org
   - Login with demo credentials
   - Browse funding opportunities
   - Test AI draft generation (if ChromaDB configured)

2. **Update documentation:**
   - Add actual domain to project README
   - Update API documentation
   - Share login credentials with team

3. **Enable monitoring:**
   - Set up Cloudflare Analytics
   - Configure uptime monitoring
   - Set up error tracking

4. **Optional enhancements:**
   - Switch to Oracle database: `USE_SQLITE=false`
   - Add backend SSL certificate
   - Configure Cloudflare rate limiting
   - Enable Cloudflare WAF rules

---

## Success Checklist

- [ ] Custom domain added to Cloudflare Pages
- [ ] DNS A record created for api.edufunds.org
- [ ] SSL/TLS set to Flexible mode
- [ ] DNS propagation complete (check with dig)
- [ ] Frontend accessible at https://edufunds.org
- [ ] API health check working at https://api.edufunds.org/api/v1/health
- [ ] Login functionality working
- [ ] Funding list displaying correctly

---

## Support

If you encounter issues:

1. Check PRODUCTION-DEPLOYMENT-STATUS.md
2. Check CLOUDFLARE-SETUP-INSTRUCTIONS.md
3. View backend logs:
   ```bash
   ssh -i ~/.ssh/be-api-direct opc@130.61.76.199 "sudo journalctl -u foerder-api -f"
   ```

---

**Configuration Time:** ~10 minutes
**DNS Propagation:** 5-60 minutes
**Total Time to Live:** ~15-70 minutes

🎉 Once complete, your application will be fully accessible at **https://edufunds.org**!
