-- Oracle Database Schema v2 for Förder-Finder Grundschule
-- Enhanced Production Schema with Full-Text Search Support
-- Migration from SQLite Development Database
-- Date: 2025-11-03

-- ============================================================
-- CLEANUP: Drop existing objects (if migration retry)
-- ============================================================

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE APPLICATION_DRAFTS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE APPLICATIONS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE FUNDING_OPPORTUNITIES CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE STIFTUNGEN CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE USERS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE SCHOOLS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ============================================================
-- TABLE: SCHOOLS (Mandanten - Grundschulen)
-- ============================================================

CREATE TABLE SCHOOLS (
    school_id VARCHAR2(36) PRIMARY KEY,
    name VARCHAR2(255) NOT NULL,
    address VARCHAR2(500),
    city VARCHAR2(100),
    state VARCHAR2(50),
    postal_code VARCHAR2(20),
    contact_email VARCHAR2(255),
    contact_phone VARCHAR2(50),

    -- Audit fields
    is_active NUMBER(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR2(36),
    updated_by VARCHAR2(36),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR2(36)
);

COMMENT ON TABLE SCHOOLS IS 'Grundschulen (Multi-Tenant)';
COMMENT ON COLUMN SCHOOLS.is_active IS 'Soft delete flag';

-- ============================================================
-- TABLE: USERS (Nutzer mit Rollen)
-- ============================================================

CREATE TABLE USERS (
    user_id VARCHAR2(36) PRIMARY KEY,
    school_id VARCHAR2(36) NOT NULL,
    email VARCHAR2(255) UNIQUE NOT NULL,
    password_hash VARCHAR2(255) NOT NULL,
    first_name VARCHAR2(100),
    last_name VARCHAR2(100),
    full_name VARCHAR2(255),
    role VARCHAR2(50) DEFAULT 'lehrkraft' CHECK (role IN ('admin', 'lehrkraft')),

    -- Audit fields
    is_active NUMBER(1) DEFAULT 1,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR2(36),
    updated_by VARCHAR2(36),

    CONSTRAINT fk_users_school FOREIGN KEY (school_id)
        REFERENCES SCHOOLS(school_id) ON DELETE CASCADE
);

COMMENT ON TABLE USERS IS 'Nutzer (Lehrer, Admins)';

-- ============================================================
-- TABLE: STIFTUNGEN (Stiftungsdatenbank)
-- ============================================================

CREATE TABLE STIFTUNGEN (
    stiftung_id VARCHAR2(36) PRIMARY KEY,
    name VARCHAR2(500) NOT NULL,
    description CLOB,
    website VARCHAR2(1000),

    -- Geographical
    bundesland VARCHAR2(100),
    stadt VARCHAR2(100),
    plz VARCHAR2(20),

    -- Metadata
    quelle VARCHAR2(100),  -- e.g., 'stiftungen.org'
    stiftungsart VARCHAR2(100),
    stiftungszweck CLOB,

    -- Audit
    is_active NUMBER(1) DEFAULT 1,
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE STIFTUNGEN IS 'Stiftungen Verzeichnis';

-- ============================================================
-- TABLE: FUNDING_OPPORTUNITIES (Fördermittel)
-- ============================================================

CREATE TABLE FUNDING_OPPORTUNITIES (
    funding_id VARCHAR2(36) PRIMARY KEY,

    -- Basic Info
    title VARCHAR2(500) NOT NULL,
    provider VARCHAR2(255),
    funder_name VARCHAR2(255),

    -- Large text fields (CLOB for > 4000 chars)
    description CLOB,
    eligibility CLOB,
    evaluation_criteria CLOB,
    requirements CLOB,
    application_process CLOB,
    eligible_costs CLOB,
    cleaned_text CLOB,  -- RAG-optimized text (avg 19KB, max 198KB)
    metadata_json CLOB,

    -- Dates
    application_deadline DATE,
    deadline DATE,  -- Duplicate, can be removed after migration

    -- Funding Amounts (NUMBER for precision)
    funding_amount_min NUMBER(12, 2),
    min_funding_amount NUMBER(12, 2),  -- Duplicate, can be removed
    funding_amount_max NUMBER(12, 2),
    max_funding_amount NUMBER(12, 2),  -- Duplicate, can be removed
    co_financing_rate NUMBER(5, 2),

    -- Booleans
    co_financing_required NUMBER(1) DEFAULT 0,

    -- Categories (comma-separated for now, normalize later)
    categories VARCHAR2(1000),
    target_groups VARCHAR2(1000),
    region VARCHAR2(100),
    funding_area VARCHAR2(200),
    funding_type VARCHAR2(100),
    source_type VARCHAR2(50) DEFAULT 'website',

    -- URLs
    url VARCHAR2(1000),
    source_url VARCHAR2(1000),
    application_url VARCHAR2(1000),

    -- Contact
    contact_person VARCHAR2(255),
    contact_email VARCHAR2(255),
    contact_phone VARCHAR2(100),

    -- Foreign Keys
    stiftung_id VARCHAR2(36),

    -- Quality/Processing Metrics
    scraped_pages NUMBER(3) DEFAULT 1,
    extraction_quality_score NUMBER(3, 2),

    -- Timestamps
    last_scraped TIMESTAMP,
    last_extracted TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Audit fields (soft delete)
    created_by VARCHAR2(36),
    updated_by VARCHAR2(36),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR2(36),

    CONSTRAINT fk_funding_stiftung FOREIGN KEY (stiftung_id)
        REFERENCES STIFTUNGEN(stiftung_id) ON DELETE SET NULL
);

COMMENT ON TABLE FUNDING_OPPORTUNITIES IS 'Fördermittel Datenbank';
COMMENT ON COLUMN FUNDING_OPPORTUNITIES.cleaned_text IS 'RAG-optimized text for AI (Firecrawl markdown)';
COMMENT ON COLUMN FUNDING_OPPORTUNITIES.extraction_quality_score IS 'LLM extraction quality (0.0-1.0)';

-- ============================================================
-- TABLE: APPLICATIONS (Anträge der Schulen)
-- ============================================================

CREATE TABLE APPLICATIONS (
    application_id VARCHAR2(36) PRIMARY KEY,
    school_id VARCHAR2(36) NOT NULL,
    funding_id VARCHAR2(36) NOT NULL,
    user_id VARCHAR2(36) NOT NULL,

    title VARCHAR2(500) NOT NULL,
    status VARCHAR2(50) DEFAULT 'draft'
        CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'withdrawn')),

    -- Application content
    application_text CLOB,
    draft_text CLOB,
    final_text CLOB,

    -- Metadata
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Audit
    created_by VARCHAR2(36),
    updated_by VARCHAR2(36),

    CONSTRAINT fk_app_school FOREIGN KEY (school_id)
        REFERENCES SCHOOLS(school_id) ON DELETE CASCADE,
    CONSTRAINT fk_app_funding FOREIGN KEY (funding_id)
        REFERENCES FUNDING_OPPORTUNITIES(funding_id) ON DELETE CASCADE,
    CONSTRAINT fk_app_user FOREIGN KEY (user_id)
        REFERENCES USERS(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE APPLICATIONS IS 'Förderanträge';

-- ============================================================
-- TABLE: APPLICATION_DRAFTS (KI-generierte Entwürfe)
-- ============================================================

CREATE TABLE APPLICATION_DRAFTS (
    draft_id VARCHAR2(36) PRIMARY KEY,
    application_id VARCHAR2(36),  -- Can be NULL for standalone drafts
    school_id VARCHAR2(36) NOT NULL,
    funding_id VARCHAR2(36) NOT NULL,
    user_id VARCHAR2(36) NOT NULL,

    -- Draft content
    draft_text CLOB NOT NULL,
    school_context CLOB,

    -- AI metadata
    ai_model VARCHAR2(100),
    prompt_used CLOB,
    user_feedback VARCHAR2(1000),
    version INTEGER DEFAULT 1,

    -- Timestamps
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_draft_application FOREIGN KEY (application_id)
        REFERENCES APPLICATIONS(application_id) ON DELETE CASCADE,
    CONSTRAINT fk_draft_school FOREIGN KEY (school_id)
        REFERENCES SCHOOLS(school_id) ON DELETE CASCADE,
    CONSTRAINT fk_draft_funding FOREIGN KEY (funding_id)
        REFERENCES FUNDING_OPPORTUNITIES(funding_id) ON DELETE CASCADE,
    CONSTRAINT fk_draft_user FOREIGN KEY (user_id)
        REFERENCES USERS(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE APPLICATION_DRAFTS IS 'KI-generierte Antragsentwürfe';

-- ============================================================
-- INDEXES: Performance Optimization
-- ============================================================

-- SCHOOLS indexes
CREATE INDEX idx_schools_active ON SCHOOLS(is_active, deleted_at);

-- USERS indexes
CREATE INDEX idx_users_school ON USERS(school_id);
CREATE INDEX idx_users_email ON USERS(email);
CREATE INDEX idx_users_active ON USERS(is_active);

-- STIFTUNGEN indexes
CREATE INDEX idx_stiftungen_bundesland ON STIFTUNGEN(bundesland);
CREATE INDEX idx_stiftungen_quelle ON STIFTUNGEN(quelle);
CREATE INDEX idx_stiftungen_active ON STIFTUNGEN(is_active);

-- FUNDING_OPPORTUNITIES indexes (Critical for performance!)
CREATE INDEX idx_funding_deadline ON FUNDING_OPPORTUNITIES(application_deadline);
CREATE INDEX idx_funding_deadline_active ON FUNDING_OPPORTUNITIES(application_deadline, source_type);
CREATE INDEX idx_funding_provider ON FUNDING_OPPORTUNITIES(provider);
CREATE INDEX idx_funding_region ON FUNDING_OPPORTUNITIES(region);
CREATE INDEX idx_funding_source_url ON FUNDING_OPPORTUNITIES(source_url);
CREATE INDEX idx_funding_stiftung ON FUNDING_OPPORTUNITIES(stiftung_id);
CREATE INDEX idx_funding_quality ON FUNDING_OPPORTUNITIES(extraction_quality_score DESC);

-- Composite index for common query pattern
CREATE INDEX idx_funding_amount_range
    ON FUNDING_OPPORTUNITIES(funding_amount_min, funding_amount_max);

-- APPLICATIONS indexes
CREATE INDEX idx_applications_school ON APPLICATIONS(school_id);
CREATE INDEX idx_applications_funding ON APPLICATIONS(funding_id);
CREATE INDEX idx_applications_user ON APPLICATIONS(user_id);
CREATE INDEX idx_applications_status ON APPLICATIONS(status);

-- APPLICATION_DRAFTS indexes
CREATE INDEX idx_drafts_application ON APPLICATION_DRAFTS(application_id);
CREATE INDEX idx_drafts_school ON APPLICATION_DRAFTS(school_id);
CREATE INDEX idx_drafts_funding ON APPLICATION_DRAFTS(funding_id);

-- ============================================================
-- ORACLE TEXT FULL-TEXT SEARCH INDEXES
-- ============================================================
-- NOTE: Requires CTXAPP role granted to user
-- GRANT CTXAPP TO ADMIN;
-- GRANT EXECUTE ON CTXSYS.CTX_DDL TO ADMIN;

-- Full-text search on cleaned_text (RAG text)
-- This makes CONTAINS() queries 10-100x faster than LIKE '%keyword%'
CREATE INDEX idx_funding_fulltext
    ON FUNDING_OPPORTUNITIES(cleaned_text)
    INDEXTYPE IS CTXSYS.CONTEXT
    PARAMETERS ('SYNC (ON COMMIT)');

-- Full-text search on description
CREATE INDEX idx_funding_desc_fulltext
    ON FUNDING_OPPORTUNITIES(description)
    INDEXTYPE IS CTXSYS.CONTEXT
    PARAMETERS ('SYNC (ON COMMIT)');

-- ============================================================
-- STATISTICS GATHERING (for query optimization)
-- ============================================================

BEGIN
    DBMS_STATS.GATHER_SCHEMA_STATS(
        ownname => USER,
        options => 'GATHER AUTO',
        estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
        method_opt => 'FOR ALL COLUMNS SIZE AUTO',
        cascade => TRUE
    );
END;
/

-- ============================================================
-- GRANT PERMISSIONS
-- ============================================================

-- If using separate API user (recommended)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON SCHOOLS TO api_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON USERS TO api_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON FUNDING_OPPORTUNITIES TO api_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON APPLICATIONS TO api_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON APPLICATION_DRAFTS TO api_user;

COMMIT;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- List all created tables
SELECT table_name, num_rows
FROM user_tables
WHERE table_name IN (
    'SCHOOLS', 'USERS', 'STIFTUNGEN',
    'FUNDING_OPPORTUNITIES', 'APPLICATIONS', 'APPLICATION_DRAFTS'
)
ORDER BY table_name;

-- List all created indexes
SELECT index_name, table_name, uniqueness, index_type
FROM user_indexes
WHERE table_name IN (
    'SCHOOLS', 'USERS', 'STIFTUNGEN',
    'FUNDING_OPPORTUNITIES', 'APPLICATIONS', 'APPLICATION_DRAFTS'
)
ORDER BY table_name, index_name;

-- Verify Oracle Text indexes
SELECT idx_name, idx_table, idx_status
FROM ctx_user_indexes
ORDER BY idx_name;

PROMPT 'Schema creation complete!';
PROMPT 'Next steps:';
PROMPT '1. Run data migration script (migrate_sqlite_to_oracle.py)';
PROMPT '2. Verify row counts match SQLite';
PROMPT '3. Test Oracle Text search: SELECT * FROM FUNDING_OPPORTUNITIES WHERE CONTAINS(cleaned_text, ''grundschule'') > 0;';
PROMPT '4. Update backend/.env to USE_SQLITE=false';
