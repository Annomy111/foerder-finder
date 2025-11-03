# Quick Start: 2 Manual Steps to Complete Deployment

**Time Required:** 2 minutes
**Difficulty:** Easy (point-and-click)

---

## 🎯 Overview

Your Förder-Finder app is **fully deployed and functional**, but needs 2 quick manual configuration steps in the Cloudflare dashboard to enable the production URLs.

**Current Status:**
- ✅ Frontend works at: https://68fd435a.edufunds.pages.dev
- ✅ Backend works locally on server
- ⏳ Production URLs need setup: https://edufunds.org and https://api.edufunds.org

---

## Step 1: Enable API Access (1 minute)

### What This Does
Allows the frontend to communicate with your backend API through `https://api.edufunds.org`

### Instructions

1. **Open Cloudflare SSL/TLS Settings**
   - Click: https://dash.cloudflare.com/0641cb79c8ff2b1d3ff8e99b3be39533/ssl-tls

2. **Change SSL/TLS Encryption Mode**
   - You'll see a dropdown that currently shows "Full" or "Full (Strict)"
   - Click the dropdown
   - Select: **"Flexible"**
   - Wait for the green "Updated" notification

3. **Done!**
   - The API is now accessible at https://api.edufunds.org

### Test It Works
```bash
curl https://api.edufunds.org/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "sqlite (dev)",
  "chromadb": "not configured",
  "mode": "development"
}
```

---

## Step 2: Add Custom Domain (1 minute)

### What This Does
Makes your app accessible at `https://edufunds.org` instead of the temporary Cloudflare URL

### Instructions

1. **Open Cloudflare Pages Project**
   - Click: https://dash.cloudflare.com/a867271c1fc772b3fbd26f1c347892ff/pages/view/edufunds

2. **Add Custom Domain**
   - Click the **"Custom domains"** tab at the top
   - Click the **"Set up a custom domain"** button
   - Enter: `edufunds.org`
   - Click **"Continue"**
   - Cloudflare will show you that it's creating DNS records automatically
   - Click **"Activate domain"** (or similar confirmation button)

3. **Wait for Propagation** (5-10 minutes)
   - Cloudflare will show "Active" status
   - DNS propagation happens in the background

4. **Done!**
   - Your app will be live at https://edufunds.org

### Test It Works (after 5-10 minutes)
```bash
curl -I https://edufunds.org
```

**Expected Response:**
```
HTTP/2 200
```

---

## 🎉 You're Done!

After completing these 2 steps, your application will be fully operational at:

- **Frontend**: https://edufunds.org
- **API**: https://api.edufunds.org/api/v1

### Login Credentials
- **Email**: admin@gs-musterberg.de
- **Password**: test1234

---

## 🔍 Troubleshooting

### Issue: "Flexible SSL" option is grayed out
**Solution:** Make sure you're on the "Overview" tab under SSL/TLS settings. The option should be in a dropdown at the top.

### Issue: "Domain already exists" when adding custom domain
**Solution:** The domain is already added! Just verify it's showing as "Active" in the Custom domains tab.

### Issue: https://edufunds.org shows 404 after 10 minutes
**Solution:**
1. Check DNS is resolving: `dig edufunds.org +short`
2. Should show Cloudflare IPs like 104.21.x.x
3. If not, wait another 5-10 minutes for global DNS propagation

### Issue: https://api.edufunds.org still shows "Not Found"
**Solution:**
1. Double-check SSL/TLS mode is set to "Flexible" (not "Full")
2. Wait 1-2 minutes for the setting to propagate
3. Try in a private/incognito browser window (clears cache)

---

## 📞 Need Help?

All deployment details and troubleshooting info are in:
- `DEPLOYMENT-STATUS-FINAL.md` - Complete deployment documentation
- `SYSTEM-TEST-REPORT.md` - Detailed test results
- `DNS-SETUP-COMPLETE.md` - DNS configuration details

---

**Created:** 2025-10-27 02:26 UTC
**Status:** 2 manual steps required to complete deployment
