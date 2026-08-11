import { describe, expect, it } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { Chess } from "chess.js";
import { useChessGame } from "@/hooks/useChessGame";

describe("useChessGame", () => {
  it("starts on the standard starting position with empty history", () => {
    const { result } = renderHook(() => useChessGame());
    expect(result.current.game.fen()).toBe(new Chess().fen());
    expect(result.current.history).toHaveLength(0);
  });

  it("loads a position from a FEN", () => {
    const { result } = renderHook(() => useChessGame());
    const fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";
    act(() => {
      result.current.loadPosition(fen);
    });
    expect(result.current.game.fen().startsWith("rnbqkbnr/pppppppp/8/8/4P3")).toBe(true);
  });

  it("loads a PGN and allows stepping through moves", () => {
    const { result } = renderHook(() => useChessGame());
    act(() => {
      result.current.loadPosition("1. e4 e5 2. Nf3 Nc6");
    });
    expect(result.current.history).toHaveLength(4);

    act(() => {
      result.current.goToMove(2);
    });
    expect(result.current.currentMove).toBe(2);

    act(() => {
      result.current.nextMove();
    });
    expect(result.current.currentMove).toBe(3);

    act(() => {
      result.current.previousMove();
    });
    expect(result.current.currentMove).toBe(2);

    act(() => {
      result.current.reset();
    });
    expect(result.current.history).toHaveLength(0);
    expect(result.current.currentMove).toBe(0);
  });
});
