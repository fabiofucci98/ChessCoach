"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { syncGames, getSyncStatus, type SyncStatus } from "@/lib/api";

export default function Settings({ onDataChanged }: { onDataChanged: () => void }) {
  const { user, token, updateChessComUsername, updateSyncLimit } = useAuth();
  const [chessComUsername, setChessComUsername] = useState("");
  const [syncLimit, setSyncLimit] = useState(50);
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (user?.chess_com_username) setChessComUsername(user.chess_com_username);
    if (user?.sync_limit) setSyncLimit(user.sync_limit);
  }, [user]);

  // Poll sync status on mount and while syncing
  useEffect(() => {
    if (!token) return;
    let interval: ReturnType<typeof setInterval> | null = null;

    const poll = async () => {
      try {
        const status = await getSyncStatus(token);
        setSyncStatus(status);
        setSyncing(status.running);
        if (!status.running && status.progress === 100) {
          onDataChanged();
        }
      } catch {
        // silent
      }
    };

    poll();
    interval = setInterval(poll, 1000);
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [token, onDataChanged]);

  const handleSaveUsername = async () => {
    if (!chessComUsername.trim()) return;
    setError(null);
    setSuccess(null);
    try {
      await updateChessComUsername(chessComUsername.trim());
      setSuccess("Chess.com username updated!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update username");
    }
  };

  const handleSaveLimit = async () => {
    if (syncLimit < 1 || syncLimit > 500) {
      setError("Games to analyze must be between 1 and 500");
      return;
    }
    setError(null);
    setSuccess(null);
    try {
      await updateSyncLimit(syncLimit);
      setSuccess("Games to analyze updated!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update sync limit");
    }
  };

  const handleSync = async () => {
    if (!token) return;
    setSyncing(true);
    setError(null);
    setSuccess(null);
    setSyncStatus({ running: true, progress: 5, current_game: 0, total_games: 0, message: "Starting sync..." });
    try {
      await syncGames(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sync games");
      setSyncing(false);
    }
  };

  return (
    <section className="rounded border border-neutral-800 bg-neutral-800/50 p-4">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-400">⚙️ Settings</h2>

      {error && <div className="mb-4 rounded bg-red-900/50 p-3 text-red-200">{error}</div>}
      {success && <div className="mb-4 rounded bg-green-900/50 p-3 text-green-200">{success}</div>}

      <div className="mb-6">
        <label className="mb-1 block text-xs text-gray-400">Chess.com username</label>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Chess.com username"
            value={chessComUsername}
            onChange={(e) => setChessComUsername(e.target.value)}
            className="flex-1 rounded bg-neutral-700 px-3 py-2 text-sm"
          />
          <button onClick={handleSaveUsername} className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500">
            Save
          </button>
        </div>
      </div>

      <div className="mb-6">
        <label className="mb-1 block text-xs text-gray-400">Games to analyze</label>
        <div className="flex gap-2">
          <input
            type="number"
            min={1}
            max={500}
            value={syncLimit}
            onChange={(e) => setSyncLimit(parseInt(e.target.value) || 50)}
            className="w-32 rounded bg-neutral-700 px-3 py-2 text-sm"
          />
          <button onClick={handleSaveLimit} className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500">
            Save
          </button>
        </div>
        <p className="mt-1 text-xs text-gray-500">How many recent games to fetch and analyze from chess.com.</p>
      </div>

      <div className="mb-4">
        <button
          onClick={handleSync}
          disabled={syncing || !user?.chess_com_username}
          className="rounded bg-green-600 px-4 py-2 text-sm font-semibold hover:bg-green-500 disabled:opacity-50"
        >
          {syncing ? "Syncing..." : "Sync Now"}
        </button>
        {!user?.chess_com_username && (
          <p className="mt-2 text-xs text-gray-400">Set your chess.com username to start syncing games.</p>
        )}
      </div>

      {syncStatus && (
        <div className="mb-4">
          <div className="mb-1 flex items-center justify-between text-xs text-gray-400">
            <span>{syncStatus.message}</span>
            <span>{syncStatus.progress}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded bg-neutral-700">
            <div
              className="h-full bg-green-500 transition-all duration-500"
              style={{ width: `${syncStatus.progress}%` }}
            />
          </div>
          {syncStatus.running && syncStatus.total_games > 0 && (
            <p className="mt-1 text-xs text-gray-500">
              Analyzing game {syncStatus.current_game}/{syncStatus.total_games}
            </p>
          )}
        </div>
      )}

      {user?.chess_com_username && (
        <p className="mt-2 text-xs text-green-400">🔄 Auto-sync enabled — new games pulled automatically every 5 min.</p>
      )}
    </section>
  );
}