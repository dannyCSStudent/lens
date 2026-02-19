import { apiFetch } from "../lib/api";

export type FeedMode = "latest" | "trending";

export async function getFeed(
  mode: FeedMode,
  limit = 20,
  offset = 0
) {
  return apiFetch(
    `/posts/feed?mode=${mode}&limit=${limit}&offset=${offset}`
  );
}
