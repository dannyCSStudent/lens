# Phase 3 – Evidence Integrity & Source Intelligence

## Description

Wire archival fetcher, content hashing, integrity verifier, and source reputation updates after each submission.

## Affected Backend Files

- apps/api/app/services/archive_service.py
- apps/api/app/services/integrity_verifier.py
- apps/api/app/services/source_intelligence.py
- apps/api/app/services/credibility_engine.py

## Affected Frontend Files

- None

## Database Changes

Add `sources` table with reputation fields and link evidence rows; add tamper flags & timestamps on evidence.

## API Endpoints

- POST /evidence/verify-integrity

## Acceptance Criteria

- Integrity job iterates evidence and marks tampered items when hashes mismatch
- Source reputation recalculates per submission
- Archival failures logged but never crash background jobs

## Test Requirements

- Service tests stubbing HTTP fetch
- Scheduled task test verifying tamper flag toggles correctly

