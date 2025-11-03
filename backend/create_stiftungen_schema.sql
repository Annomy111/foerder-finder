-- ============================================================================
-- STIFTUNGEN Schema für Förder-Finder
-- Zweck: Integration von Stiftungsdatenbanken (DSZ, Bundesverband, etc.)
-- ============================================================================

-- Haupttabelle für Stiftungen
CREATE TABLE STIFTUNGEN (
    stiftung_id VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    name VARCHAR2(500) NOT NULL,
    website VARCHAR2(500),
    beschreibung CLOB,
    foerderbereiche CLOB,  -- JSON Array: ["Bildung", "MINT", "Integration"]
    foerdersumme_min NUMBER(12,2),
    foerdersumme_max NUMBER(12,2),
    bewerbungsfrist VARCHAR2(100),
    kontakt_email VARCHAR2(200),
    kontakt_telefon VARCHAR2(50),
    kontakt_ansprechpartner VARCHAR2(200),
    bundesland VARCHAR2(100),
    stadt VARCHAR2(200),
    plz VARCHAR2(10),
    zielgruppen CLOB,  -- JSON Array: ["Grundschule", "Sekundarstufe"]
    anforderungen CLOB,  -- JSON Array der Bewerbungsanforderungen
    quelle VARCHAR2(100) NOT NULL,  -- 'DSZ', 'Bundesverband', 'DKJS', etc.
    quelle_url VARCHAR2(500),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active NUMBER(1) DEFAULT 1,
    
    -- Constraints
    CONSTRAINT chk_foerdersumme CHECK (foerdersumme_max >= foerdersumme_min OR foerdersumme_min IS NULL),
    CONSTRAINT chk_is_active CHECK (is_active IN (0, 1))
);

-- Verknüpfung FUNDING_OPPORTUNITIES zu Stiftungen
ALTER TABLE FUNDING_OPPORTUNITIES ADD (
    stiftung_id VARCHAR2(36),
    source_type VARCHAR2(50) DEFAULT 'website',  -- 'website' oder 'stiftung'
    CONSTRAINT fk_funding_stiftung FOREIGN KEY (stiftung_id) 
        REFERENCES STIFTUNGEN(stiftung_id) ON DELETE SET NULL
);

-- Performance-Indizes
CREATE INDEX idx_stiftung_bundesland ON STIFTUNGEN(bundesland);
CREATE INDEX idx_stiftung_quelle ON STIFTUNGEN(quelle);
CREATE INDEX idx_stiftung_active ON STIFTUNGEN(is_active);
CREATE INDEX idx_stiftung_name ON STIFTUNGEN(UPPER(name));
CREATE INDEX idx_funding_stiftung ON FUNDING_OPPORTUNITIES(stiftung_id);

-- Kommentare für Dokumentation
COMMENT ON TABLE STIFTUNGEN IS 'Stiftungsdatenbank für Bildungsförderung';
COMMENT ON COLUMN STIFTUNGEN.foerderbereiche IS 'JSON Array der Förderbereiche';
COMMENT ON COLUMN STIFTUNGEN.zielgruppen IS 'JSON Array der Zielgruppen (Grundschule, etc.)';
COMMENT ON COLUMN STIFTUNGEN.quelle IS 'Datenquelle: DSZ, Bundesverband, DKJS, etc.';

-- Trigger für updated_at
CREATE OR REPLACE TRIGGER trg_stiftungen_updated_at
BEFORE UPDATE ON STIFTUNGEN
FOR EACH ROW
BEGIN
    :NEW.updated_at := CURRENT_TIMESTAMP;
END;
/

-- Beispiel-Daten für Tests
INSERT INTO STIFTUNGEN (
    name, website, beschreibung, foerderbereiche, 
    foerdersumme_min, foerdersumme_max, bundesland, 
    zielgruppen, quelle, quelle_url
) VALUES (
    'Test-Stiftung für Grundschulbildung',
    'https://example-stiftung.de',
    'Fördert innovative Bildungsprojekte an Grundschulen',
    '["Bildung", "MINT", "Digitalisierung"]',
    5000, 25000,
    'Berlin',
    '["Grundschule", "Primarstufe"]',
    'TEST',
    'https://example.com/test'
);

COMMIT;
