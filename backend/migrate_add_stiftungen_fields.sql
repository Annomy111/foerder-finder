-- ============================================================================
-- Migration: Add Stiftungen Support to FUNDING_OPPORTUNITIES
-- Datum: 2025-10-29
-- Zweck: Felder für Stiftungs-Integration hinzufügen
-- ============================================================================

-- Add missing columns
ALTER TABLE FUNDING_OPPORTUNITIES ADD (
    region VARCHAR2(100),
    funder_name VARCHAR2(255),
    source_url VARCHAR2(1000),
    source_type VARCHAR2(50) DEFAULT 'website'
);

-- Add index for source_type (häufig gefiltert)
CREATE INDEX idx_funding_source_type ON FUNDING_OPPORTUNITIES(source_type);

-- Add index for region
CREATE INDEX idx_funding_region ON FUNDING_OPPORTUNITIES(region);

-- Kommentare
COMMENT ON COLUMN FUNDING_OPPORTUNITIES.source_type IS 'Typ: website, stiftung, eu, bund';
COMMENT ON COLUMN FUNDING_OPPORTUNITIES.region IS 'Bundesland oder Bundesweit';
COMMENT ON COLUMN FUNDING_OPPORTUNITIES.funder_name IS 'Name des Förderers/Stiftung';
COMMENT ON COLUMN FUNDING_OPPORTUNITIES.source_url IS 'Original-URL der Quelle';

-- Update existing records
UPDATE FUNDING_OPPORTUNITIES
SET source_type = 'website'
WHERE source_type IS NULL;

COMMIT;
