-- ============================================================================
-- Förder-Finder Grundschule - Database Schema
-- Database: Oracle Autonomous Database (ATP)
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- 1. MANDANTEN-TABELLE (SCHULEN)
-- ============================================================================
CREATE TABLE SCHOOLS (
    school_id RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    school_name VARCHAR2(255) NOT NULL,
    school_number VARCHAR2(50) UNIQUE, -- Offizielle Schulnummer
    address CLOB, -- JSON: {street, zip, city, state}
    schultyp VARCHAR2(100), -- "Grundschule", "Förderschule"
    schuelerzahl NUMBER(5),
    traeger VARCHAR2(255), -- "Kommunal", "Privat", "Kirchlich"
    contact_email VARCHAR2(255),
    contact_phone VARCHAR2(50),
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    is_active NUMBER(1) DEFAULT 1, -- 1=aktiv, 0=inaktiv
    CONSTRAINT chk_school_active CHECK (is_active IN (0, 1))
);

CREATE INDEX idx_schools_name ON SCHOOLS(school_name);
CREATE INDEX idx_schools_active ON SCHOOLS(is_active);

-- ============================================================================
-- 2. NUTZER-TABELLE
-- ============================================================================
CREATE TABLE USERS (
    user_id RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    school_id RAW(16) NOT NULL,
    email VARCHAR2(255) NOT NULL UNIQUE,
    password_hash VARCHAR2(255) NOT NULL,
    first_name VARCHAR2(100),
    last_name VARCHAR2(100),
    role VARCHAR2(50) DEFAULT 'lehrkraft' NOT NULL,
    is_active NUMBER(1) DEFAULT 1,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_user_school FOREIGN KEY (school_id)
        REFERENCES SCHOOLS(school_id) ON DELETE CASCADE,
    CONSTRAINT chk_user_role CHECK (role IN ('admin', 'lehrkraft', 'sekretariat')),
    CONSTRAINT chk_user_active CHECK (is_active IN (0, 1))
);

CREATE INDEX idx_users_email ON USERS(email);
CREATE INDEX idx_users_school ON USERS(school_id);
CREATE INDEX idx_users_role ON USERS(role);

-- ============================================================================
-- 3. GESCRAPTE FÖRDERMITTEL
-- ============================================================================
CREATE TABLE FUNDING_OPPORTUNITIES (
    funding_id RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    title VARCHAR2(1000) NOT NULL,
    source_url VARCHAR2(2048) NOT NULL UNIQUE,
    deadline TIMESTAMP,
    provider VARCHAR2(500), -- "BMBF", "Land Brandenburg", etc.
    region VARCHAR2(255), -- "Bundesweit", "Brandenburg", "Berlin"
    funding_area VARCHAR2(255), -- "Digitalisierung", "Sport", "MINT"
    tags CLOB, -- JSON-Array: ["Digital", "Inklusion", "MINT"]
    cleaned_text CLOB NOT NULL, -- Haupttext für RAG (sehr wichtig!)
    metadata_json CLOB, -- JSON mit allen weiteren Feldern
    min_funding_amount NUMBER(12,2),
    max_funding_amount NUMBER(12,2),
    scraped_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    is_active NUMBER(1) DEFAULT 1,
    CONSTRAINT chk_funding_active CHECK (is_active IN (0, 1))
);

CREATE INDEX idx_funding_deadline ON FUNDING_OPPORTUNITIES(deadline);
CREATE INDEX idx_funding_provider ON FUNDING_OPPORTUNITIES(provider);
CREATE INDEX idx_funding_region ON FUNDING_OPPORTUNITIES(region);
CREATE INDEX idx_funding_area ON FUNDING_OPPORTUNITIES(funding_area);
CREATE INDEX idx_funding_active ON FUNDING_OPPORTUNITIES(is_active);

-- ============================================================================
-- 4. ANTRAGS-VERWALTUNG
-- ============================================================================
CREATE TABLE APPLICATIONS (
    application_id RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    school_id RAW(16) NOT NULL,
    user_id_created RAW(16) NOT NULL,
    funding_id_linked RAW(16),
    title VARCHAR2(1000) NOT NULL,
    status VARCHAR2(50) DEFAULT 'entwurf' NOT NULL,
    projektbeschreibung CLOB, -- Manuelle Beschreibung durch Schule
    budget_total NUMBER(12,2),
    budget_details CLOB, -- JSON: Kostenaufstellung
    submission_date TIMESTAMP,
    decision_date TIMESTAMP,
    decision_status VARCHAR2(50), -- "genehmigt", "abgelehnt", "nachbesserung"
    notes CLOB,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_app_school FOREIGN KEY (school_id)
        REFERENCES SCHOOLS(school_id) ON DELETE CASCADE,
    CONSTRAINT fk_app_user FOREIGN KEY (user_id_created)
        REFERENCES USERS(user_id),
    CONSTRAINT fk_app_funding FOREIGN KEY (funding_id_linked)
        REFERENCES FUNDING_OPPORTUNITIES(funding_id),
    CONSTRAINT chk_app_status CHECK (status IN (
        'entwurf', 'in_bearbeitung', 'eingereicht', 'genehmigt', 'abgelehnt'
    ))
);

