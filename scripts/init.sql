-- Initialize schema for sql-rag project

CREATE TABLE "user" (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bio TEXT
);

CREATE TABLE "task_type" (
    task_type_id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    valid_response_format TEXT
);

CREATE TABLE "metric" (
    metric_id SERIAL PRIMARY KEY,
    task_type_id INTEGER REFERENCES "task_type"(task_type_id),
    name VARCHAR(100) NOT NULL,
    formula TEXT,
    optimization_direction VARCHAR(10),
    description TEXT
);

CREATE TABLE "competition" (
    competition_id SERIAL PRIMARY KEY,
    organizer_id INTEGER REFERENCES "user"(user_id),
    task_type_id INTEGER REFERENCES "task_type"(task_type_id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'draft'
);

CREATE TABLE "competition_config" (
    config_id SERIAL PRIMARY KEY,
    competition_id INTEGER REFERENCES "competition"(competition_id),
    metric_id INTEGER REFERENCES "metric"(metric_id),
    aggregation_rule VARCHAR(20) DEFAULT 'best',
    max_daily_submissions INTEGER DEFAULT 5
);

CREATE TABLE "prize" (
    prize_id SERIAL PRIMARY KEY,
    competition_id INTEGER REFERENCES "competition"(competition_id),
    rank_position INTEGER,
    description TEXT,
    amount DECIMAL(15, 2),
    currency VARCHAR(10) DEFAULT 'USD'
);

CREATE TABLE "participation" (
    participation_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(user_id),
    competition_id INTEGER REFERENCES "competition"(competition_id),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE "dataset" (
    dataset_id SERIAL PRIMARY KEY,
    competition_id INTEGER REFERENCES "competition"(competition_id),
    name VARCHAR(255) NOT NULL,
    usage_type VARCHAR(20),
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "file_artifact" (
    file_id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES "dataset"(dataset_id),
    filename VARCHAR(255) NOT NULL,
    storage_path TEXT,
    checksum VARCHAR(64),
    size_bytes BIGINT
);

CREATE TABLE "submission" (
    submission_id SERIAL PRIMARY KEY,
    participation_id INTEGER REFERENCES "participation"(participation_id),
    file_path TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'queued'
);

CREATE TABLE "evaluation" (
    evaluation_id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES "submission"(submission_id),
    metric_value DECIMAL(20, 10),
    is_valid BOOLEAN DEFAULT TRUE,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_log TEXT
);

CREATE TABLE "leaderboard_row" (
    row_id SERIAL PRIMARY KEY,
    participation_id INTEGER REFERENCES "participation"(participation_id),
    best_evaluation_id INTEGER REFERENCES "evaluation"(evaluation_id),
    score DECIMAL(20, 10),
    rank INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "code_kernel" (
    kernel_id SERIAL PRIMARY KEY,
    participation_id INTEGER REFERENCES "participation"(participation_id),
    evaluation_id INTEGER REFERENCES "evaluation"(evaluation_id),
    title VARCHAR(255),
    source_code TEXT,
    language VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
