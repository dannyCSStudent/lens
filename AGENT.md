# LENS – Codex Development Guide

This document provides architectural context for AI coding agents working on the LENS repository.

Agents should read this file before making code changes.

---

# Project Overview

LENS is a free-speech-first social platform designed to separate **expression from factual claims** and allow evidence to accumulate without algorithmic amplification.

The system does NOT determine truth.

Instead, it structures discourse so that evidence can accumulate transparently.

Core design philosophy:

Speech is free.  
Confidence is earned.  
Truth is never decreed.

---

# Core Platform Concepts

Every post must be one of three types:

### Expression
Opinions or beliefs.

Characteristics:
- never subject to verification
- cannot receive evidence

---

### Claim
A statement asserting factual reality.

Characteristics:
- can receive supporting or contradicting evidence
- evidence contributes to the post’s confidence indicator

---

### Investigation
An evolving inquiry.

Characteristics:
- designed to accumulate evidence
- open-ended

---

# Evidence System

Evidence is NOT a comment.

Evidence is a structured record.

Each evidence item contains:

- evidence_id
- associated post_id
- submitted_by user
- evidence_type (link, document, image, quote)
- source_description
- direction (supports | contradicts)
- timestamp

Important rules:

- Evidence cannot be deleted by users
- Evidence cannot be downvoted
- Evidence exists independently of replies
- Evidence is immutable once created

Evidence integrity is critical to the platform.

---

# Confidence Indicator

The system never determines truth.

Instead it reflects the **state of evidence**.

Rules:

No evidence
→ "No community review yet"

Evidence from one direction
→ "Community evidence present"

Evidence from both directions
→ "Conflicting evidence present"

There are:

- no scores
- no voting
- no ranking

Confidence state must always be **computed server-side**.

---

# Feed Design Rules

The feed must always remain:

Chronological.

Forbidden features:

- trending
- ranking
- virality algorithms
- engagement scoring
- follower amplification

This rule is **non-negotiable**.

---

# Moderation Model

Moderation is intentionally minimal.

Allowed moderator actions:

- remove illegal content
- lock threads when legally required

Not allowed:

- shadow banning
- silent reach suppression
- hidden enforcement

All moderation actions must be:

- public
- immutable
- logged
- linked to moderator accounts

Moderation logs must never be editable.

---

# Monorepo Architecture

The repository uses a **pnpm + turbo monorepo structure**.

Top-level structure:

apps/
packages/
docker/

---

# Backend API

Location:

apps/api

Stack:

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic migrations
- JWT authentication

Key directories:

app/api/routes
API endpoints

app/api/schemas
Pydantic request/response models

app/core/models
Database models

app/services
Business logic layer

Agents should implement new features in the **service layer** first, not directly in routes.

---

# Database

Primary entities:

users  
posts  
evidence  
replies  
reports  
moderation_actions  
notifications  

Constraints:

Posts are never deleted.
Status changes instead.

Evidence cannot be deleted.

Moderation logs must be immutable.

Counters must be enforced at database level.

---

# Web Application

Location:

apps/web

Stack:

- Next.js
- TypeScript
- App Router
- Tailwind CSS

Responsibilities:

- authentication
- feed display
- post creation
- evidence submission
- threaded discussions
- moderation transparency views

The web app should remain **stateless where possible** and rely on the API.

---

# Shared Packages

packages/contracts

Shared TypeScript types between frontend and backend.

packages/ui

Shared UI components.

packages/rules

Contains logic related to confidence indicators.

---

# API Design Rules

All write operations require authentication.

Public read endpoints are allowed where safe.

Responses must be JSON.

Pagination must use cursor-based pagination.

Confidence states must always be computed server-side.

Never trust client-provided counters.

---

# Security Principles

Authentication:

JWT access tokens

Refresh tokens stored in database.

Security features implemented:

- login detection
- security events
- rate limiting
- geoip tracking

Security services are located in:

app/services/security_service.py

Agents must not weaken security systems.

---

# Development Commands

Start backend:

cd apps/api
uvicorn app.main:app --reload

Run migrations:

alembic upgrade head

Run web app:

cd apps/web
pnpm dev

Run tests:

pytest

---

# Coding Guidelines

Backend:

- use async FastAPI routes
- use Pydantic schemas
- keep business logic inside services
- maintain database integrity constraints

Frontend:

- prefer server components
- keep API calls centralized in services layer

---

# Non-Negotiable Design Rules

Agents must never introduce:

- ranking algorithms
- engagement scoring
- truth labels
- vote systems for truth determination
- evidence deletion

The system must remain structurally neutral.

---

# Current Development Focus

High priority improvements:

1. Evidence submission UX
2. Confidence indicator computation
3. Moderation transparency tools
4. Reply threading improvements
5. Feed performance and pagination
6. Notification system stability

---

# How AI Agents Should Work

When implementing new features:

1. update database model if required
2. create service-layer logic
3. expose API endpoint
4. update schemas
5. update web UI if needed

Agents should prefer **small incremental PRs** over large changes.

---

End of AGENT.md
