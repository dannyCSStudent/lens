# LENS

![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-MVP%20Active-orange)

**Speech is free. Confidence is earned. Truth is never decreed.**

LENS is a minimal, legally-safe, free-speech-first social platform designed to separate **expression from factual claims** and allow evidence to accumulate without censorship.

The MVP demonstrates that disagreement can be organized instead of amplified — and that claims can be examined without declaring them “true” or “false.”

---

## Purpose

Most platforms optimize for engagement.  
LENS optimizes for clarity.

We remove amplification incentives and replace them with structure:

- Expression is protected.
- Claims can receive evidence.
- Investigations evolve over time.
- Moderation is transparent.
- No algorithm decides truth.

---

# Core Principles (Non-Negotiable)

- No shadow banning  
- No forced truth labels  
- No engagement-maximizing algorithms  
- Clear separation between speech and factual claims  
- All moderation actions are public and appealable  
- Free speech does not include illegal content  

---

# MVP Overview (v0.1)

## User Roles

### Regular User
- Create posts
- Attach evidence
- Participate in threaded discussions

### Moderator (Limited Scope)
- Remove illegal content only
- Lock threads when legally required
- All actions publicly logged
- Cannot suppress reach or hide posts silently

---

# The Three Post Types

Users must explicitly choose one when posting:

## 1. Expression
Opinions, beliefs, experiences.  
Never subject to verification.

Label: `Expression`

---

## 2. Claim
Statements asserting factual reality.  
Can receive supporting or contradicting evidence.

Label: `Claim`

---

## 3. Investigation
Open-ended inquiry designed to evolve.  
Acts as a container for accumulating evidence.

Label: `Investigation`

---

# Evidence System (Core Differentiator)

Evidence is **not** a comment.

Each evidence item contains:

- Evidence ID
- Associated Post
- Submitted by user
- Evidence Type (link, document, image, quote)
- Source description (required)
- Direction: `supports` or `contradicts`
- Timestamp

Evidence:
- Cannot be downvoted into invisibility
- Cannot be deleted by users
- Exists independently of discussion

---

# Confidence Indicator (Computed, Not Voted)

The system does **not** determine truth.

It only reflects evidence state:

| Condition | Displayed State |
|------------|----------------|
| No evidence | No community review yet |
| One direction only | Community evidence present |
| Both directions | Conflicting evidence present |

No scores.  
No AI judgment.  
No “true/false” labels.

---

# Feed Design

- Chronological only
- Filterable by post type
- No trending
- No virality ranking
- No engagement optimization
- No follower-based amplification

Removing amplification removes manipulation incentives.

---

# Moderation Model

### Allowed
- Remove illegal content
- Lock threads if legally required

### Not Allowed
- Hiding posts silently
- Reach suppression
- Secret enforcement

All moderation actions are:
- Public
- Logged
- Immutable
- Linked to a moderator account
- Appeal-enabled

Reports never auto-hide content.

---

# Tech Stack

## Backend
- FastAPI
- PostgreSQL
- JWT authentication
- Cursor-based pagination
- Server-computed derived states

## Frontend (Planned)
- Web-first (Next.js recommended)
- Mobile-ready APIs
- No ranking assumptions

---

# Database Schema (MVP)

Core tables:

- `users`
- `posts`
- `evidence`
- `replies`
- `moderation_actions`
- `reports`
- `notifications`

Design constraints:

- Posts are never deleted (status change only)
- Evidence cannot be user-deleted
- Moderation logs are immutable
- Counters enforced with DB-level constraints
- No hidden ranking signals stored

---

# API Design Principles

- RESTful JSON
- Auth required for all write actions
- Public read access where safe
- Server computes confidence states
- No client-side trust

## Core Endpoints

- POST /auth/register
- POST /auth/login

- GET /posts
- POST /posts

- POST /posts/{id}/evidence
- POST /posts/{id}/replies

- POST /moderation/actions
- GET /moderation/log

---

# Abuse & Threat Mitigation (MVP Hardening)

## Mass Disinformation Flooding
- Chronological feed only
- Rate limits
- Claims without evidence remain labeled “No review”

## Bot Amplification
- No engagement ranking
- Public activity logs
- Manual abnormal behavior review

## Weaponized Reporting
- Reports never auto-hide content
- Moderator review required
- Public moderation actions

## Moderator Abuse
- Immutable moderation logs
- Visible enforcement
- No silent controls

---

# Build Order

## Phase 1 — Foundation
- Auth
- Database
- User model

## Phase 2 — Core Content
- Posts
- Feed
- Post detail

## Phase 3 — Context Layer
- Evidence system
- Confidence computation

## Phase 4 — Discourse
- Threaded replies
- Rate limits

## Phase 5 — Safety
- Moderation actions
- Reporting system
- Public moderation log

## Phase 6 — Polish
- Notifications
- Performance
- Pagination optimization

---

# Out of Scope (MVP)

- AI fact-checking  
- Reputation scoring  
- Recommendation algorithms  
- Monetization  
- Ads  
- Mobile apps  
- Federation  

---

# Design Outcome

LENS discourages manipulation not by suppression —  
but by removing amplification incentives.

It does not declare truth.

It structures disagreement.

---

# Project Status

🚧 Active MVP Development  
Invite-only initial launch (50–100 users)  
Manual moderation during early phase  

---

If you're interested in contributing, reviewing architecture, or helping shape a platform designed around structural clarity rather than engagement incentives — we welcome thoughtful collaboration.

---

# Quick Start (Local Development)

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/lens.git
cd lens
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

pip install -r requirements.txt

Create a .env file in the project root:
DATABASE_URL=postgresql://user:password@localhost:5432/lens
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
```

**Speech is free. Confidence is earned. Truth is never decreed.**

