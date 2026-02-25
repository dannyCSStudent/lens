"use client";

import { useEffect, useState } from "react";

type Session = {
  id: string;
  device_name: string | null;
  ip_address: string | null;
  created_at: string;
  last_used_at: string | null;
  expires_at: string;
};

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [revoking, setRevoking] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadSessions() {
    try {
      setError(null);

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/sessions`,
        { credentials: "include" }
      );

      if (!res.ok) throw new Error();

      const data = await res.json();

      setSessions(data.sessions);
      setCurrentSessionId(data.current_session_id);
    } catch {
      setError("Could not load sessions.");
    } finally {
      setLoading(false);
    }
  }

  async function revokeSession(id: string) {
    try {
      setRevoking(id);

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/sessions/${id}`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );

      if (!res.ok) throw new Error();

      await loadSessions();
    } catch {
      alert("Failed to revoke session.");
    } finally {
      setRevoking(null);
    }
  }

  async function revokeAllOtherSessions() {
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/sessions/revoke-others`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );

      await loadSessions();
    } catch {
      alert("Failed to revoke sessions.");
    }
  }

  useEffect(() => {
    loadSessions();
  }, []);

  if (loading) return <p>Loading sessions...</p>;

  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-2">
        You&apos;re logged in on {sessions.length} device
        {sessions.length !== 1 ? "s" : ""}
      </h1>

      {sessions.length > 1 && (
        <button
          onClick={revokeAllOtherSessions}
          className="text-sm text-blue-600 mb-6"
        >
          Sign out of all other sessions
        </button>
      )}

      {error && (
        <p className="text-red-600 mb-4">{error}</p>
      )}

      <div className="space-y-4">
        {sessions.map((session) => {
          const isCurrent = session.id === currentSessionId;

          return (
            <div
              key={session.id}
              className={`border rounded-xl p-4 ${
                isCurrent ? "border-blue-500 bg-blue-50" : ""
              }`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-semibold">
                    {getDeviceLabel(session)}
                    {isCurrent && (
                      <span className="ml-2 text-xs text-blue-600">
                        (This device)
                      </span>
                    )}
                  </p>

                  <p className="text-sm text-gray-500">
                    IP: {session.ip_address ?? "Unknown"}
                  </p>

                  <p className="text-sm text-gray-500">
                    Created: {formatDate(session.created_at)}
                  </p>

                  <p className="text-sm text-gray-500">
                    Last used:{" "}
                    {session.last_used_at
                      ? formatDate(session.last_used_at)
                      : "—"}
                  </p>

                  <p className="text-sm text-gray-500">
                    Expires: {formatDate(session.expires_at)}
                  </p>
                </div>

                {!isCurrent && (
                  <button
                    disabled={revoking === session.id}
                    onClick={() => revokeSession(session.id)}
                    className="text-red-600 text-sm disabled:opacity-50"
                  >
                    {revoking === session.id
                      ? "Revoking..."
                      : "Revoke"}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </main>
  );
}

function formatDate(date: string) {
  return new Date(date).toLocaleString();
}

function getDeviceLabel(session: Session) {
  if (!session.device_name && !session.ip_address)
    return "Unknown Device";

  return session.device_name ?? "Web Session";
}
