# Phase 2 – Frontend Feed & Composer

## Description

Implement feed UI with mode toggle, infinite scroll, and a post composer for all post types with optimistic create.

## Affected Backend Files

- None

## Affected Frontend Files

- apps/web/src/app/page.tsx
- apps/web/src/app/services/feed.ts
- apps/web/src/app/services/posts.ts
- apps/web/src/app/components/PostComposer.tsx

## Database Changes

None

## API Endpoints

- GET /posts/feed
- POST /posts

## Acceptance Criteria

- Switching modes reloads feed cleanly
- Composer enforces post type helper text and length validation
- Optimistic insert replaced with server payload once POST finishes

## Test Requirements

- Cypress/Playwright scenario covering create + feed refresh
- Unit tests for composer validation state machine

