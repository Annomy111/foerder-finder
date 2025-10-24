#!/bin/bash

# ============================================================================
# Frontend Deployment Script für Cloudflare Pages
# Deployed React App auf Cloudflare
# ============================================================================

set -e  # Exit on error

echo "=== Förder-Finder Frontend Deployment ==="
echo ""

# Konfiguration
PROJECT_NAME="foerder-finder"
CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-}"  # Aus ENV oder leer

cd ../frontend

echo "[1/4] Installiere Dependencies..."
npm install

echo ""
echo "[2/4] Build Frontend..."
VITE_API_URL="https://api.foerder-finder.de" npm run build

echo ""
echo "[3/4] Deploye zu Cloudflare Pages..."
if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
  # Interaktive Authentifizierung
  npx wrangler pages deploy dist --project-name "$PROJECT_NAME" --branch main
else
  # Mit Account ID (für CI/CD)
  npx wrangler pages deploy dist \
    --project-name "$PROJECT_NAME" \
    --branch main \
    --account-id "$CLOUDFLARE_ACCOUNT_ID"
fi

echo ""
echo "[4/4] Deployment abgeschlossen!"
echo "Frontend erreichbar unter: https://$PROJECT_NAME.pages.dev"
echo "Oder: https://app.foerder-finder.de (nach DNS-Setup)"
