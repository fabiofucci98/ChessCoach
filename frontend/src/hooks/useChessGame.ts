"use client";

import { Chess } from "chess.js";
import { useState } from "react";

export function useChessGame() {
  const [game, setGame] = useState(new Chess());
  const [history, setHistory] = useState<string[]>([]);
  const [currentMove, setCurrentMove] = useState(0);

  function loadPosition(input: string) {
    try {
      const chess = new Chess();

      if (input.includes("/") && input.split(" ").length === 6) {
        // FEN
        chess.load(input);
        setHistory([]);
        setCurrentMove(0);
      } else {
        // PGN
        chess.loadPgn(input);

        const moves = chess.history();

        setHistory(moves);
        setCurrentMove(moves.length);
      }

      setGame(chess);

    } catch (error) {
      console.error("Invalid chess input", error);
    }
  }


  function goToMove(moveNumber: number) {
    if (history.length === 0) return;

    const chess = new Chess();

    for (let i = 0; i < moveNumber; i++) {
      chess.move(history[i]);
    }

    setGame(chess);
    setCurrentMove(moveNumber);
  }


  function nextMove() {
    if (currentMove < history.length) {
      goToMove(currentMove + 1);
    }
  }


  function previousMove() {
    if (currentMove > 0) {
      goToMove(currentMove - 1);
    }
  }


  function reset() {
    setGame(new Chess());
    setHistory([]);
    setCurrentMove(0);
  }

function updateGame(chess: Chess) {
  setGame(chess);
  setHistory(chess.history());
  setCurrentMove(chess.history().length);
}
  return {
    game,
    history,
    currentMove,
    loadPosition,
    goToMove,
    nextMove,
    previousMove,
    reset,
    updateGame
  };
}