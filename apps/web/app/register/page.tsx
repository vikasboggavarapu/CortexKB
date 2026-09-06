"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const { register, login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, password);
      await login(email, password);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to register");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="card-brand w-full max-w-sm p-8">
        <div className="brand-mark mb-5" />
        <h1 className="mb-1 text-2xl font-semibold">Create an account</h1>
        <p className="mb-6 text-sm text-brand-mauve">
          Upload documents, then query and chat with them.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-brand"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="password" className="text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              maxLength={128}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-brand"
            />
            <span className="text-xs text-brand-mauve">At least 8 characters.</span>
          </div>
          {error && (
            <p className="rounded-md bg-brand-coral/10 px-3 py-2 text-sm text-brand-rust">
              {error}
            </p>
          )}
          <button type="submit" disabled={submitting} className="btn-brand mt-2 w-full">
            {submitting ? "Creating account…" : "Register"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-brand-mauve">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-brand-coral hover:text-brand-rust">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
