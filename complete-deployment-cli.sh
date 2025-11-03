#!/bin/bash
# Complete Deployment Automation für Förder-Finder
# Führt SSL/TLS Config und Custom Domain Setup via CLI durch

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Förder-Finder Deployment - Finale Schritte${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if token is provided
if [ -z "$CF_FULL_TOKEN" ]; then
    echo -e "${RED}❌ Kein API Token gefunden!${NC}"
    echo ""
    echo "Bitte erstelle ein Token mit folgenden Permissions:"
    echo "  - Zone → Zone Settings: Edit"
    echo "  - Zone → DNS: Edit"
    echo "  - Account → Cloudflare Pages: Edit"
    echo ""
    echo "Dann führe aus:"
    echo "  export CF_FULL_TOKEN='dein_token_hier'"
    echo "  ./complete-deployment-cli.sh"
    echo ""
    echo "Oder siehe: CREATE-API-TOKEN-GUIDE.md"
    exit 1
fi

ZONE_ID="0641cb79c8ff2b1d3ff8e99b3be39533"
ACCOUNT_ID="a867271c1fc772b3fbd26f1c347892ff"
PROJECT="edufunds"
DOMAIN="edufunds.org"

echo -e "${YELLOW}🔐 API Token gefunden, starte Konfiguration...${NC}"
echo ""

# Step 1: SSL/TLS auf Flexible setzen
echo -e "${YELLOW}Schritt 1/2: SSL/TLS Modus auf 'Flexible' setzen...${NC}"
SSL_RESPONSE=$(curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/ssl" \
  -H "Authorization: Bearer $CF_FULL_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value":"flexible"}')

SSL_SUCCESS=$(echo $SSL_RESPONSE | jq -r '.success')

if [ "$SSL_SUCCESS" == "true" ]; then
    echo -e "${GREEN}✅ SSL/TLS auf Flexible gesetzt${NC}"
elif echo $SSL_RESPONSE | grep -q "already"; then
    echo -e "${GREEN}✅ SSL/TLS war bereits auf Flexible${NC}"
else
    echo -e "${RED}❌ SSL/TLS Fehler:${NC}"
    echo $SSL_RESPONSE | jq -r '.errors[0].message'
    echo ""
    echo -e "${YELLOW}Versuche trotzdem mit Custom Domain...${NC}"
fi

echo ""

# Step 2: Custom Domain zu Pages hinzufügen
echo -e "${YELLOW}Schritt 2/2: Custom Domain '$DOMAIN' zu Pages hinzufügen...${NC}"
DOMAIN_RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects/$PROJECT/domains" \
  -H "Authorization: Bearer $CF_FULL_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{\"name\":\"$DOMAIN\"}")

DOMAIN_SUCCESS=$(echo $DOMAIN_RESPONSE | jq -r '.success')

if [ "$DOMAIN_SUCCESS" == "true" ]; then
    echo -e "${GREEN}✅ Domain '$DOMAIN' zu Pages hinzugefügt${NC}"
elif echo $DOMAIN_RESPONSE | grep -q "already"; then
    echo -e "${GREEN}✅ Domain war bereits hinzugefügt${NC}"
else
    echo -e "${RED}❌ Domain Fehler:${NC}"
    echo $DOMAIN_RESPONSE | jq -r '.errors[0].message // .errors[0] // "Unbekannter Fehler"'
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Konfiguration abgeschlossen!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}DNS Propagation läuft...${NC}"
echo ""
echo "Deine URLs (in 5-10 Minuten aktiv):"
echo -e "  • Frontend: ${GREEN}https://edufunds.org${NC}"
echo -e "  • API: ${GREEN}https://api.edufunds.org/api/v1${NC}"
echo ""
echo "Test nach 5 Minuten:"
echo "  curl -I https://edufunds.org"
echo "  curl https://api.edufunds.org/api/v1/health"
echo ""
echo "Login Credentials:"
echo "  Email: admin@gs-musterberg.de"
echo "  Password: test1234"
echo ""
