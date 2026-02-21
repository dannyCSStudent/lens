import { apiFetch } from "../lib/api";

export async function likePost(postId: string) {
  return apiFetch(`/likes/posts/${postId}`, {
    method: "POST",
  });
}

export async function unlikePost(postId: string) {
  return apiFetch(`/likes/posts/${postId}`, {
    method: "DELETE",
  });
}
