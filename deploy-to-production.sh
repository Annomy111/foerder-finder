#!/bin/bash
#
# EduFunds Production Deployment Script
# Deployt neuen Code + erstellt GGS Sandstraße
#

set -e

echo "=================================="
echo "EDUFUNDS PRODUCTION DEPLOYMENT"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_SERVER="130.61.76.199"  # api.edufunds.org
SSH_KEY="$HOME/.ssh/be-api-direct"
BACKEND_PATH="/opt/foerder-finder-backend"
ADMIN_TOKEN="ggs-deploy-production-2025"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ SSH Key nicht gefunden: $SSH_KEY${NC}"
    echo "Bitte korrekten SSH Key angeben"
    exit 1
fi

echo -e "${YELLOW}📡 Teste Verbindung zu Production Server...${NC}"
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 opc@$PRODUCTION_SERVER "echo OK" > /dev/null 2>&1; then
    echo -e "${RED}❌ SSH-Verbindung fehlgeschlagen${NC}"
    echo ""
    echo "Mögliche Lösungen:"
    echo "1. SSH Port in OCI Security List freischalten"
    echo "2. Korrekten SSH Key verwenden"
    echo "3. Via OCI Console auf den Server zugreifen"
    echo ""
    echo "Nutze stattdessen: admin-deploy-tool.html"
    exit 1
fi

echo -e "${GREEN}✅ SSH-Verbindung erfolgreich${NC}"
echo ""

# Step 1: Pull Code
echo -e "${YELLOW}📥 Step 1/4: Pull neuen Code...${NC}"
ssh -i "$SSH_KEY" opc@$PRODUCTION_SERVER "cd $BACKEND_PATH && git pull origin main"
echo -e "${GREEN}✅ Code aktualisiert${NC}"
echo ""

# Step 2: Set Admin Token
echo -e "${YELLOW}🔑 Step 2/4: Setze Admin Token...${NC}"
ssh -i "$SSH_KEY" opc@$PRODUCTION_SERVER "grep -q ADMIN_SECRET_TOKEN $BACKEND_PATH/.env || echo 'ADMIN_SECRET_TOKEN=$ADMIN_TOKEN' >> $BACKEND_PATH/.env"
echo -e "${GREEN}✅ Admin Token gesetzt${NC}"
echo ""

# Step 3: Restart API
echo -e "${YELLOW}🔄 Step 3/4: Restart API Service...${NC}"
ssh -i "$SSH_KEY" opc@$PRODUCTION_SERVER "sudo systemctl restart foerder-api 2>/dev/null || (pkill -f 'uvicorn.*foerder' && sleep 2 && cd $BACKEND_PATH && nohup python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8009 > /tmp/api.log 2>&1 &)"
sleep 5
echo -e "${GREEN}✅ API neu gestartet${NC}"
echo ""

# Step 4: Verify Deployment
echo -e "${YELLOW}🔍 Step 4/4: Verify Deployment...${NC}"
API_HEALTH=$(curl -s https://api.edufunds.org/api/v1/health | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "error")

if [ "$API_HEALTH" == "healthy" ]; then
    echo -e "${GREEN}✅ API ist online${NC}"
else
    echo -e "${RED}❌ API antwortet nicht korrekt${NC}"
    exit 1
fi

# Check if Admin Endpoint exists
ADMIN_CHECK=$(curl -s -X GET https://api.edufunds.org/api/v1/admin/health -H "X-Admin-Token: $ADMIN_TOKEN" -w "%{http_code}" -o /dev/null)

if [ "$ADMIN_CHECK" == "200" ]; then
    echo -e "${GREEN}✅ Admin Endpoint verfügbar${NC}"
else
    echo -e "${RED}❌ Admin Endpoint nicht verfügbar (HTTP $ADMIN_CHECK)${NC}"
    echo "Möglicherweise muss die API noch neu gestartet werden"
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ DEPLOYMENT ERFOLGREICH${NC}"
echo "=================================="
echo ""

# Step 5: Create GGS Sandstraße
echo -e "${YELLOW}🏫 Soll GGS Sandstraße jetzt angelegt werden? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo -e "${YELLOW}📝 Lege GGS Sandstraße an...${NC}"

    python3 << 'ENDPYTHON'
import requests
import json

admin_token = "ggs-deploy-production-2025"

school_data = {
    "name": "Gemeinschaftsgrundschule Sandstraße",
    "address": "Sandstraße 46, Duisburg-Marxloh",
    "city": "Duisburg",
    "postal_code": "47169",
    "state": "Nordrhein-Westfalen",
    "contact_email": "ggs.sandstr@stadt-duisburg.de",
    "contact_phone": "0203-403688",
    "logo_url": "https://www.ggs-sandstrasse.de/wp-content/uploads/2022/04/Logo_mSchrift-e1672838922106.jpg",
    "admin_email": "admin@ggs-sandstrasse.de",
    "admin_password": "GGS2025!Admin",
    "admin_first_name": "Klaus",
    "admin_last_name": "Hagge"
}

response = requests.post(
    'https://api.edufunds.org/api/v1/admin/seed-school',
    headers={
        'X-Admin-Token': admin_token,
        'Content-Type': 'application/json'
    },
    json=school_data
)

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ GGS Sandstraße erfolgreich angelegt!\n")
    print(f"School ID: {result['school_id']}")
    print(f"Admin User ID: {result['admin_user_id']}")
    print(f"\n🔐 Login Credentials:")
    print(f"   URL: https://edufunds.org/login")
    print(f"   Email: admin@ggs-sandstrasse.de")
    print(f"   Passwort: GGS2025!Admin")
elif response.status_code == 409:
    print(f"\n⚠️  Schule existiert bereits")
else:
    print(f"\n❌ Fehler: {response.status_code}")
    print(response.text)
ENDPYTHON

else
    echo ""
    echo "Schule nicht angelegt."
    echo "Nutze später: admin-deploy-tool.html oder Python Script"
fi

echo ""
echo "=================================="
echo "DEPLOYMENT ABGESCHLOSSEN"
echo "=================================="
