// packages/contracts/src/types.ts

import {
  PostType,
  ConfidenceState,
  ContentStatus,
} from './enums';

export interface UserPublic {
  id: string;
  username: string;
  display_name: string | null;
  bio: string | null;
}

export interface PostCard {
  id: string;
  post_type: PostType;
  title: string;
  author: UserPublic;
  created_at: string;
  evidence_count: number;
  confidence_state: ConfidenceState;
  status: ContentStatus;
}

export interface PostDetail extends PostCard {
  body: string;
}
