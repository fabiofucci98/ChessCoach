"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { listGames, getBadMoves, getSyncStatus, type BadMove } from "@/lib/api";
import PuzzleTrainer from "@/components/chess/PuzzleTrainer";
import PlayVsStockfish from "@/components/chess/PlayVsStockfish";
import Settings from "@/components/chess/Settings";

type Tab = "play" | "review" | "settings";

export default function Home() {
  const { user, token, isLoading, logout } = useAuth();
  const router = useRouter();

  const [mounted, setMounted] = useState(false);
  const [tab, setTab] = useState<Tab>("play");
  const [gameCount, setGameCount] = useState(0);
  const [badMoves, setBadMoves] = useState<BadMove[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => setMounted(true), []);

  const loadData = useCallback(async () => {
    if (!token) return;
    try {
      const games = await listGames(token, 50);
      setGameCount(games.length);
      const data = await getBadMoves(token, 500);
      setBadMoves(data.bad_moves);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    loadData();
  }, [token, loadData]);

  // Poll sync status globally to update stats live while syncing
  useEffect(() => {
    if (!token) return;
    const interval = setInterval(async () => {
      try {
        const status = await getSyncStatus(token);
        if (status.running) {
          loadData();
        }
      } catch {
        // silent
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [token, loadData]);

  useEffect(() => {
    if (!token || !user?.chess_com_username) return;
    const interval = setInterval(async () => {
      try {
        await loadData();
      } catch {
        // silent
      }
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [token, user?.chess_com_username, loadData]);

  if (isLoading || !mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-neutral-900 text-white">
        <div className="animate-pulse text-3xl">♟ ChessCoach</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-neutral-900 text-white">
        <h1 className="text-4xl font-bold">♟ ChessCoach</h1>
        <p className="text-gray-400">Your personal chess analysis coach</p>
        <button
          onClick={() => router.push("/login")}
          className="rounded bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-500"
        >
          Login / Register
        </button>
      </div>
    );
  }

  const repeatedMistakes = badMoves.filter((bm) => bm.counter >= 2).length;

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: "play", label: "Play", icon: "🎮" },
    { id: "review", label: "Review", icon: "🧩" },
    { id: "settings", label: "Settings", icon: "⚙️" },
  ];

  return (
    <main className="min-h-screen bg-neutral-900 text-white">
      <header className="border-b border-neutral-800 bg-neutral-900 px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <h1 className="text-xl font-bold">♟ ChessCoach</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">@{user.username}</span>
            <button onClick={logout} className="rounded bg-neutral-800 px-3 py-1.5 text-sm hover:bg-neutral-700">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-5xl p-6">
        {error && <div className="mb-4 rounded bg-red-900/50 p-3 text-red-200">{error}</div>}

        {/* Stats row */}
        <div className="mb-6 grid grid-cols-3 gap-4">
          <div className="rounded border border-neutral-800 bg-neutral-800/50 p-4 text-center">
            <div className="text-2xl font-bold">{gameCount}</div>
            <div className="text-xs text-gray-400">Games Analyzed</div>
          </div>
          <div className="rounded border border-neutral-800 bg-neutral-800/50 p-4 text-center">
            <div className="text-2xl font-bold">{badMoves.length}</div>
            <div className="text-xs text-gray-400">Mistakes Found</div>
          </div>
          <div className="rounded border border-neutral-800 bg-neutral-800/50 p-4 text-center">
            <div className="text-2xl font-bold">{repeatedMistakes}</div>
            <div className="text-xs text-gray-400">Repeated Mistakes</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-neutral-800">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`rounded-t px-4 py-2 text-sm font-semibold transition ${
                tab === t.id
                  ? "border-b-2 border-blue-500 bg-neutral-800/50 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {tab === "play" && <PlayVsStockfish />}
        {tab === "review" && <PuzzleTrainer />}
        {tab === "settings" && <Settings onDataChanged={loadData} />}
      </div>
    </main>
  );
}