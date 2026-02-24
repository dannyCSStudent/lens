const API_URL = "http://localhost:8000";

export async function apiFetch(
  endpoint: string,
  options?: RequestInit
) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    credentials: "include", // 🔐 send httpOnly cookies
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || "API error");
  }

  return res.json();
}
