# Phase 1 – User Model & Persistence Layer

## Description

Define the `users` table schema, ORM model, and helper repos with verification + security flags aligned to auth needs.

## Affected Backend Files

- apps/api/app/core/models/user.py
- apps/api/app/core/models/base.py
- apps/api/alembic/versions/xxxx_create_users.py

## Affected Frontend Files

- None

## Database Changes

New `users` table with UUID PK, unique indexes on email and username, password hash, verification + lockout fields, timestamps.

## API Endpoints

- None

## Acceptance Criteria

- Migration applies cleanly and enforces uniqueness on email/username
- Creating a `User` via SQLAlchemy sets sane defaults (verified false, no lockout)
- Duplicate emails rejected at DB level

## Test Requirements

- Model tests covering default values and constraints
- Migration test verifying uniqueness by attempting duplicate inserts

