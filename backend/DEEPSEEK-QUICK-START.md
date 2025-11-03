# DeepSeek API - Quick Start Guide

Get AI-powered draft generation working in 3 minutes.

---

## Step 1: Get Your API Key

1. Go to: https://platform.deepseek.com/
2. Sign up / Log in
3. Navigate to **API Keys**
4. Click **Create API Key**
5. Copy the key (starts with `sk-...`)

---

## Step 2: Configure Environment

**Local Development**:
```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export DEEPSEEK_API_KEY=sk-your-key-here

# Or create backend/.env file
echo "DEEPSEEK_API_KEY=sk-your-key-here" >> backend/.env
```

**Production (OCI VM)**:
```bash
# SSH into VM
ssh opc@130.61.76.199

# Edit environment
sudo nano /opt/foerder-finder-backend/.env

# Add line:
DEEPSEEK_API_KEY=sk-your-key-here

# Restart service
sudo systemctl restart foerder-api
```

---

## Step 3: Test Integration

```bash
cd backend
python3 test_deepseek_integration.py
```

**Expected Output**:
```
✅ Real API call successful!
   Length: 7730 characters
```

---

## Verify in Application

1. Start backend: `uvicorn main:app --reload`
2. Login to frontend
3. Create new application
4. Click "Generate Draft"
5. Check response: `"model_used": "deepseek-chat"` ✅

---

## Cost Monitoring

**Current Usage**: Check at https://platform.deepseek.com/usage

**Estimated Costs**:
- 10 drafts/day = ~$0.15/day = $4.50/month
- 100 drafts/day = ~$1.50/day = $45/month
- 1000 drafts/day = ~$15/day = $450/month

**Budget Alert**: Set up at platform dashboard

---

## Troubleshooting

### "API key not configured" warning

**Problem**: API key not found
**Solution**:
```bash
export DEEPSEEK_API_KEY=sk-your-key-here
# Restart backend
```

### "API call failed" error

**Problem**: Network or rate limit
**Solution**: Check logs:
```bash
tail -f /var/log/foerder-api.log | grep DeepSeek
```

**Fallback**: System automatically uses mock generator

### Drafts seem generic

**Problem**: Using mock fallback
**Solution**: Verify API key is set correctly
```bash
echo $DEEPSEEK_API_KEY
# Should output: sk-...
```

---

## Advanced Configuration

### Adjust Temperature (Creativity)

```bash
# backend/.env
DEEPSEEK_TEMPERATURE=0.5  # More conservative (default: 0.7)
DEEPSEEK_TEMPERATURE=0.9  # More creative
```

### Increase Max Tokens (Longer Drafts)

```bash
# backend/.env
DEEPSEEK_MAX_TOKENS=8192  # Very detailed (default: 4096)
```

### Change Model

```bash
# backend/.env
DEEPSEEK_MODEL=deepseek-chat  # Default
DEEPSEEK_MODEL=deepseek-coder  # If they offer alternative models
```

---

## Support

- **API Docs**: https://platform.deepseek.com/docs
- **Status**: https://status.deepseek.com/
- **Support**: support@deepseek.com

---

**That's it!** You now have AI-powered funding application generation. 🎉
