"use client";

import { createClient } from "./lib/supabase/client";

export default function Home() {
  const supabase = createClient();

  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
  };
  

  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="mb-6 text-4xl font-bold">
          TaskFlow
        </h1>

        <button
          onClick={handleGoogleLogin}
          className="rounded-lg border px-6 py-3"
        >
          Continue with Google
        </button>
      </div>
    </main>
  );
}