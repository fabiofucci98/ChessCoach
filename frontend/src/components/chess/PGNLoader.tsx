"use client";

import { useState } from "react";

type Props = {
  onLoadPGN: (pgn: string) => void;
};

export default function PGNLoader({ onLoadPGN }: Props) {
  const [pgn, setPgn] = useState("");

  function load() {
    if (!pgn.trim()) return;

    onLoadPGN(pgn);
  }

  return (
    <div className="flex flex-col gap-3">
      <textarea
        value={pgn}
        onChange={(e) => setPgn(e.target.value)}
        placeholder="Paste PGN here..."
        className="h-40 rounded border p-3 text-black"
      />

      <button
        onClick={load}
        className="rounded bg-blue-600 px-4 py-2 text-white"
      >
        Load Game
      </button>
    </div>
  );
}