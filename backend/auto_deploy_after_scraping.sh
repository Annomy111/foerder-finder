#!/bin/bash
################################################################################
# AUTO-DEPLOY NACH SCRAPING
# Wartet bis Scraping fertig ist und deployed automatisch auf Production
################################################################################

set -e  # Exit on error

echo "================================================================================"
echo "AUTO-DEPLOY PIPELINE"
echo "================================================================================"
echo ""

# Configuration
BACKEND_DIR="/Users/winzendwyers/Papa Projekt/backend"
PRODUCTION_SERVER="opc@130.61.76.199"
SSH_KEY="$HOME/.ssh/be-api-direct"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Wait for scraping processes to finish
echo -e "${YELLOW}[1/6] Warte auf Scraping-Prozesse...${NC}"
echo ""

# Check for running Python scraping processes
while pgrep -f "import_stiftungen_batch.py\|scrape_more_foundations.py" > /dev/null; do
    echo "⏳ Scraping läuft noch... (prüfe in 30 Sekunden wieder)"
    sleep 30
done

echo -e "${GREEN}✅ Alle Scraping-Prozesse abgeschlossen!${NC}"
echo ""

# Step 2: Show statistics
echo -e "${YELLOW}[2/6] Datenbank-Statistiken (Lokal)${NC}"
cd "$BACKEND_DIR"
sqlite3 dev_database.db <<EOF
.mode column
.headers on
SELECT
    COUNT(*) as total_programs,
    COUNT(CASE WHEN extraction_quality_score > 0 THEN 1 END) as high_quality,
    ROUND(AVG(extraction_quality_score), 2) as avg_quality
FROM FUNDING_OPPORTUNITIES;
EOF
echo ""

# Step 3: Backup Production Database
echo -e "${YELLOW}[3/6] Backup Production Datenbank...${NC}"
BACKUP_NAME="dev_database.db.backup_$(date +%Y%m%d_%H%M%S)"
ssh -i "$SSH_KEY" "$PRODUCTION_SERVER" "cd ~/Papa_Projekt/backend && cp dev_database.db '$BACKUP_NAME'" || {
    echo -e "${RED}❌ Backup fehlgeschlagen!${NC}"
    exit 1
}
echo -e "${GREEN}✅ Backup erstellt: $BACKUP_NAME${NC}"
echo ""

# Step 4: Deploy Database to Production
echo -e "${YELLOW}[4/6] Deploye Datenbank auf Production...${NC}"
scp -i "$SSH_KEY" "$BACKEND_DIR/dev_database.db" "$PRODUCTION_SERVER:~/Papa_Projekt/backend/" || {
    echo -e "${RED}❌ Datenbank-Upload fehlgeschlagen!${NC}"
    exit 1
}
echo -e "${GREEN}✅ Datenbank deployed!${NC}"
echo ""

# Step 5: Re-index ChromaDB on Production
echo -e "${YELLOW}[5/6] ChromaDB neu indexieren (Production)...${NC}"
echo "⏳ Backup alte ChromaDB..."
ssh -i "$SSH_KEY" "$PRODUCTION_SERVER" "cd ~/Papa_Projekt/backend && tar czf chroma_db_dev.backup_$(date +%Y%m%d_%H%M%S).tar.gz chroma_db_dev/ 2>/dev/null || echo 'Kein altes ChromaDB vorhanden'"

echo "⏳ Kopiere neue ChromaDB..."
cd "$BACKEND_DIR"
tar czf /tmp/chroma_db_dev_deploy.tar.gz chroma_db_dev/
scp -i "$SSH_KEY" /tmp/chroma_db_dev_deploy.tar.gz "$PRODUCTION_SERVER:~/Papa_Projekt/backend/" || {
    echo -e "${RED}❌ ChromaDB-Upload fehlgeschlagen!${NC}"
    exit 1
}

ssh -i "$SSH_KEY" "$PRODUCTION_SERVER" "cd ~/Papa_Projekt/backend && tar xzf chroma_db_dev_deploy.tar.gz && rm chroma_db_dev_deploy.tar.gz"
rm /tmp/chroma_db_dev_deploy.tar.gz

echo -e "${GREEN}✅ ChromaDB deployed!${NC}"
echo ""

# Step 6: Verify Production
echo -e "${YELLOW}[6/6] Verifiziere Production Deployment...${NC}"
ssh -i "$SSH_KEY" "$PRODUCTION_SERVER" "cd ~/Papa_Projekt/backend && sqlite3 dev_database.db 'SELECT COUNT(*) as total_programs FROM FUNDING_OPPORTUNITIES; SELECT COUNT(*) as high_quality FROM FUNDING_OPPORTUNITIES WHERE extraction_quality_score > 0;'"
echo ""

# Final Summary
echo "================================================================================"
echo -e "${GREEN}🎉 AUTO-DEPLOY ERFOLGREICH ABGESCHLOSSEN!${NC}"
echo "================================================================================"
echo ""
echo "✅ Datenbank deployed"
echo "✅ ChromaDB deployed"
echo "✅ Production verifiziert"
echo ""
echo "Die Homepage zeigt jetzt die neuen Förderprogramme!"
echo ""
echo "Production Server: http://130.61.76.199:8000"
echo "API Health Check: http://130.61.76.199:8000/api/v1/health"
echo ""
echo "================================================================================"
