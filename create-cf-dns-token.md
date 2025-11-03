# Cloudflare API Token für Let's Encrypt erstellen

## Quick Link
https://dash.cloudflare.com/profile/api-tokens

## Schritte

1. **Klicke "Create Token"**

2. **Wähle Template: "Edit zone DNS"** (auf der rechten Seite)

3. **Konfiguration**:
   - Permissions: `Zone` → `DNS` → `Edit`
   - Zone Resources: `Include` → `Specific zone` → `edufunds.org`
   - (Optional) IP Address Filtering: Leer lassen
   - (Optional) TTL: Leer lassen (kein Ablaufdatum)

4. **"Continue to summary"** → **"Create Token"**

5. **Token kopieren** (wird nur EINMAL angezeigt!)

## Token Format
Der Token sieht aus wie: `AbCdEf1234567890_-AbCdEf1234567890`

## Was ich damit mache
- Setze temporär einen TXT-Record für `_acme-challenge.api.edufunds.org`
- Let's Encrypt prüft den DNS-Record
- Zertifikat wird ausgestellt
- TXT-Record wird automatisch gelöscht

## Sicherheit
- Token wird NUR lokal auf der OCI VM gespeichert
- Nur für DNS-Einträge von edufunds.org
- Kann jederzeit in Cloudflare gelöscht werden

## Nächster Schritt
Wenn du den Token hast, gib mir ein Zeichen und ich konfiguriere alles automatisch.
