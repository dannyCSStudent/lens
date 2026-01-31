// packages/contracts/src/enums.ts

export enum PostType {
  EXPRESSION = 'expression',
  CLAIM = 'claim',
  INVESTIGATION = 'investigation',
}

export enum EvidenceDirection {
  SUPPORTS = 'supports',
  CONTRADICTS = 'contradicts',
}

export enum ConfidenceState {
  NO_REVIEW = 'no_review',
  COMMUNITY_REVIEWED = 'community_reviewed',
  CONFLICTING_EVIDENCE = 'conflicting_evidence',
}

export enum ContentStatus {
  ACTIVE = 'active',
  LOCKED = 'locked',
  REMOVED_ILLEGAL = 'removed_illegal',
}

export enum ModerationActionType {
  REMOVED_ILLEGAL = 'removed_illegal',
  LOCKED = 'locked',
}

export enum UserStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
}
