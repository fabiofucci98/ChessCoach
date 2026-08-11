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
  const [reviewPause, setReviewPause] = useState(false);
  const [pendingContinue, setPendingContinue] = useState<{ fen: string; uci: string } | null>(null);

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
    setReviewPause(false);
    setPendingContinue(null);
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

  function continueGame() {
    const pending = pendingContinue;
    setPendingContinue(null);
    setReviewPause(false);
    if (!pending || !pending.uci) return;
    const sf = new Chess(pending.fen);
    try {
      sf.move({ from: pending.uci.slice(0, 2), to: pending.uci.slice(2, 4), promotion: "q" });
      setBoard(sf);
      setLastMove(`${sf.history().slice(-1)[0] ?? ""} (Stockfish)`);
      if (sf.isCheckmate()) {
        setMessage("😵 Checkmate — Stockfish wins.");
        setType("bad");
      } else if (sf.isStalemate() || sf.isDraw()) {
        setMessage("🤝 Draw.");
        setType("info");
      }
    } catch {
      // ignore invalid Stockfish reply
    }
  }

  async function evaluateMove(fen: string, fenBefore: string) {
    try {
      if (!token) {
        setMessage("Login to get angry coach feedback!");
        setType("info");
      } else {
        const r = await playMove(token, fen, fenBefore);
        setEvalScore(r.evaluation);

        // Flagged mistake -> pause the game and offer to review instead of continuing
        if (r.is_mistake) {
          const level =
            r.mistake_level === "blunder"
              ? "Blunder"
              : r.mistake_level === "mistake"
              ? "Mistake"
              : "Inaccuracy";
          setMessage(`${level}: ${r.message} Best move: ${r.best_move ?? "N/A"}`);
          setType(r.repeated_mistake ? "angry" : "bad");
          setPendingContinue(r.stockfish_uci ? { fen, uci: r.stockfish_uci } : null);
          setReviewPause(true);
          setThinking(false);
          return;
        }

        // Good move: positive feedback, then Stockfish replies
        setMessage(r.message);
        setType("good");

        if (r.stockfish_uci) {
          const sf = new Chess(fen);
          try {
            sf.move({ from: r.stockfish_uci.slice(0, 2), to: r.stockfish_uci.slice(2, 4), promotion: "q" });
            setBoard(sf);
            setLastMove(`${sf.history().slice(-1)[0] ?? ""} (Stockfish)`);
            if (sf.isCheckmate()) {
              setMessage("😵 Checkmate — Stockfish wins.");
              setType("bad");
            } else if (sf.isStalemate() || sf.isDraw()) {
              setMessage("🤝 Draw.");
              setType("info");
            }
          } catch {
            // ignore invalid Stockfish reply
          }
        } else {
          // No reply (e.g. the player's move ended the game by checkmate)
          const c = new Chess(fen);
          if (c.isCheckmate()) {
            setMessage("🏆 Checkmate — you win! Well played!");
            setType("good");
          } else if (c.isStalemate() || c.isDraw()) {
            setMessage("🤝 Draw.");
            setType("info");
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
    if (thinking || reviewPause) return false;
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

    // The player's move ends the game by checkmate -> they win
    if (copy.isCheckmate()) {
      setMessage("🏆 Checkmate — you win! Well played!");
      setType("good");
      return true;
    }

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

      {reviewPause && (
        <button
          onClick={continueGame}
          className="mt-2 rounded bg-blue-600 px-3 py-1.5 text-xs font-semibold hover:bg-blue-500"
        >
          ▶ Continue playing
        </button>
      )}

      {type === "angry" && (
        <p className="mt-2 text-xs text-red-400">
          💡 Tip: Review your mistakes in the Review Mistakes section!
        </p>
      )}
    </section>
  );
}