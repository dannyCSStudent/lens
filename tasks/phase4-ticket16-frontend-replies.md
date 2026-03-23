# Phase 4 – Frontend Threaded Replies UI

## Description

Build nested reply list with expand/collapse, inline composer per depth, and rate-limit messaging.

## Affected Backend Files

- None

## Affected Frontend Files

- apps/web/src/app/posts/[id]/page.tsx
- apps/web/src/app/components/ReplyList.tsx
- apps/web/src/app/components/ReplyComposer.tsx
- apps/web/src/app/services/replies.ts

## Database Changes

None

## API Endpoints

- GET /posts/{id}/replies
- POST /replies

## Acceptance Criteria

- Replies render in correct hierarchy
- Composer disables once depth limit reached
- Rate-limit errors surface inline

## Test Requirements

- Component tests for tree rendering
- E2E posting nested reply

