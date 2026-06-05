-- 05-数据库Schema.sql
-- MVP schema draft for TeamBrain
-- PostgreSQL + pgvector

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100),
    real_name VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(200),
    status VARCHAR(50) DEFAULT 'active',
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(100) UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS project_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    role_in_project VARCHAR(100),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_im_bindings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    im_platform VARCHAR(50) NOT NULL,
    im_user_id VARCHAR(200) NOT NULL,
    im_display_name VARCHAR(200),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE(im_platform, im_user_id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    im_platform VARCHAR(50) NOT NULL,
    conversation_type VARCHAR(50) NOT NULL,
    conversation_id VARCHAR(200) NOT NULL,
    group_id VARCHAR(200),
    title VARCHAR(500),
    project_id UUID REFERENCES projects(id),
    takeover_mode VARCHAR(50) DEFAULT 'collaborate',
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE(im_platform, conversation_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(100) UNIQUE NOT NULL,
    message_uid VARCHAR(200),
    conversation_id UUID REFERENCES conversations(id),
    project_id UUID REFERENCES projects(id),
    sender_user_id UUID REFERENCES users(id),
    sender_im_id VARCHAR(200),
    sender_name VARCHAR(200),
    message_type VARCHAR(50) DEFAULT 'text',
    direction VARCHAR(50) DEFAULT 'user_to_agent',
    content TEXT,
    attachments JSONB DEFAULT '[]'::jsonb,
    raw_payload JSONB,
    is_at_bot BOOLEAN DEFAULT FALSE,
    takeover BOOLEAN,
    takeover_reason VARCHAR(200),
    intent VARCHAR(100),
    status VARCHAR(50) DEFAULT 'received',
    created_at TIMESTAMP DEFAULT now(),
    processed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_no VARCHAR(100) UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    message_id UUID REFERENCES messages(id),
    payload JSONB,
    status VARCHAR(50) DEFAULT 'recorded',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_no VARCHAR(100) UNIQUE,
    project_id UUID REFERENCES projects(id),
    source_message_id UUID REFERENCES messages(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    owner_text VARCHAR(200),
    status VARCHAR(50) DEFAULT 'todo',
    due_date TIMESTAMP,
    due_text VARCHAR(200),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_no VARCHAR(100) UNIQUE,
    project_id UUID REFERENCES projects(id),
    title VARCHAR(500),
    summary TEXT,
    attendees JSONB DEFAULT '[]'::jsonb,
    source_message_id UUID REFERENCES messages(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_no VARCHAR(100) UNIQUE,
    project_id UUID REFERENCES projects(id),
    message_id UUID REFERENCES messages(id),
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(100),
    bucket VARCHAR(100),
    object_key TEXT,
    storage_path TEXT,
    file_size BIGINT,
    uploaded_by UUID REFERENCES users(id),
    parse_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    package_code VARCHAR(100) UNIQUE,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    package_type VARCHAR(100) NOT NULL,
    project_id UUID REFERENCES projects(id),
    status VARCHAR(50) DEFAULT 'active',
    priority INT DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    knowledge_package_id UUID REFERENCES knowledge_packages(id),
    file_id UUID REFERENCES files(id),
    title VARCHAR(500),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id),
    knowledge_package_id UUID REFERENCES knowledge_packages(id),
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding vector,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_event_id ON messages(event_id);
CREATE INDEX IF NOT EXISTS idx_messages_intent ON messages(intent);
CREATE INDEX IF NOT EXISTS idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_chunks_package ON document_chunks(knowledge_package_id);
