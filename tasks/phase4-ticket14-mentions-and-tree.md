# Phase 4 – Mention Detection & Reply Tree Serialization

## Description

Parse @mentions, create mention notifications, and optimize reply tree serialization to avoid N+1 queries.

## Affected Backend Files

- apps/api/app/services/mention_service.py
- apps/api/app/api/deps/reply_tree.py
- apps/api/app/services/notification_service.py

## Affected Frontend Files

- None

## Database Changes

Add `reply_mentions` junction table linking replies to mentioned users.

## API Endpoints

- POST /replies

## Acceptance Criteria

- Mentions captured from reply bodies and deduped
- Notifications emitted via service
- Reply serializer batches children to stay within query limits

## Test Requirements

- Parser unit tests for mention extraction
- Integration test ensuring notification enqueued when user mentioned

