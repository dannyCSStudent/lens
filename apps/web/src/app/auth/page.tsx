"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

type Mode = "login" | "signup";

export default function AuthPage() {
  const router = useRouter();

  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const [needsVerification, setNeedsVerification] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown <= 0) return;

    const timer = setTimeout(() => {
      setCooldown((prev) => prev - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [cooldown]);


  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    const endpoint =
      mode === "login"
        ? "http://localhost:8000/auth/login"
        : "http://localhost:8000/auth/register";

    const payload =
      mode === "login"
        ? { email, password }
        : { email, username, password };

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // 🔐 REQUIRED
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        if (Array.isArray(data.detail)) {
          setError(
            data.detail
              .map((err: { msg: string }) => err.msg)
              .join(", ")
          );
        } else {
          const message = data.detail || "Authentication failed";

          setError(message);

          // Detect unverified email error from backend
          if (
            mode === "login" &&
            typeof message === "string" &&
            message.toLowerCase().includes("not verified")
          ) {
            setNeedsVerification(true);
          } else {
            setNeedsVerification(false);
          }
        }
        return;
      }

      // =========================
      // LOGIN FLOW (Cookie-Based)
      // =========================
      if (mode === "login") {
        if (res.ok) {
          router.push("/");
          return;
        } else {
          setError("Login failed.");
          return;
        }
      }


      // =========================
      // SIGNUP FLOW
      // =========================
      if (mode === "signup") {
        setSuccess(
          "Account created successfully. Please check your email to verify your account before logging in."
        );

        // Clear fields
        setEmail("");
        setUsername("");
        setPassword("");

        // Switch back to login mode
        setMode("login");
      }
    } catch (err) {
      console.error(err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleResendVerification() {
    if (!email) return;

    setResendLoading(true);

    try {
      const res = await fetch(
        "http://localhost:8000/auth/resend-verification",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        }
      );

      await res.json();

      setSuccess(
        "If an account exists, a verification email has been sent."
      );
      setCooldown(60); // start 60 second cooldown
    } catch (err) {
      console.error(err);
      setError("Failed to resend verification email.");
    } finally {
      setResendLoading(false);
    }
  }


  return (
    <main className="relative flex items-center justify-center min-h-screen bg-black text-white overflow-hidden">
      <div className="relative z-10 backdrop-blur-xl bg-white/5 border border-white/10 p-10 rounded-3xl w-105 shadow-2xl">
        <h1 className="text-3xl font-semibold mb-6 text-center">
          {mode === "login" ? "Welcome Back" : "Create Account"}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-5">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full p-3 rounded-xl bg-white/10 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          {mode === "signup" && (
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full p-3 rounded-xl bg-white/10 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          )}

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full p-3 rounded-xl bg-white/10 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          {error && (
            <div className="text-red-400 text-sm space-y-2">
              <div>{error}</div>

              {needsVerification && (
                <button
                  type="button"
                  onClick={handleResendVerification}
                  disabled={resendLoading || cooldown > 0}
                  className="text-purple-400 underline text-sm hover:text-purple-300 disabled:opacity-50"
                >
                  {resendLoading
                    ? "Sending..."
                    : cooldown > 0
                    ? `Resend available in ${cooldown}s`
                    : "Resend verification email"}
                </button>
              )}

            </div>
          )}

          {success && (
            <div className="text-green-400 text-sm">{success}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full p-3 rounded-xl bg-linear-to-r from-purple-600 to-blue-600 hover:opacity-90 transition font-medium disabled:opacity-50"
          >
            {loading
              ? "Processing..."
              : mode === "login"
              ? "Login"
              : "Sign Up"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-400">
          {mode === "login"
            ? "No account?"
            : "Already have an account?"}

          <button
            onClick={() => {
              setMode(mode === "login" ? "signup" : "login");
              setError("");
              setSuccess("");
            }}
            className="ml-2 text-white underline"
          >
            {mode === "login" ? "Sign Up" : "Login"}
          </button>
        </div>
      </div>
    </main>
  );
}
