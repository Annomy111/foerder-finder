# API Token mit vollen Permissions erstellen

## Warum brauchst du das?

Dein aktuelles Token kann **nur DNS** bearbeiten. Um SSL/TLS und Pages Custom Domains via CLI zu konfigurieren, brauchen wir ein Token mit mehr Rechten.

---

## Schritt 1: Token erstellen (2 Minuten)

1. **Öffne:** https://dash.cloudflare.com/profile/api-tokens

2. **Klicke:** "Create Token"

3. **Wähle:** "Create Custom Token"

4. **Setze folgende Permissions:**

   | Permission | Zone/Account | Access |
   |------------|--------------|--------|
   | Zone → Zone Settings | Specific Zone: `edufunds.org` | Edit |
   | Zone → DNS | Specific Zone: `edufunds.org` | Edit |
   | Account → Cloudflare Pages | Specific Account | Edit |

5. **Continue to summary** → **Create Token**

6. **Kopiere den Token** (z.B. `xYzAbC123...`)

---

## Schritt 2: Token in Terminal setzen

```bash
export CF_FULL_TOKEN="DEIN_TOKEN_HIER"
```

---

## Schritt 3: CLI-Script ausführen

Dann kann ich automatisch:

```bash
# SSL/TLS auf Flexible setzen
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/0641cb79c8ff2b1d3ff8e99b3be39533/settings/ssl" \
  -H "Authorization: Bearer $CF_FULL_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value":"flexible"}'

# Custom Domain zu Pages hinzufügen
curl -X POST "https://api.cloudflare.com/client/v4/accounts/a867271c1fc772b3fbd26f1c347892ff/pages/projects/edufunds/domains" \
  -H "Authorization: Bearer $CF_FULL_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"name":"edufunds.org"}'
```

---

## Alternative: Manuelle Schritte (1 Minute)

Falls du kein neues Token erstellen möchtest, kannst du die 2 Schritte auch manuell im Dashboard machen:

### 1. SSL/TLS
- https://dash.cloudflare.com/0641cb79c8ff2b1d3ff8e99b3be39533/ssl-tls
- Dropdown → "Flexible"

### 2. Custom Domain
- https://dash.cloudflare.com/a867271c1fc772b3fbd26f1c347892ff/pages/view/edufunds
- "Custom domains" → "Set up a custom domain" → `edufunds.org`

---

**Beide Wege funktionieren!** CLI ist nur schneller, wenn du das Token hast.
