# Cloudflare Setup Instructions for edufunds.org

## Current Deployment Status

✅ **Frontend**: Deployed to Cloudflare Pages
- Project: `edufunds`
- Temporary URL: https://68fd435a.edufunds.pages.dev
- Production URL (to configure): https://edufunds.org

✅ **Backend**: Running on OCI VM
- Server: 130.61.76.199:8009
- Backend is using SQLite (development mode)
- CORS already configured for edufunds.org

## Step 1: Add edufunds.org as Custom Domain to Pages

### Via Cloudflare Dashboard:

1. Go to https://dash.cloudflare.com
2. Navigate to **Workers & Pages** > **Pages**
3. Click on **edufunds** project
4. Go to **Custom domains** tab
5. Click **Set up a custom domain**
6. Enter: `edufunds.org`
7. Also add: `www.edufunds.org` (optional)
8. Click **Continue** and follow the prompts

Cloudflare will automatically:
- Create the necessary DNS records
- Provision SSL/TLS certificates
- Configure the domain

## Step 2: Configure API Subdomain (api.edufunds.org)

You need to point `api.edufunds.org` to your backend server.

### Via Cloudflare Dashboard:

1. Go to https://dash.cloudflare.com
2. Select **edufunds.org** domain
3. Go to **DNS** > **Records**
4. Click **Add record**
5. Configure:
   - **Type**: `A`
   - **Name**: `api`
   - **IPv4 address**: `130.61.76.199`
   - **Proxy status**: ☁️ Proxied (ORANGE CLOUD) - This gives you DDoS protection, caching, and HTTPS
   - **TTL**: Auto
6. Click **Save**

## Step 3: Configure SSL/TLS Settings

1. In Cloudflare Dashboard, go to **SSL/TLS** tab
2. Set **SSL/TLS encryption mode** to:
   - **Flexible** (if backend doesn't have SSL)
   - **Full** (if backend has self-signed cert)
   - **Full (Strict)** (if backend has valid cert) ← Recommended for production

Currently, your backend doesn't have HTTPS, so use **Flexible** for now.

## Step 4: Configure Firewall Rules (Optional but Recommended)

To protect your API from abuse:

1. Go to **Security** > **WAF** > **Rate limiting rules**
2. Add rules:
   - **Login endpoint**: 10 requests per minute from single IP
   - **API endpoints**: 60 requests per minute from single IP
   - **AI generation**: 5 requests per minute from single IP

## Step 5: Verify Deployment

After DNS propagation (can take 5-60 minutes):

1. Test frontend: https://edufunds.org
2. Test API: https://api.edufunds.org/api/v1/health
3. Test login functionality
4. Test funding list and AI generation

## Troubleshooting

### Frontend shows 404
- Wait for DNS propagation (check with `nslookup edufunds.org`)
- Verify custom domain is properly added in Pages project

### API not accessible
- Check DNS record for `api.edufunds.org`
- Verify backend is running: `curl http://130.61.76.199:8009/api/v1/health`
- Check Cloudflare proxy status (should be orange cloud)

### CORS errors
- Backend CORS is already configured for edufunds.org
- If issues persist, check backend logs on server

## Alternative: Quick Test with Temporary URL

While waiting for DNS:
1. Visit: https://68fd435a.edufunds.pages.dev
2. This will try to connect to https://api.edufunds.org
3. API won't work until DNS is configured

## Production Checklist

Before going live:
- [ ] Custom domain added to Pages project (edufunds.org)
- [ ] DNS A record created (api.edufunds.org → 130.61.76.199)
- [ ] SSL/TLS mode configured
- [ ] Test all functionality
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerts
- [ ] Update backend to use Oracle Database (currently using SQLite)

## Commands Reference

### Deploy new version:
```bash
cd /Users/winzendwyers/Papa Projekt/frontend
npm run build
npx wrangler pages deploy dist --project-name edufunds --branch main
```

### Check deployment status:
```bash
npx wrangler pages deployment list --project-name edufunds
```

### View Pages projects:
```bash
npx wrangler pages project list
```
