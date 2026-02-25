-- Factory Knowledge GraphRAG - PostgreSQL初期スキーマ
-- Phase 1: MVP

-- UUID拡張
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================
-- users テーブル
-- =====================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(200),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    department VARCHAR(100),
    ad_object_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_department ON users(department);

-- =====================
-- sessions テーブル
-- =====================
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- =====================
-- documents テーブル
-- =====================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000),
    file_type VARCHAR(20) NOT NULL,
    file_size BIGINT,
    document_type VARCHAR(50),
    department VARCHAR(100),
    version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT true,
    previous_version_id UUID REFERENCES documents(id),
    minio_object_key VARCHAR(500) NOT NULL,
    minio_bucket VARCHAR(100) DEFAULT 'documents',
    chunk_count INTEGER DEFAULT 0,
    etl_status VARCHAR(20) DEFAULT 'pending',
    etl_error TEXT,
    uploaded_by UUID REFERENCES users(id),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_department ON documents(department);
CREATE INDEX idx_documents_latest ON documents(is_latest);
CREATE INDEX idx_documents_etl_status ON documents(etl_status);
CREATE INDEX idx_documents_file_name ON documents(file_name);

-- =====================
-- chat_sessions テーブル
-- =====================
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);

-- =====================
-- chat_messages テーブル
-- =====================
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,
    graph_data JSONB,
    token_count INTEGER,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(chat_session_id);
CREATE INDEX idx_chat_messages_created ON chat_messages(created_at);

-- =====================
-- feedback テーブル
-- =====================
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    rating VARCHAR(10) NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_message ON feedback(chat_message_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);

-- =====================
-- etl_jobs テーブル
-- =====================
CREATE TABLE etl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'queued',
    progress REAL DEFAULT 0.0,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_etl_jobs_status ON etl_jobs(status);
CREATE INDEX idx_etl_jobs_document ON etl_jobs(document_id);

-- =====================
-- audit_log テーブル
-- =====================
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);

-- =====================
-- 初期管理者ユーザー (パスワード: admin123 のbcryptハッシュ)
-- 本番環境では変更必須
-- =====================
INSERT INTO users (username, email, password_hash, display_name, role, department)
VALUES (
    'admin',
    'admin@factory.local',
    '$2b$12$21BZVFu7IV/suj06MSdbtOGJlfVhNcNRMJ6IvFwLuP2a35y.NCmpy',
    'System Administrator',
    'admin',
    'IT'
);
