#!/bin/bash

# Cloudflare DNS Setup Script for edufunds.org
# This script opens the Cloudflare dashboard and provides step-by-step guidance

set -e

echo "========================================="
echo "Cloudflare DNS Setup for edufunds.org"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Add custom domain to Pages
echo -e "${BLUE}Step 1: Add Custom Domain to Cloudflare Pages${NC}"
echo "Opening Cloudflare Pages dashboard..."
echo ""
sleep 2
open "https://dash.cloudflare.com/$(npx wrangler whoami 2>/dev/null | grep 'Account ID' | awk '{print $4}')/pages/view/edufunds"

echo -e "${YELLOW}Please complete these steps in your browser:${NC}"
echo "1. Click on 'Custom domains' tab"
echo "2. Click 'Set up a custom domain' button"
echo "3. Enter: edufunds.org"
echo "4. Click 'Continue'"
echo "5. Cloudflare will automatically configure DNS and SSL"
echo ""
echo -e "${GREEN}✓ This will activate: https://edufunds.org${NC}"
echo ""
read -p "Press ENTER when you've completed Step 1..."

# Step 2: Check if edufunds.org is in Cloudflare
echo ""
echo -e "${BLUE}Step 2: Configure API Subdomain${NC}"
echo "Opening Cloudflare DNS settings..."
echo ""
sleep 2

# Try to detect if edufunds.org is already in Cloudflare
echo "Checking for edufunds.org in your Cloudflare account..."
ACCOUNT_ID=$(npx wrangler whoami 2>/dev/null | grep 'Account ID' | awk '{print $4}' | tr -d '│')

if [ ! -z "$ACCOUNT_ID" ]; then
    # Open Cloudflare dashboard
    open "https://dash.cloudflare.com/$ACCOUNT_ID"
    echo ""
    echo -e "${YELLOW}Please complete these steps:${NC}"
    echo "1. Find and click on 'edufunds.org' domain"
    echo "2. Click 'DNS' in the sidebar"
    echo "3. Click 'Add record' button"
    echo "4. Configure the A record:"
    echo "   - Type: A"
    echo "   - Name: api"
    echo "   - IPv4 address: 130.61.76.199"
    echo "   - Proxy status: ☁️ Proxied (orange cloud ON)"
    echo "   - TTL: Auto"
    echo "5. Click 'Save'"
    echo ""
    echo -e "${GREEN}✓ This will activate: https://api.edufunds.org${NC}"
else
    echo "Could not detect Account ID. Please add DNS record manually:"
    echo "https://dash.cloudflare.com"
fi

echo ""
read -p "Press ENTER when you've added the API DNS record..."

# Step 3: Optional - Add www redirect
echo ""
echo -e "${BLUE}Step 3 (Optional): Add www Redirect${NC}"
echo ""
echo -e "${YELLOW}If you want www.edufunds.org to redirect:${NC}"
echo "1. In the same DNS settings, click 'Add record' again"
echo "2. Configure CNAME record:"
echo "   - Type: CNAME"
echo "   - Name: www"
echo "   - Target: edufunds.org"
echo "   - Proxy status: ☁️ Proxied"
echo "3. Click 'Save'"
echo ""
read -p "Press ENTER to continue (or skip this step)..."

# Step 4: Verify configuration
echo ""
echo "========================================="
echo "DNS Configuration Summary"
echo "========================================="
echo ""
echo -e "${GREEN}✓ Frontend:${NC} https://edufunds.org"
echo -e "${GREEN}✓ API:${NC} https://api.edufunds.org/api/v1"
echo -e "${GREEN}✓ Temporary URL:${NC} https://68fd435a.edufunds.pages.dev"
echo ""
echo "DNS propagation typically takes 5-60 minutes."
echo ""
echo "========================================="
echo "Testing Current Status"
echo "========================================="
echo ""

# Test temporary URL
echo "Testing temporary URL..."
if curl -s https://68fd435a.edufunds.pages.dev > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Temporary URL is working${NC}"
else
    echo -e "${YELLOW}⚠ Temporary URL not responding${NC}"
fi

# Test backend API
echo "Testing backend API..."
if curl -s http://130.61.76.199:8009/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend API not responding${NC}"
fi

echo ""
echo "========================================="
echo "What to Test After DNS Propagates"
echo "========================================="
echo ""
echo "1. Frontend: https://edufunds.org"
echo "   - Should show the login page"
echo "   - Login with: admin@gs-musterberg.de / admin123"
echo ""
echo "2. API Health: https://api.edufunds.org/api/v1/health"
echo "   - Should return: {\"status\": \"healthy\"}"
echo ""
echo "3. Check SSL:"
echo "   - Both URLs should have valid SSL certificates"
echo "   - Cloudflare handles this automatically"
echo ""
echo -e "${GREEN}Setup Complete!${NC}"
echo ""
echo "To check DNS propagation status:"
echo "  dig edufunds.org"
echo "  dig api.edufunds.org"
echo ""
echo "For troubleshooting, check:"
echo "  - CLOUDFLARE-SETUP-INSTRUCTIONS.md"
echo "  - PRODUCTION-DEPLOYMENT-STATUS.md"
echo ""
