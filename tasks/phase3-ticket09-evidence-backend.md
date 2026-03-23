# Phase 3 – Evidence Submission Backend

## Description

Allow attaching immutable evidence records with archival metadata and source linkage.

## Affected Backend Files

- apps/api/app/api/routes/evidence.py
- apps/api/app/api/schemas/evidence.py
- apps/api/app/core/models/evidence.py
- apps/api/app/services/evidence_service.py

## Affected Frontend Files

- None

## Database Changes

Create `evidence` table referencing posts and optional sources, storing direction, archive URL, content hash, credibility score.

## API Endpoints

- POST /evidence
- GET /evidence/post/{post_id}

## Acceptance Criteria

- Evidence records immutable once created
- API enforces required descriptions and direction
- Archive + hash recorded when source_url provided (failures logged but do not block)

## Test Requirements

- API tests for supports vs contradicts
- Attempting to update/delete evidence should fail
- Hashing mocked to assert persisted values

