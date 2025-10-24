#!/bin/bash

# ============================================================================
# Backend Deployment Script für OCI VM
# Deployed FastAPI, Scraper und RAG Indexer auf Oracle Cloud
# ============================================================================

set -e  # Exit on error

echo "=== Förder-Finder Backend Deployment ==="
echo ""

# Konfiguration
OCI_VM_IP="130.61.76.199"
OCI_VM_USER="opc"
SSH_KEY="~/.ssh/be-api-direct"
REMOTE_DIR="/opt/foerder-finder-backend"

echo "[1/5] Teste SSH-Verbindung..."
ssh -i "$SSH_KEY" "$OCI_VM_USER@$OCI_VM_IP" "echo 'SSH OK'"

echo ""
echo "[2/5] Erstelle Remote-Verzeichnis..."
ssh -i "$SSH_KEY" "$OCI_VM_USER@$OCI_VM_IP" "sudo mkdir -p $REMOTE_DIR && sudo chown $OCI_VM_USER:$OCI_VM_USER $REMOTE_DIR"

echo ""
echo "[3/5] Kopiere Backend-Code..."
rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' \
  -e "ssh -i $SSH_KEY" \
  ../backend/ "$OCI_VM_USER@$OCI_VM_IP:$REMOTE_DIR/"

echo ""
echo "[4/5] Installiere Dependencies..."
ssh -i "$SSH_KEY" "$OCI_VM_USER@$OCI_VM_IP" << 'EOF'
cd /opt/foerder-finder-backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

echo ""
echo "[5/5] Starte Services..."
ssh -i "$SSH_KEY" "$OCI_VM_USER@$OCI_VM_IP" << 'EOF'
# Erstelle systemd Service-Files (wenn noch nicht vorhanden)
sudo cp /opt/foerder-finder-backend/../deployment/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Starte Services
sudo systemctl restart foerder-api
sudo systemctl restart foerder-scraper.timer
sudo systemctl restart foerder-indexer.timer

# Status
sudo systemctl status foerder-api --no-pager
EOF

echo ""
echo "=== Deployment abgeschlossen ==="
echo "API erreichbar unter: http://$OCI_VM_IP:8000"
