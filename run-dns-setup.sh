#!/bin/bash

# Quick DNS Setup Runner
# This script will prompt you for API token and run the full DNS setup

echo "========================================="
echo "Cloudflare DNS Setup via CLI"
echo "========================================="
echo ""
echo "I've opened the Cloudflare API token page in your browser."
echo ""
echo "Please follow these steps:"
echo ""
echo "1. Click 'Create Token' button"
echo "2. Use template: 'Edit zone DNS'"
echo "3. OR create custom token with permissions:"
echo "   - Zone > DNS > Edit"
echo "   - Zone > Zone Settings > Edit"
echo "   - Account > Cloudflare Pages > Edit"
echo "4. Click 'Continue to summary'"
echo "5. Click 'Create Token'"
echo "6. Copy the token (you'll only see it once!)"
echo ""
read -p "Press ENTER when you've copied the token..."
echo ""
read -sp "Paste your Cloudflare API token here: " CLOUDFLARE_API_TOKEN
echo ""
echo ""

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Export token
export CLOUDFLARE_API_TOKEN

# Save for future use
echo "export CLOUDFLARE_API_TOKEN='$CLOUDFLARE_API_TOKEN'" > ~/.cloudflare_token
chmod 600 ~/.cloudflare_token
echo "✅ Token saved to ~/.cloudflare_token (for future use)"
echo ""

# Run the setup script
echo "Running DNS automation..."
echo ""
/tmp/cloudflare_dns_setup.sh
