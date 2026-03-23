# Phase 3 – Confidence State Computation

## Description

Compute truth_score/confidence_state whenever evidence changes and expose on feed + post responses.

## Affected Backend Files

- apps/api/app/services/truth_engine.py
- apps/api/app/services/evidence_weight.py
- apps/api/app/services/post_service.py
- apps/api/app/api/schemas/feed.py

## Affected Frontend Files

- None

## Database Changes

Add `truth_score` numeric column and `confidence_state` enum to `posts` with backfill script.

## API Endpoints

- GET /posts/feed
- GET /posts/{id}

## Acceptance Criteria

- Evidence insertion triggers recalculation via service
- State transitions follow defined table (no_review → evidence_present → conflicting)
- Feed + detail endpoints include new fields

## Test Requirements

- Truth engine unit tests covering weighting edge cases
- API regression verifying serialization of confidence fields

