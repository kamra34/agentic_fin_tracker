-- Migration: Admin session/activity audit (login history + activity log)
-- Date: 2026-06-23
-- Description: Adds users.last_login plus two audit tables:
--   login_events    - one row per login attempt (success/failure), with IP + device.
--   activity_events - one row per authenticated API request (approximates navigation).
-- Viewed by superusers only via /api/admin/*. Nullable/additive; safe to re-run.
--
-- IMPORTANT: Run on the Railway production DB BEFORE deploying the new backend — the
--   models SELECT these tables/columns, so they must exist first.

ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

CREATE TABLE IF NOT EXISTS login_events (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id),
    email       VARCHAR(255),
    success     BOOLEAN NOT NULL DEFAULT TRUE,
    ip_address  VARCHAR(64),
    user_agent  VARCHAR(512),
    device      VARCHAR(128),
    created_at  TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);
CREATE INDEX IF NOT EXISTS ix_login_events_user_id    ON login_events (user_id);
CREATE INDEX IF NOT EXISTS ix_login_events_created_at ON login_events (created_at);

CREATE TABLE IF NOT EXISTS activity_events (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER REFERENCES users(id),
    method       VARCHAR(10),
    path         VARCHAR(255),
    status_code  INTEGER,
    ip_address   VARCHAR(64),
    created_at   TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);
CREATE INDEX IF NOT EXISTS ix_activity_events_user_id    ON activity_events (user_id);
CREATE INDEX IF NOT EXISTS ix_activity_events_created_at ON activity_events (created_at);

COMMENT ON TABLE login_events    IS 'Login attempts (admin session/security log).';
COMMENT ON TABLE activity_events IS 'Authenticated API requests per user (admin activity log).';
