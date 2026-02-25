const API_URL = "http://localhost:8000";

export async function apiFetch(
  endpoint: string,
  options?: RequestInit
) {
  let res = await fetch(`${API_URL}${endpoint}`, {
    credentials: "include",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (res.status === 401) {
    // attempt refresh
    const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });

    if (refreshRes.ok) {
      // retry original request
      res = await fetch(`${API_URL}${endpoint}`, {
        credentials: "include",
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
      });
    } else {
      window.location.href = "/auth";
      throw new Error("Session expired");
    }
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || "API error");
  }

  return res.json();
}
