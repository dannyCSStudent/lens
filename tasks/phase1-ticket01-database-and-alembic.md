# Phase 1 – Stand Up Database + Alembic Baseline

## Description

Configure the async SQLAlchemy engine/session management and align Alembic's environment + baseline migration so the API can boot with a healthy database lifecycle in all environments.

## Affected Backend Files

- apps/api/app/core/database.py
- apps/api/alembic/env.py
- apps/api/alembic/versions/bdceba147cf0_initial.py

## Affected Frontend Files

- None

## Database Changes

Ensure the baseline migration creates required extensions (uuid-ossp), timestamps, and Alembic metadata so subsequent migrations run without manual tweaks.

## API Endpoints

- None

## Acceptance Criteria

- `alembic upgrade head` succeeds on a fresh database and can downgrade back to base
- FastAPI boots locally and `/health` returns 200 while the DB is reachable
- Database connection failures surface a clear log error without crashing the app

## Test Requirements

- Integration test or script that runs `alembic upgrade head` against a test database
- Smoke test covering `/health` in both healthy and forced-failure DB scenarios

