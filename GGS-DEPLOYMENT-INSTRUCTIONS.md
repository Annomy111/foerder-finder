# GGS Sandstraße - Production Deployment Anleitung

## Status

✅ **Lokal erfolgreich getestet**
- Admin Endpoint funktioniert lokal
- GGS Sandstraße kann via API erstellt werden
- Login funktioniert mit passlib-kompatiblen Hashes

✅ **Code gepusht** (Git commit 6b8ade4)
- `backend/api/routers/admin.py` - Neuer Admin Router
- `backend/api/main.py` - Admin Router registriert

⏳ **Warte auf Production Deployment**

---

## Option 1: SSH Deployment (empfohlen)

### 1.1 SSH-Zugriff einrichten

Falls SSH blockiert ist, muss Port 22 in der OCI Security List freigegeben werden:

```bash
# OCI Console → Networking → Virtual Cloud Networks → BerlinerEnsemble-VCN
# → Security Lists → Default Security List
# → Add Ingress Rule:
#   - Source CIDR: YOUR_IP/32 (oder 0.0.0.0/0 temporär)
#   - Destination Port: 22
#   - IP Protocol: TCP
```

### 1.2 Production Deployment

```bash
# 1. SSH auf Production Server
ssh -i ~/.ssh/be-api-direct opc@130.61.76.199

# 2. Navigiere zum Backend Directory
cd /opt/foerder-finder-backend

# 3. Pull neuen Code
git pull origin main

# 4. Setze Admin Secret Token (falls noch nicht gesetzt)
echo "ADMIN_SECRET_TOKEN=ggs-deploy-production-2025" >> .env

# 5. Restart API Service
sudo systemctl restart foerder-api
# ODER falls gunicorn/uvicorn manuell läuft:
# pkill -f "uvicorn.*foerder"
# USE_SQLITE=true python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8009 &

# 6. Verify API is running
curl http://localhost:8009/api/v1/health

# 7. Test Admin Endpoint
curl -X GET http://localhost:8009/api/v1/admin/health \
  -H "X-Admin-Token: ggs-deploy-production-2025"
```

---

## Option 2: OCI Console Serial Connection (falls SSH nicht möglich)

```bash
# 1. OCI Console → Compute → Instances → BE-API-Server
# 2. Click "Console Connection" → Create Local Connection
# 3. Follow instructions to connect via SSH tunnel
# 4. Execute same commands as in Option 1.2
```

---

## Schritt 3: GGS Sandstraße via API erstellen

Nach erfolgreichem Deployment:

```bash
# Von deinem lokalen Mac aus:
python3 << 'ENDPYTHON'
import requests
import json

# Admin Token (aus Production .env)
admin_token = "ggs-deploy-production-2025"

# GGS Sandstraße Daten
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

# API Call
response = requests.post(
    'https://api.edufunds.org/api/v1/admin/seed-school',
    headers={
        'X-Admin-Token': admin_token,
        'Content-Type': 'application/json'
    },
    json=school_data
)

print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if response.status_code == 200:
    print("\n✅ GGS Sandstraße erfolgreich angelegt!")
    print("\n🔐 Login Credentials:")
    print("   URL: https://edufunds.org/login")
    print("   Email: admin@ggs-sandstrasse.de")
    print("   Passwort: GGS2025!Admin")
else:
    print(f"\n❌ Fehler beim Anlegen der Schule")
ENDPYTHON
```

---

## Schritt 4: Production Login testen

```bash
# Test Login via API
python3 << 'ENDPYTHON'
import requests

response = requests.post(
    'https://api.edufunds.org/api/v1/auth/login',
    json={
        'email': 'admin@ggs-sandstrasse.de',
        'password': 'GGS2025!Admin'
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ LOGIN SUCCESS!")
    print(f"Role: {data['role']}")
    print(f"School ID: {data['school_id'][:8]}...")
    print(f"Token: {data['access_token'][:40]}...")
else:
    print(f"❌ LOGIN FAILED: {response.status_code}")
    print(response.text)
ENDPYTHON
```

Oder teste direkt im Browser:
1. Öffne https://edufunds.org/login
2. Email: `admin@ggs-sandstrasse.de`
3. Passwort: `GGS2025!Admin`

---

## Troubleshooting

### Problem: Admin Endpoint gibt 404
**Lösung**: Code noch nicht auf Production deployed
```bash
# Auf Production Server:
cd /opt/foerder-finder-backend && git pull && sudo systemctl restart foerder-api
```

### Problem: Admin Endpoint gibt 401 (Unauthorized)
**Lösung**: Admin Token falsch oder nicht gesetzt
```bash
# Auf Production Server:
grep ADMIN_SECRET_TOKEN /opt/foerder-finder-backend/.env
# Falls leer:
echo "ADMIN_SECRET_TOKEN=ggs-deploy-production-2025" >> /opt/foerder-finder-backend/.env
sudo systemctl restart foerder-api
```

### Problem: School exists (409 Conflict)
**Lösung**: Schule existiert bereits
```bash
# Option A: Direkt einloggen
# Option B: Schule löschen und neu anlegen (nur für Tests!)
# sqlite3 /opt/foerder-finder-backend/dev_database.db
# "DELETE FROM USERS WHERE email = 'admin@ggs-sandstrasse.de';"
# "DELETE FROM SCHOOLS WHERE name LIKE '%Sandstraße%';"
```

---

## Zusammenfassung der Credentials

Nach erfolgreichem Deployment:

**Production Login:**
- URL: https://edufunds.org/login
- Email: `admin@ggs-sandstrasse.de`
- Passwort: `GGS2025!Admin`
- Rolle: Admin
- Schule: Gemeinschaftsgrundschule Sandstraße, Duisburg

**Test Account (bereits vorhanden):**
- Email: `admin@gs-musterberg.de`
- Passwort: `test1234`

---

## Nächste Schritte

Nach erfolgreichem Login:
1. ✅ Dashboard öffnen
2. ✅ Fördermittel durchsuchen
3. ✅ KI-Antragsgenerator testen
4. ✅ Schuldaten anpassen (Logo, Kontaktdaten)
5. ✅ Weitere Nutzer anlegen (Lehrkräfte)

---

**Deployment-Status**: Code bereit, warte auf SSH-Zugriff oder OCI Console Access
**Erstellt**: $(date +"%Y-%m-%d %H:%M")