CREATE INDEX idx_app_school ON APPLICATIONS(school_id);
CREATE INDEX idx_app_user ON APPLICATIONS(user_id_created);
CREATE INDEX idx_app_funding ON APPLICATIONS(funding_id_linked);
CREATE INDEX idx_app_status ON APPLICATIONS(status);
CREATE INDEX idx_app_created ON APPLICATIONS(created_at);

-- ============================================================================
-- 5. KI-GENERIERTE ENTWÜRFE
-- ============================================================================
CREATE TABLE APPLICATION_DRAFTS (
    draft_id RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    application_id RAW(16) NOT NULL,
    generated_content CLOB NOT NULL,
    model_used VARCHAR2(100) DEFAULT 'DeepSeek',
    prompt_used CLOB, -- Der verwendete Prompt (für Debugging)
    generation_metadata CLOB, -- JSON: temperature, tokens, etc.
    user_feedback VARCHAR2(50), -- "helpful", "not_helpful"
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_draft_app FOREIGN KEY (application_id)
        REFERENCES APPLICATIONS(application_id) ON DELETE CASCADE
);

CREATE INDEX idx_draft_app ON APPLICATION_DRAFTS(application_id);
CREATE INDEX idx_draft_created ON APPLICATION_DRAFTS(created_at);

-- ============================================================================
-- 6. AUDIT LOG (Optional, für Compliance)
-- ============================================================================
CREATE TABLE AUDIT_LOG (
    log_id RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    user_id RAW(16),
    school_id RAW(16),
    action VARCHAR2(100) NOT NULL, -- "LOGIN", "CREATE_APPLICATION", etc.
    entity_type VARCHAR2(50), -- "APPLICATION", "USER", etc.
    entity_id RAW(16),
    details CLOB, -- JSON mit allen Details
    ip_address VARCHAR2(50),
    user_agent VARCHAR2(500),
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id)
        REFERENCES USERS(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_audit_school FOREIGN KEY (school_id)
        REFERENCES SCHOOLS(school_id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_user ON AUDIT_LOG(user_id);
CREATE INDEX idx_audit_school ON AUDIT_LOG(school_id);
CREATE INDEX idx_audit_action ON AUDIT_LOG(action);
CREATE INDEX idx_audit_created ON AUDIT_LOG(created_at);

-- ============================================================================
-- 7. TRIGGER FÜR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE TRIGGER trg_schools_updated
    BEFORE UPDATE ON SCHOOLS
    FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_users_updated
    BEFORE UPDATE ON USERS
    FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_funding_updated
    BEFORE UPDATE ON FUNDING_OPPORTUNITIES
    FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_applications_updated
    BEFORE UPDATE ON APPLICATIONS
    FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

-- ============================================================================
-- 8. INITIALE TEST-DATEN (Optional)
-- ============================================================================

-- Beispiel-Schule
INSERT INTO SCHOOLS (school_name, school_number, address, schultyp, schuelerzahl, traeger, contact_email)
VALUES (
    'Grundschule am Musterberg',
    'BB-12345',
    '{"street": "Musterstraße 1", "zip": "12345", "city": "Berlin", "state": "Berlin"}',
    'Grundschule',
    320,
    'Kommunal',
    'info@gs-musterberg.de'
);

-- Beispiel-Admin-User (Passwort: admin123 - MUSS in Production geändert werden!)
-- Hash generiert mit: passlib.hash.bcrypt.hash("admin123")
INSERT INTO USERS (school_id, email, password_hash, first_name, last_name, role)
VALUES (
    (SELECT school_id FROM SCHOOLS WHERE school_number = 'BB-12345'),
    'admin@gs-musterberg.de',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qUxR7Doju',
    'Max',
    'Mustermann',
    'admin'
);

COMMIT;

-- ============================================================================
-- 9. HILFREICHE VIEWS
-- ============================================================================

-- View: Aktive Fördermittel mit offenen Fristen
CREATE OR REPLACE VIEW V_ACTIVE_FUNDING AS
SELECT
    f.funding_id,
    f.title,
    f.provider,
    f.region,
    f.funding_area,
    f.deadline,
    f.min_funding_amount,
    f.max_funding_amount,
    CASE
        WHEN f.deadline > SYSTIMESTAMP THEN
            EXTRACT(DAY FROM (f.deadline - SYSTIMESTAMP))
        ELSE 0
    END AS days_until_deadline
FROM FUNDING_OPPORTUNITIES f
WHERE f.is_active = 1
  AND (f.deadline IS NULL OR f.deadline > SYSTIMESTAMP)
ORDER BY f.deadline ASC NULLS LAST;

-- View: Antrags-Übersicht pro Schule
CREATE OR REPLACE VIEW V_APPLICATION_SUMMARY AS
SELECT
    s.school_id,
    s.school_name,
    COUNT(CASE WHEN a.status = 'entwurf' THEN 1 END) AS entwuerfe,
    COUNT(CASE WHEN a.status = 'eingereicht' THEN 1 END) AS eingereicht,
    COUNT(CASE WHEN a.status = 'genehmigt' THEN 1 END) AS genehmigt,
    COUNT(CASE WHEN a.status = 'abgelehnt' THEN 1 END) AS abgelehnt,
    SUM(CASE WHEN a.status = 'genehmigt' THEN a.budget_total ELSE 0 END) AS total_approved_funding
FROM SCHOOLS s
LEFT JOIN APPLICATIONS a ON s.school_id = a.school_id
GROUP BY s.school_id, s.school_name;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
