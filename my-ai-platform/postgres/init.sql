-- PostgreSQL 초기화 스크립트
-- AI Platform - 구조화된 데이터 저장용

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 대화 세션 테이블
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 대화 메시지 테이블
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 문서 메타데이터 테이블 (실제 벡터는 Milvus에 저장)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500),
    source VARCHAR(500),
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    milvus_collection VARCHAR(100), -- Milvus 컬렉션 이름
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 문서 청크 메타데이터 (벡터는 Milvus, 메타데이터는 PostgreSQL)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    milvus_id VARCHAR(100), -- Milvus에서의 벡터 ID
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Agent 실행 로그 테이블
CREATE TABLE IF NOT EXISTS agent_executions (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES conversation_sessions(id),
    agent_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    error_message TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- RAG 검색 로그 테이블
CREATE TABLE IF NOT EXISTS rag_queries (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES conversation_sessions(id),
    query_text TEXT NOT NULL,
    retrieved_chunks INTEGER,
    response_text TEXT,
    relevance_scores JSONB, -- [0.95, 0.87, 0.82, ...]
    search_time_ms INTEGER,
    generation_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX idx_messages_session_id ON conversation_messages(session_id);
CREATE INDEX idx_messages_created_at ON conversation_messages(created_at);
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_milvus_id ON document_chunks(milvus_id);
CREATE INDEX idx_agent_executions_session_id ON agent_executions(session_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_rag_queries_session_id ON rag_queries(session_id);

-- 샘플 데이터 삽입 (개발용)
INSERT INTO users (username, email) 
VALUES 
    ('admin', 'admin@example.com'),
    ('test_user', 'test@example.com')
ON CONFLICT (username) DO NOTHING;

-- 함수: 업데이트 시간 자동 갱신
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 설정
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_sessions_updated_at BEFORE UPDATE ON conversation_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE users IS '사용자 정보';
COMMENT ON TABLE conversation_sessions IS '대화 세션 (채팅방)';
COMMENT ON TABLE conversation_messages IS '대화 메시지 내역';
COMMENT ON TABLE documents IS '업로드된 문서 메타데이터';
COMMENT ON TABLE document_chunks IS '문서 청크 메타데이터 (벡터는 Milvus)';
COMMENT ON TABLE agent_executions IS 'LangGraph 에이전트 실행 로그';
COMMENT ON TABLE rag_queries IS 'RAG 검색 쿼리 로그';
