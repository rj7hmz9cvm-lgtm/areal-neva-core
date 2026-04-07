PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE tasks (
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
INSERT INTO tasks VALUES('2c5e3f5e-465a-4b1d-8d0d-58bfd6382068',NULL,NULL,-1003725299009,NULL,2061134525,'telegram','voice','Есть кто живой нет?',NULL,NULL,'AWAITING_CONFIRMATION',5,1,0,3,NULL,'Живой: я, DeepSeek. Оркестр из нейросетей отсутствует.',NULL,NULL,'2026-04-06T19:17:45.333Z','2026-04-06T19:18:06.452Z',NULL);
INSERT INTO tasks VALUES('99fd2657-84c1-4dfe-a30c-f4b97236a57a',NULL,NULL,-1003725299009,NULL,2061134525,'telegram','text','тест',NULL,NULL,'AWAITING_CONFIRMATION',5,1,0,3,NULL,'Тест пройден.',NULL,NULL,'2026-04-06T19:17:56.132Z','2026-04-06T19:18:11.457Z',NULL);
CREATE TABLE artifacts (
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
CREATE TABLE state_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    triggered_by TEXT,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
INSERT INTO state_transitions VALUES(1,'2c5e3f5e-465a-4b1d-8d0d-58bfd6382068','NEW','INTAKE','telegram_daemon',NULL,'2026-04-06T19:17:45.336Z');
INSERT INTO state_transitions VALUES(2,'99fd2657-84c1-4dfe-a30c-f4b97236a57a','NEW','INTAKE','telegram_daemon',NULL,'2026-04-06T19:17:56.134Z');
INSERT INTO state_transitions VALUES(3,'2c5e3f5e-465a-4b1d-8d0d-58bfd6382068','INTAKE','IN_PROGRESS','ai_router',NULL,'2026-04-06T19:18:01.791Z');
INSERT INTO state_transitions VALUES(4,'2c5e3f5e-465a-4b1d-8d0d-58bfd6382068','IN_PROGRESS','RESULT_READY','ai_router',NULL,'2026-04-06T19:18:05.582Z');
INSERT INTO state_transitions VALUES(5,'2c5e3f5e-465a-4b1d-8d0d-58bfd6382068','RESULT_READY','AWAITING_CONFIRMATION','task_worker',NULL,'2026-04-06T19:18:06.452Z');
INSERT INTO state_transitions VALUES(6,'99fd2657-84c1-4dfe-a30c-f4b97236a57a','INTAKE','IN_PROGRESS','ai_router',NULL,'2026-04-06T19:18:07.512Z');
INSERT INTO state_transitions VALUES(7,'99fd2657-84c1-4dfe-a30c-f4b97236a57a','IN_PROGRESS','RESULT_READY','ai_router',NULL,'2026-04-06T19:18:10.122Z');
INSERT INTO state_transitions VALUES(8,'99fd2657-84c1-4dfe-a30c-f4b97236a57a','RESULT_READY','AWAITING_CONFIRMATION','task_worker',NULL,'2026-04-06T19:18:11.457Z');
CREATE TABLE context_sessions (
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
CREATE TABLE pinned_messages (
    id TEXT PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    topic_id INTEGER,
    message_id INTEGER NOT NULL,
    task_id TEXT,
    label TEXT,
    content TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE agent_executions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    event TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE leads_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    raw_text TEXT,
    volume TEXT,
    location TEXT,
    phone TEXT,
    budget TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE automation_rules (
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
CREATE TABLE automation_events (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'done',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE followup_state (
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
CREATE TABLE memory_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    topic_id    INTEGER,
    role        TEXT NOT NULL DEFAULT 'user',
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
INSERT INTO memory_log VALUES(1,-1003725299009,NULL,'user','Есть кто живой нет?','2026-04-06T22:18:05Z');
INSERT INTO memory_log VALUES(2,-1003725299009,NULL,'assistant','Живой: я, DeepSeek. Оркестр из нейросетей отсутствует.','2026-04-06T22:18:05Z');
INSERT INTO memory_log VALUES(3,-1003725299009,NULL,'user','тест','2026-04-06T22:18:10Z');
INSERT INTO memory_log VALUES(4,-1003725299009,NULL,'assistant','Тест пройден.','2026-04-06T22:18:10Z');
CREATE TABLE reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    topic_id    INTEGER,
    text        TEXT NOT NULL,
    done        INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);
CREATE TABLE cognitive_journal(id INTEGER PRIMARY KEY, chat_id INTEGER, entry_type TEXT, content TEXT, content_norm TEXT, file_meta TEXT, file_meta_norm TEXT, created_at TEXT);
CREATE TABLE file_registry(id INTEGER PRIMARY KEY, chat_id INTEGER, path TEXT UNIQUE, filename TEXT, filename_norm TEXT, suffix TEXT, extracted_text TEXT, extracted_text_norm TEXT, file_mtime REAL, indexed_at TEXT);
INSERT INTO file_registry VALUES(1,-1003725299009,'/root/AI_ORCHESTRA/telegram/1888.ogg','1888.ogg','1888.ogg','.ogg','','',1775503065.87523293,'2026-04-06T19:18:07.278727');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('state_transitions',8);
INSERT INTO sqlite_sequence VALUES('memory_log',4);
CREATE INDEX idx_tasks_state ON tasks(state);
CREATE INDEX idx_tasks_chat_topic ON tasks(chat_id, topic_id, created_at);
CREATE INDEX idx_tasks_priority ON tasks(state, priority, created_at);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_artifacts_task_id ON artifacts(task_id);
CREATE INDEX idx_artifacts_status ON artifacts(processing_status);
CREATE INDEX idx_state_transitions_task ON state_transitions(task_id);
CREATE UNIQUE INDEX idx_ctx_chat_topic
ON context_sessions(chat_id, COALESCE(topic_id, -1));
CREATE INDEX idx_automation_rules_active
ON automation_rules(is_active, type, next_run_at);
CREATE INDEX idx_automation_events_rule
ON automation_events(rule_id, created_at);
CREATE INDEX idx_followup_due
ON followup_state(followup_required, status, followup_deadline);
CREATE INDEX idx_memory_chat
ON memory_log(chat_id, topic_id, created_at);
CREATE INDEX idx_reminders_done
ON reminders(done, created_at);
COMMIT;
