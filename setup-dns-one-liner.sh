#!/bin/bash
# One-line DNS setup for edufunds.org
# Usage: CLOUDFLARE_API_TOKEN="your_token" ./setup-dns-one-liner.sh

set -e

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo ""
    echo "❌ No API token found!"
    echo ""
    echo "Create a token at: https://dash.cloudflare.com/profile/api-tokens"
    echo "Then run:"
    echo ""
    echo "  CLOUDFLARE_API_TOKEN='your_token_here' ./setup-dns-one-liner.sh"
    echo ""
    exit 1
fi

ACCOUNT_ID="a867271c1fc772b3fbd26f1c347892ff"
DOMAIN="edufunds.org"

echo "🔍 Finding edufunds.org zone..."
ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" | jq -r '.result[0].id // empty')

if [ -z "$ZONE_ID" ]; then
    echo "❌ Domain not found in Cloudflare. Add it first at: https://dash.cloudflare.com"
    exit 1
fi

echo "✅ Zone found: $ZONE_ID"
echo ""
echo "🌐 Creating DNS records..."

# Create api.edufunds.org A record
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"api","content":"130.61.76.199","ttl":1,"proxied":true}' | \
  jq -r 'if .success then "✅ DNS: api.edufunds.org → 130.61.76.199" else "⚠️  " + .errors[0].message end'

# Set SSL to Flexible
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/ssl" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value":"flexible"}' | \
  jq -r 'if .success then "✅ SSL: Flexible mode enabled" else "⚠️  SSL already configured" end'

# Add custom domain to Pages
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects/edufunds/domains" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{\"name\":\"$DOMAIN\"}" | \
  jq -r 'if .success then "✅ Pages: edufunds.org added" else "⚠️  " + (.errors[0].message // "Domain may already exist") end'

echo ""
echo "✅ DNS setup complete!"
echo ""
echo "Test URLs (after DNS propagation 5-60min):"
echo "  • https://edufunds.org"
echo "  • https://api.edufunds.org/api/v1/health"
