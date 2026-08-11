"use client";

import { useState, useEffect, useCallback } from "react";
import { Chess } from "chess.js";
import { Chessboard, type PieceDropHandlerArgs } from "react-chessboard";
import { useAuth } from "@/lib/auth-context";
import { getNextPuzzle, answerPuzzle, type Puzzle, type PuzzleAnswer } from "@/lib/api";

export default function PuzzleTrainer() {
  const { token } = useAuth();
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null);
  const [board, setBoard] = useState<Chess | null>(null);
  const [orientation, setOrientation] = useState<"white" | "black">("white");
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<PuzzleAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [solved, setSolved] = useState(0);
  const [attempted, setAttempted] = useState(0);

  const loadPuzzle = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const p = await getNextPuzzle(token);
      setPuzzle(p);
      if (p) {
        const b = new Chess(p.fen_before);
        setBoard(b);
        setOrientation(b.turn() === "b" ? "black" : "white");
      } else {
        setBoard(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load puzzle");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadPuzzle();
  }, [loadPuzzle]);

  function onDrop({ sourceSquare, targetSquare }: PieceDropHandlerArgs): boolean {
    if (!board || !puzzle || result) return false;
    if (!targetSquare) return false;

    const copy = new Chess(board.fen());
    let move;
    try {
      move = copy.move({ from: sourceSquare, to: targetSquare, promotion: "q" });
    } catch {
      return false;
    }
    if (!move) return false;

    setBoard(copy);
    setAttempted((a) => a + 1);

    // Submit the answer
    if (token) {
      answerPuzzle(token, puzzle.id, move.san)
        .then((res) => {
          setResult(res);
          if (res.correct) setSolved((s) => s + 1);
        })
        .catch((err) => setError(err instanceof Error ? err.message : "Failed to submit answer"));
    }
    return true;
  }

  if (loading) {
    return (
      <section className="rounded border border-neutral-800 bg-neutral-800/50 p-4">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">🧩 Review Mistakes</h2>
        <p className="text-sm text-gray-400">Loading puzzle...</p>
      </section>
    );
  }

  if (!puzzle) {
    return (
      <section className="rounded border border-neutral-800 bg-neutral-800/50 p-4">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">🧩 Review Mistakes</h2>
        <p className="text-sm text-gray-400">
          No puzzles available yet. Sync your games and make the same mistake twice to get a puzzle!
        </p>
      </section>
    );
  }

  return (
    <section className="rounded border border-neutral-800 bg-neutral-800/50 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-400">🧩 Review Mistakes</h2>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>✅ {solved}/{attempted}</span>
          <span className="rounded bg-yellow-900/70 px-2 py-0.5 font-bold text-yellow-200">×{puzzle.counter}</span>
        </div>
      </div>

      <p className="mb-3 text-sm text-gray-300">
        You made this mistake <b className="text-red-400">{puzzle.counter} times</b>. Find the best move!
      </p>

      {board && (
        <div className="w-full max-w-[480px]">
          <Chessboard
            options={{
              position: board.fen(),
              onPieceDrop: onDrop,
              boardOrientation: orientation,
            }}
          />
        </div>
      )}

      {error && <p className="mt-3 rounded bg-red-900/50 p-2 text-sm text-red-200">{error}</p>}

      {result && (
        <div className={`mt-3 rounded p-3 text-sm ${result.correct ? "bg-green-900/50 text-green-200" : "bg-red-900/50 text-red-200"}`}>
          {result.correct ? (
            <p>✅ Correct! The best move was <b>{result.best_move}</b>.</p>
          ) : (
            <p>❌ Wrong. Best move was <b>{result.best_move}</b> (you played <b>{puzzle.move_played}</b>).</p>
          )}
          <p className="mt-1 text-xs opacity-80">
            Next review in {result.interval} day{result.interval === 1 ? "" : "s"}.
          </p>
          <button
            onClick={loadPuzzle}
            className="mt-2 rounded bg-neutral-700 px-3 py-1.5 text-xs hover:bg-neutral-600"
          >
            Next Puzzle →
          </button>
        </div>
      )}
    </section>
  );
}