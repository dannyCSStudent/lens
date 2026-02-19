"use client";

import { useEffect, useState, useTransition } from "react";
import { getFeed } from "../app/services/feed";
import type { PostCard } from "@repo/contracts";



export default function Home() {
  
  const [posts, setPosts] = useState<PostCard[]>([]);
  const [mode, setMode] = useState<"latest" | "trending">("trending");
  const [isPending, startTransition] = useTransition();
  
  async function loadFeed(selectedMode: "latest" | "trending") {
    const data = await getFeed(selectedMode);
    setPosts(data);
  }
 
  useEffect(() => {
    loadFeed(mode);
  }, [mode]);


  function handleModeChange(newMode: "latest" | "trending") {
    setMode(newMode);

    startTransition(() => {
      loadFeed(newMode);
    });
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

      {isPending && <p>Loading...</p>}

      {posts.map((post) => (
        <div key={post.id} className="border p-4 mb-4 rounded-lg">
          <h2 className="text-xl font-bold">{post.title}</h2>
          <p className="text-sm text-gray-500">
            @{post.author.username}
          </p>
          <p className="text-sm mt-2">
            Evidence: {post.evidence_count}
          </p>
        </div>
      ))}
    </main>
  );
}
