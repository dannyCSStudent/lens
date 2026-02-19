const API_URL = "http://localhost:8000";

export async function apiFetch(
  endpoint: string,
  options?: RequestInit
) {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error("API error");
  }

  return res.json();
}
