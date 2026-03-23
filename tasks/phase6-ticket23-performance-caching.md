# Phase 6 – Performance & Caching Pass

## Description

Introduce Redis-backed caching for feed queries, tune SQL, and offload heavy analytics to async tasks.

## Affected Backend Files

- apps/api/app/services/post_service.py
- apps/api/app/core/cache/redis.py
- apps/api/app/services/feed_cache.py
- apps/api/app/api/routes/posts.py

## Affected Frontend Files

- None

## Database Changes

Add covering indexes to `posts` (status, created_at, id) and `evidence` (post_id, created_at).

## API Endpoints

- GET /posts/feed
- GET /posts/{id}

## Acceptance Criteria

- Cache hit ratio logged and monitored
- Feed p95 latency meets target (< configured ms)
- Fallback path works when Redis unavailable

## Test Requirements

- Unit tests for cache decorator hit/miss
- Load/perf script comparison before vs after

