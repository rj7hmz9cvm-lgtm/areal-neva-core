PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    parent_task_id TEXT,
    media_group_id TEXT,
    chat_id INTEGER NOT NULL,
    topic_id INTEGER,
    user_id INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT '',
    input_type TEXT NOT NULL DEFAULT '',
    raw_input TEXT,
    parsed_input TEXT,
    agent_type TEXT,
    state TEXT NOT NULL DEFAULT 'NEW',
    priority INTEGER NOT NULL DEFAULT 5,
    cancellable INTEGER NOT NULL DEFAULT 1,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    next_retry_at TEXT,
    result TEXT,
    drive_url TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    timeout_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_tasks_chat_topic ON tasks(chat_id, topic_id, created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(state, priority, created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    source_message_id INTEGER,
    type TEXT NOT NULL,
    file_path TEXT,
    file_url TEXT,
    drive_url TEXT,
    storage_url TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    processing_status TEXT NOT NULL DEFAULT 'pending',
    error TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_artifacts_task_id ON artifacts(task_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(processing_status);

CREATE TABLE IF NOT EXISTS state_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    triggered_by TEXT,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_state_transitions_task ON state_transitions(task_id);

CREATE TABLE IF NOT EXISTS context_sessions (
    id TEXT PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    topic_id INTEGER,
    user_id INTEGER NOT NULL DEFAULT 0,
    last_task_id TEXT,
    history TEXT NOT NULL DEFAULT '[]',
    pinned_data TEXT NOT NULL DEFAULT '{}',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ctx_chat_topic
ON context_sessions(chat_id, COALESCE(topic_id, -1));

CREATE TABLE IF NOT EXISTS pinned_messages (
    id TEXT PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    topic_id INTEGER,
    message_id INTEGER NOT NULL,
    task_id TEXT,
    label TEXT,
    content TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS agent_executions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    event TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS leads_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    raw_text TEXT,
    volume TEXT,
    location TEXT,
    phone TEXT,
    budget TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS automation_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL DEFAULT 'schedule',
    source TEXT,
    chat_id INTEGER NOT NULL DEFAULT 0,
    topic_id INTEGER,
    user_id INTEGER NOT NULL DEFAULT 0,
    target_id TEXT,
    condition_json TEXT NOT NULL DEFAULT '{}',
    schedule_json TEXT NOT NULL DEFAULT '{}',
    message_template TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    last_run_at TEXT,
    next_run_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_automation_rules_active
ON automation_rules(is_active, type, next_run_at);

CREATE TABLE IF NOT EXISTS automation_events (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'done',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_automation_events_rule
ON automation_events(rule_id, created_at);

CREATE TABLE IF NOT EXISTS followup_state (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    chat_id INTEGER NOT NULL,
    topic_id INTEGER,
    user_id INTEGER NOT NULL DEFAULT 0,
    last_seen_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    last_replied_at TEXT,
    followup_required INTEGER NOT NULL DEFAULT 1,
    followup_deadline TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    status TEXT NOT NULL DEFAULT 'open',
    UNIQUE(source, external_id)
);

CREATE INDEX IF NOT EXISTS idx_followup_due
ON followup_state(followup_required, status, followup_deadline);

CREATE TABLE IF NOT EXISTS memory_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    topic_id    INTEGER,
    role        TEXT NOT NULL DEFAULT 'user',
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memory_chat
ON memory_log(chat_id, topic_id, created_at);

CREATE TABLE IF NOT EXISTS reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    topic_id    INTEGER,
    text        TEXT NOT NULL,
    done        INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reminders_done
ON reminders(done, created_at);
