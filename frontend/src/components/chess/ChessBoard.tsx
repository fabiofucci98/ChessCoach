"use client";

import { Chessboard, type PieceDropHandlerArgs } from "react-chessboard";
import { Chess } from "chess.js";
import { useState } from "react";

import PGNLoader from "./PGNLoader";
import MoveHistory from "./MoveHistory";
import ChessControls from "./ChessControls";
import AnalysisPanel from "./AnalysisPanel";
import PositionPanel from "./PositionPanel";
import { useChessGame } from "@/hooks/useChessGame";
import CapturedPieces from "./CapturedPieces";

import { analyzePosition } from "@/lib/api";
export default function ChessBoard() {
  const [orientation, setOrientation] = useState<"white" | "black">("white");

  const {
    game,
    history,
    currentMove,
    loadPosition,
    updateGame,
    goToMove,
    nextMove,
    previousMove,
    reset,
  } = useChessGame();


type Analysis = {
  evaluation: number | null;
  bestMove: string | null;
  message: string | null;
};


const [analysis, setAnalysis] = useState<Analysis>({
  evaluation: null,
  bestMove: null,
  message: null,
});


  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  async function handleAnalyze() {
    setLoadingAnalysis(true);

    try {
      const result = await analyzePosition(game.fen());

      setAnalysis({
        evaluation: result.evaluation,
        bestMove: result.best_move,
        message: "Stockfish analysis complete",
      });
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingAnalysis(false);
    }
  }

  function onDrop({
    sourceSquare,
    targetSquare,
  }: PieceDropHandlerArgs): boolean {
    if (!targetSquare) {
      return false;
    }

    const gameCopy = new Chess(game.fen());

    const move = gameCopy.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: "q",
    });

    if (!move) {
      return false;
    }

    updateGame(gameCopy);

    return true;
  }

  function flipBoard() {
    setOrientation((current) => (current === "white" ? "black" : "white"));
  }

  return (
    <div className="flex flex-col gap-6">
      <PGNLoader onLoadPGN={loadPosition} />

      <div className="w-full max-w-[600px]">
        <Chessboard
          options={{
            position: game.fen(),
            onPieceDrop: onDrop,
            boardOrientation: orientation,
          }}
        />
      </div>

      <ChessControls
        onPrevious={previousMove}
        onNext={nextMove}
        onReset={reset}
        onFlip={flipBoard}
      />
      <button
        onClick={handleAnalyze}
        className="rounded bg-blue-600 px-4 py-2 text-white"
      >
        Analyze Position
      </button>

      <MoveHistory
        moves={history}
        currentMove={currentMove}
        onMoveClick={goToMove}
      />

      <AnalysisPanel
        evaluation={analysis.evaluation}
        bestMove={analysis.bestMove}
        message={analysis.message}
        loading={loadingAnalysis}
      />
      <PositionPanel game={game} />
      <CapturedPieces game={game} />
      <div className="rounded bg-gray-900 p-3 text-xs text-gray-400 break-all">
        <strong>FEN:</strong>
        <br />
        {game.fen()}
      </div>
    </div>
  );
}
