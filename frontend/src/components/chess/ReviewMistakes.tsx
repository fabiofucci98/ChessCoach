"use client";

import { useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import type { BadMove } from "@/lib/api";

export default function ReviewMistakes({ badMoves }: { badMoves: BadMove[] }) {
  const [selected, setSelected] = useState<BadMove | null>(null);
  const sorted = [...badMoves].sort((a, b) => b.counter - a.counter);

  function gameFor(bm: BadMove) {
    try {
      return new Chess(bm.fen).fen();
    } catch {
      return "";
    }
  }

  if (sorted.length === 0) {
    return (
      <section className="rounded border border-neutral-800 bg-neutral-800/50 p-4">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
          📋 Review Mistakes
        </h2>
        <p className="text-sm text-gray-400">
          No bad moves yet. Sync chess.com games to get analysis!
        </p>
      </section>
    );
  }

  return (
    <section className="rounded border border-neutral-800 bg-neutral-800/50 p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
        📋 Review Mistakes
      </h2>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="flex max-h-[420px] flex-col gap-2 overflow-y-auto pr-1">
          {sorted.map((bm) => (
            <button
              key={bm.id}
              onClick={() => setSelected(bm)}
              className={`rounded p-3 text-left transition ${
                selected?.id === bm.id ? "bg-neutral-600/80 ring-1 ring-blue-500" : "bg-neutral-700/50 hover:bg-neutral-700"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm">
                  Move {bm.move_number}: <b className="text-red-400">{bm.move_played}</b>
                </span>
                <span className={`rounded px-2 py-0.5 text-xs font-bold ${bm.counter >= 3 ? "bg-red-900/70 text-red-200" : bm.counter === 2 ? "bg-orange-900/70 text-orange-200" : "bg-yellow-900/70 text-yellow-200"}`}>
                  ×{bm.counter}
                </span>
              </div>
              <div className="mt-1 flex items-center justify-between text-xs text-gray-400">
                <span>Best: <b className="text-green-400">{bm.best_move}</b></span>
                <span>{bm.evaluation_before.toFixed(1)} → {bm.evaluation_after.toFixed(1)}</span>
              </div>
              {bm.counter >= 3 && <p className="mt-1 text-xs font-semibold text-red-400">😠 You keep making this mistake!</p>}
            </button>
          ))}
        </div>
        <div className="flex flex-col gap-3">
          {selected ? (
            <>
              <div className="w-full max-w-[360px]">
                <Chessboard options={{ position: gameFor(selected), boardOrientation: "white" }} />
              </div>
              <div className="rounded bg-neutral-700/50 p-3 text-sm">
                <p>
                  You played <b className="text-red-400">{selected.move_played}</b>, best was{" "}
                  <b className="text-green-400">{selected.best_move}</b>.
                </p>
                <p className="mt-1 text-xs text-gray-400">
                  Eval: {selected.evaluation_before.toFixed(1)} → {selected.evaluation_after.toFixed(1)} ({selected.counter}×)
                </p>
              </div>
            </>
          ) : (
            <p className="text-sm text-gray-400">Select a mistake to see the position.</p>
          )}
        </div>
      </div>
    </section>
  );
}