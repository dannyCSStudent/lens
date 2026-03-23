# Phase 3 – Frontend Evidence Panel & Confidence Indicator

## Description

Add post detail page with evidence list, submission form, and visual confidence indicator legend.

## Affected Backend Files

- None

## Affected Frontend Files

- apps/web/src/app/posts/[id]/page.tsx
- apps/web/src/app/components/EvidencePanel.tsx
- apps/web/src/app/components/ConfidenceIndicator.tsx
- apps/web/src/app/services/evidence.ts

## Database Changes

None

## API Endpoints

- GET /posts/{id}
- GET /evidence/post/{post_id}
- POST /evidence

## Acceptance Criteria

- Confidence indicator text matches backend state
- Evidence submission validates required fields and refreshes list without full reload
- UI handles empty state and large evidence lists

## Test Requirements

- Component tests for indicator and panel
- E2E test adding evidence and seeing it appear

