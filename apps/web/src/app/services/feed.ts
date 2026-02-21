import { apiFetch } from "../lib/api";
import type { PostCard } from "@repo/contracts";

export type FeedMode = "latest" | "trending";

export type FeedResponse = {
  items: PostCard[];
  next_cursor: string | null;
};

export async function getFeed(
  mode: FeedMode,
  limit = 20,
  cursor?: string
): Promise<FeedResponse> {
  const query = new URLSearchParams({
    mode,
    limit: String(limit),
  });

  if (cursor) {
    query.append("cursor", cursor);
  }

  return apiFetch(`/posts/feed?${query.toString()}`);
}
