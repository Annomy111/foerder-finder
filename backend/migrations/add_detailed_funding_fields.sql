/*
 * Migration: Add Detailed Funding Fields
 * Purpose: Store structured metadata extracted via LLM
 * Author: Claude Code
 * Date: 2025-10-29
 * Version: 1.0
 *
 * Usage (SQLite):
 *   sqlite3 dev_database.db < migrations/add_detailed_funding_fields.sql
 *
 * Usage (Oracle):
 *   sqlplus user/pass@db @migrations/add_detailed_funding_fields.sql
 */

-- ============================================================================
-- Add Structured Metadata Fields
-- ============================================================================

-- Evaluation Criteria (how applications are judged)
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN evaluation_criteria TEXT;

-- Formal Requirements (page limits, attachments, format)
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN requirements TEXT;

-- Application Process (how to apply: portal, email, post)
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN application_process TEXT;

-- Direct link to application form
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN application_url TEXT;

-- Contact Person
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN contact_person TEXT;

-- Contact Phone
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN contact_phone TEXT;

-- Decision Timeline (when will applications be decided?)
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN decision_timeline TEXT;

-- Funding Period (project duration: "12 months", "school year 2025/26")
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN funding_period TEXT;

-- ============================================================================
-- Co-Financing Fields
-- ============================================================================

-- Is co-financing (Eigenanteil) required?
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN co_financing_required INTEGER DEFAULT 0;

-- Co-financing rate (0.1 = 10%)
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN co_financing_rate REAL;

-- ============================================================================
-- Eligible Costs (what can be funded?)
-- ============================================================================

-- JSON array of eligible cost categories
-- Example: ["Personal", "Sachmittel", "Fortbildung"]
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN eligible_costs TEXT;

-- ============================================================================
-- Scraping Quality Metrics
-- ============================================================================

-- Number of pages scraped (1 = single page, 3 = multi-page)
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN scraped_pages INTEGER DEFAULT 1;

-- Extraction quality score (0.0 - 1.0)
-- 1.0 = all critical fields present
-- 0.0 = no structured data
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN extraction_quality_score REAL;

-- Timestamp of last extraction
ALTER TABLE FUNDING_OPPORTUNITIES ADD COLUMN last_extracted TIMESTAMP;

-- ============================================================================
-- Create Index for Fast Filtering
-- ============================================================================

-- Index for deadline filtering
CREATE INDEX IF NOT EXISTS idx_funding_deadline
ON FUNDING_OPPORTUNITIES(application_deadline);

-- Index for budget filtering
CREATE INDEX IF NOT EXISTS idx_funding_amount
ON FUNDING_OPPORTUNITIES(funding_amount_min, funding_amount_max);

-- Index for quality filtering (show high-quality data first)
CREATE INDEX IF NOT EXISTS idx_funding_quality
ON FUNDING_OPPORTUNITIES(extraction_quality_score DESC);

-- ============================================================================
-- Comments (for documentation)
-- ============================================================================

-- Note: Some fields use TEXT to store JSON arrays for SQLite compatibility
-- In production with Oracle, consider using JSON data type or separate tables
