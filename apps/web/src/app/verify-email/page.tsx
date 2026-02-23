"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

type Status = "loading" | "success" | "error";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const token = searchParams.get("token");

  const [status, setStatus] = useState<Status>(
    token ? "loading" : "error"
  );
  const [message, setMessage] = useState(
    token ? "" : "Invalid verification link."
  );

  useEffect(() => {
    if (!token) return; // Already handled via initial state

    let isMounted = true;

    async function verify() {
      try {
        const res = await fetch(
          "http://localhost:8000/auth/verify-email",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
          }
        );

        const data = await res.json();

        if (!isMounted) return;

        if (!res.ok) {
          if (Array.isArray(data.detail)) {
            setMessage(
              (data.detail as { msg?: string }[])
                .map((e) => e.msg ?? "")
                .filter(Boolean)
                .join(", ") || "Verification failed."
            );
          } else {
            setMessage(data.detail || "Verification failed.");
          }
          setStatus("error");
          return;
        }

        setMessage("Your email has been verified successfully!");
        setStatus("success");

        setTimeout(() => {
          router.push("/auth");
        }, 2500);
      } catch {
        if (!isMounted) return;
        setMessage("Network error. Please try again.");
        setStatus("error");
      }
    }

    verify();

    return () => {
      isMounted = false;
    };
  }, [token, router]);

  return (
    <main className="flex items-center justify-center min-h-screen bg-black text-white">
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 p-10 rounded-3xl w-105 shadow-2xl text-center">
        {status === "loading" && (
          <>
            <h1 className="text-2xl font-semibold mb-4">
              Verifying your email...
            </h1>
            <p className="text-gray-400 text-sm">
              Please wait while we confirm your account.
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <h1 className="text-2xl font-semibold text-green-400 mb-4">
              Email Verified 🎉
            </h1>
            <p className="text-gray-300 text-sm mb-6">{message}</p>
            <p className="text-gray-500 text-xs">
              Redirecting to login...
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <h1 className="text-2xl font-semibold text-red-400 mb-4">
              Verification Failed
            </h1>
            <p className="text-gray-300 text-sm mb-6">{message}</p>
            <button
              onClick={() => router.push("/auth")}
              className="w-full p-3 rounded-xl bg-linear-to-r from-purple-600 to-blue-600 hover:opacity-90 transition font-medium"
            >
              Back to Login
            </button>
          </>
        )}
      </div>
    </main>
  );
}
