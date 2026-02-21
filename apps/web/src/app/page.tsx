"use client";

// web/src/app/page.tsx
import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { getFeed } from "../app/services/feed";
import type { PostCard } from "@repo/contracts";
import { likePost, unlikePost } from "./services/likes";

export default function Home() {
  const router = useRouter();

  const [posts, setPosts] = useState<PostCard[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [mode, setMode] = useState<"latest" | "trending">("trending");
  const [isPending, startTransition] = useTransition();
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  async function loadFeed(
    selectedMode: "latest" | "trending",
    selectedCursor?: string | null,
    append = false
  ) {
    try {
      const data = await getFeed(
        selectedMode,
        20,
        selectedCursor ?? undefined
      );

      setCursor(data.next_cursor);
      setHasMore(data.next_cursor !== null);

      if (append) {
        setPosts((prev) => [...prev, ...data.items]);
      } else {
        setPosts(data.items);
      }
    } finally {
      setIsInitialLoading(false);
    }
  }

  useEffect(() => {
    startTransition(() => {
      setPosts([]);
      setCursor(null);
      setHasMore(false);
      setIsInitialLoading(true);
      loadFeed(mode, null, false);
    });
  }, [mode]);

  function handleModeChange(newMode: "latest" | "trending") {
    setMode(newMode);
  }

  function handleLoadMore() {
    if (!hasMore || !cursor) return;

    startTransition(() => {
      loadFeed(mode, cursor, true);
    });
  }

  async function handleToggleLike(postId: string) {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    let wasLiked = false;

    // optimistic update
    setPosts((prev) =>
      prev.map((post) => {
        if (post.id !== postId) return post;

        const currentLiked = post.viewer_has_liked ?? false;
        const currentCount = post.like_count ?? 0;

        wasLiked = currentLiked;

        return {
          ...post,
          viewer_has_liked: !currentLiked,
          like_count: currentLiked
            ? currentCount - 1
            : currentCount + 1,
        };
      })
    );

    try {
      if (wasLiked) {
        await unlikePost(postId);
      } else {
        await likePost(postId);
      }
    } catch {
      // rollback on failure
      setPosts((prev) =>
        prev.map((post) => {
          if (post.id !== postId) return post;

          const currentCount = post.like_count ?? 0;

          return {
            ...post,
            viewer_has_liked: wasLiked,
            like_count: wasLiked
              ? currentCount + 1
              : currentCount - 1,
          };
        })
      );
    }
  }

  return (
    <main className="max-w-2xl mx-auto p-6">
      <div className="flex gap-4 mb-6">
        <button onClick={() => handleModeChange("latest")}>
          Latest
        </button>
        <button onClick={() => handleModeChange("trending")}>
          Trending
        </button>
      </div>

      {(isPending || isInitialLoading) && <p>Loading...</p>}

      {posts.map((post) => (
        <div key={post.id} className="border p-4 mb-4 rounded-lg">
          <h2 className="text-xl font-bold">{post.title}</h2>

          <p className="text-sm text-gray-500">
            @{post.author.username}
          </p>

          <p className="text-sm mt-2">
            Evidence: {post.evidence_count}
          </p>

          <button
            onClick={() => handleToggleLike(post.id)}
            className="mt-2 text-sm"
          >
            {post.viewer_has_liked ? "❤️" : "🤍"}{" "}
            {post.like_count ?? 0}
          </button>
        </div>
      ))}

      {hasMore && !isInitialLoading && (
        <button
          onClick={handleLoadMore}
          className="w-full border p-3 rounded-lg"
        >
          {isPending ? "Loading..." : "Load More"}
        </button>
      )}
      <button
        onClick={() => {
          localStorage.removeItem("access_token");
          window.location.href = "/login";
        }}
      >
        Logout
      </button>

    </main>
  );
}
