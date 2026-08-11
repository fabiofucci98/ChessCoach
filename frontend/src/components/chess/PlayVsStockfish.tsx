"use client";

import { useState } from "react";
import { Chess, type Square } from "chess.js";
import { Chessboard, type PieceDropHandlerArgs } from "react-chessboard";
import { useAuth } from "@/lib/auth-context";
import { playMove } from "@/lib/api";

export default function PlayVsStockfish() {
  const { token } = useAuth();
  const [board, setBoard] = useState(() => new Chess());
  const [playerColor, setPlayerColor] = useState<"white" | "black">("white");
  const [message, setMessage] = useState("Play your move...");
  const [type, setType] = useState<"info" | "good" | "bad" | "angry">("info");
  const [thinking, setThinking] = useState(false);
  const [lastMove, setLastMove] = useState<string | null>(null);
  const [evalScore, setEvalScore] = useState<number | null>(null);

  async function stockfishFirstMove() {
    if (!token) return;
    const startFen = new Chess().fen();
    try {
      const r = await playMove(token, startFen, startFen);
      if (r.stockfish_uci) {
        const sf = new Chess();
        sf.move({ from: r.stockfish_uci.slice(0, 2), to: r.stockfish_uci.slice(2, 4), promotion: "q" });
        setBoard(sf);
        setLastMove(`${sf.history().slice(-1)[0] ?? ""} (Stockfish)`);
        setMessage("Stockfish moved. Your turn!");
        setType("info");
      }
    } catch {
      // ignore
    } finally {
      setThinking(false);
    }
  }

  function startNewGame(color: "white" | "black") {
    setBoard(new Chess());
    setMessage("Game reset. Play your move...");
    setType("info");
    setLastMove(null);
    setEvalScore(null);
    setThinking(true);
    if (color === "black") {
      stockfishFirstMove();
    } else {
      setThinking(false);
    }
  }

  function resetGame() {
    startNewGame(playerColor);
  }

  function toggleColor() {
    const next: "white" | "black" = playerColor === "white" ? "black" : "white";
    setPlayerColor(next);
    startNewGame(next);
  }

  async function evaluateMove(fen: string, fenBefore: string) {
    try {
      if (!token) {
        setMessage("Login to get angry coach feedback!");
        setType("info");
      } else {
        const r = await playMove(token, fen, fenBefore);
        setEvalScore(r.evaluation);
        if (r.repeated_mistake && r.is_mistake) {
          setMessage(r.message);
          setType("angry");
        } else if (r.is_mistake) {
          setMessage(r.message);
          setType("bad");
        } else {
          setMessage(r.stockfish_move ? `${r.message}` : r.message);
          setType("good");
        }

        // Stockfish replies with its best move (applied to the position after the player's move)
        if (r.stockfish_uci) {
          const sf = new Chess(fen);
          try {
            sf.move({ from: r.stockfish_uci.slice(0, 2), to: r.stockfish_uci.slice(2, 4), promotion: "q" });
            setBoard(sf);
            setLastMove(`${sf.history().slice(-1)[0] ?? ""} (Stockfish)`);
            if (sf.isCheckmate()) {
              setMessage("🏆 Checkmate — you win! Well played!");
              setType("good");
            } else if (sf.isStalemate() || sf.isDraw()) {
              setMessage("🤝 Draw.");
              setType("info");
            }
          } catch {
            // ignore invalid Stockfish reply
          }
        }
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed");
      setType("bad");
    } finally {
      setThinking(false);
    }
  }

  function onDrop({ sourceSquare, targetSquare }: PieceDropHandlerArgs): boolean {
    if (thinking) return false;
    if (!targetSquare) return false;

    // Only the human player acts, and only on their own turn, with their own pieces
    const myColor: "w" | "b" = playerColor === "white" ? "w" : "b";
    if (board.turn() !== myColor) return false;
    const piece = board.get(sourceSquare as Square);
    if (!piece || piece.color !== myColor) return false;

    const before = board.fen();
    const copy = new Chess(board.fen());
    let move;
    try {
      move = copy.move({ from: sourceSquare, to: targetSquare, promotion: "q" });
    } catch {
      return false;
    }
    if (!move) return false;

    setBoard(copy);
    setLastMove(move.san);
    setThinking(true);
    evaluateMove(copy.fen(), before);
    return true;
  }

  const colors = {
    info: "bg-gray-800 text-gray-300",
    good: "bg-green-900/50 text-green-200",
    bad: "bg-red-900/50 text-red-200",
    angry: "bg-red-950/80 text-red-100 border border-red-700",
  };

  return (
    <section className="rounded border border-neutral-800 bg-neutral-800/50 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-400">
          🎮 Play vs Stockfish Coach
        </h2>
        <div className="flex gap-2">
          <button
            onClick={toggleColor}
            className="rounded bg-neutral-700 px-3 py-1.5 text-xs hover:bg-neutral-600"
          >
            {playerColor === "white" ? "♔ White" : "♚ Black"}
          </button>
          <button
            onClick={resetGame}
            className="rounded bg-neutral-700 px-3 py-1.5 text-xs hover:bg-neutral-600"
          >
            Reset
          </button>
        </div>
      </div>

      <div className="w-full max-w-[480px]">
        <Chessboard
          options={{
            position: board.fen(),
            onPieceDrop: onDrop,
            boardOrientation: playerColor,
          }}
        />
      </div>

      {evalScore !== null && (
        <p className="mt-2 text-xs text-gray-400">
          Evaluation: {evalScore >= 0 ? "+" : ""}
          {evalScore.toFixed(2)}
        </p>
      )}
      {lastMove && <p className="mt-1 text-xs text-gray-400">Your move: {lastMove}</p>}

      <div className={`mt-3 rounded p-3 text-sm ${colors[type]}`}>
        {thinking ? "🤔 Stockfish is thinking..." : message}
      </div>

      {type === "angry" && (
        <p className="mt-2 text-xs text-red-400">
          💡 Tip: Review your mistakes in the Review Mistakes section!
        </p>
      )}
    </section>
  );
}