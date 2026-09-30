"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/supabase/api";

type UserProfile = {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
};

export default function DashboardPage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await apiFetch("/api/auth/me");
        setUser(data.user);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Something went wrong"
        );
      }
    }

    loadUser();
  }, []);

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-red-500">{error}</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold">TaskFlow Dashboard</h1>

        <p className="mt-4">
          Logged in as: {user.email}
        </p>

        <p className="mt-2 text-sm text-gray-500">
          Backend authentication successful
        </p>
      </div>
    </main>
  );
}