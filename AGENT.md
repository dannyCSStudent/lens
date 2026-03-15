# LENS – AI Development Guide

This document provides architectural context for AI coding agents working on the LENS repository.

Agents MUST read this file before making any code changes.

If uncertain about a change, agents must ask for clarification rather than modifying existing systems.


---

# Critical Safety Rules

AI agents must follow these rules at all times.

Agents MUST NOT:

- delete existing files
- remove existing database columns
- rewrite working systems
- refactor large portions of the codebase
- remove services or routes that are already implemented

Agents MAY:

- extend existing services
- add new fields to models
- add new services
- add migrations
- add new endpoints

All work must be **incremental upgrades to the current architecture**.

Never destroy working functionality.

---

# Project Overview

LENS is an **evidence-based discourse platform**.

The goal is to structure claims and evidence so information can be evaluated transparently.

The system does not enforce a single truth authority.

Instead it provides **structured intelligence signals** derived from evidence.

Core philosophy:

Speech is free.  
Evidence accumulates.  
Confidence emerges from data.

---

# Core Content Types

Every post must be one of three types:

### Expression

Opinions or beliefs.

Characteristics:

- never subject to verification
- cannot receive evidence

---

### Claim

A factual assertion.

Characteristics:

- can receive supporting or contradicting evidence
- evidence contributes to confidence metrics

---

### Investigation

Open-ended inquiry.

Characteristics:

- designed to accumulate evidence
- evolves over time

---

# Evidence System

Evidence is structured data, not a comment.

Each evidence item contains:

- id
- post_id
- submitted_by
- evidence_type (link, document, image, quote)
- source_description
- direction (supports | contradicts)
- source_url
- archived_content
- content_hash
- tampered flag
- credibility_score

Evidence rules:

- Evidence cannot be deleted
- Evidence is immutable once created
- Evidence must be archived for integrity
- Source content must be hashed

Evidence integrity is critical to the system.

---

# Intelligence Layer

The platform includes analytical systems that operate on evidence.

These systems DO NOT declare absolute truth.

They provide **confidence signals derived from evidence patterns**.

Current systems include:

### Evidence Credibility Engine

Calculates credibility_score based on:

- evidence weight
- source reputation
- tamper status

---

### Truth Aggregation Engine

Computes truth_score for each claim based on:

supporting evidence  
vs  
contradicting evidence

---

### Source Reputation Intelligence

Tracks historical performance of sources.

Metrics include:

- citation_count
- credibility_history
- tamper_events
- reputation_score

---

### Narrative Detection Engine

Detects clusters of claims sharing similar evidence sources.

Outputs:

- narrative_cluster_id
- narrative_risk_score

---

### Claim Clustering Engine

Groups semantically similar claims.

Fields:

- claim_cluster_id
- claim_similarity_score

---

### Evidence Discovery Agents

Automated agents may investigate claims by:

- searching external sources
- discovering supporting or contradicting evidence
- attaching evidence automatically

Agents must operate through the service layer.

---

# Feed Design

The main feed must remain chronological.

Sorting modes allowed:

- latest
- evidence_activity

The system must not implement:

- virality ranking
- engagement amplification
- follower boosting

---

# Backend Architecture

Location:

apps/api

Stack:

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic migrations

Important directories:

app/api/routes  
API endpoints

app/api/schemas  
Pydantic schemas

app/core/models  
Database models

app/services  
Business logic layer

New functionality should be implemented in **services first**.

---

# Database Rules

Primary entities:

users  
posts  
evidence  
sources  
replies  
reports  
moderation_actions  

Constraints:

- posts should not be hard deleted
- evidence must remain immutable
- moderation logs must be immutable

---

# API Design Rules

Write endpoints require authentication.

Responses must be JSON.

Pagination must use cursor pagination.

All sco
