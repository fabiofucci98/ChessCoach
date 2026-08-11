import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import PuzzleTrainer from "@/components/chess/PuzzleTrainer";
import { getNextPuzzle } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  getNextPuzzle: vi.fn(),
  answerPuzzle: vi.fn(),
}));

vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({ token: "test-token" }),
}));

vi.mock("react-chessboard", () => ({
  Chessboard: () => <div data-testid="board" />,
}));

const getNextPuzzleMock = getNextPuzzle as unknown as ReturnType<typeof vi.fn>;

describe("PuzzleTrainer", () => {
  it("shows an empty-state message when there are no puzzles", async () => {
    getNextPuzzleMock.mockResolvedValue(null);
    render(<PuzzleTrainer />);
    await waitFor(() =>
      expect(screen.getByText(/No puzzles available/i)).toBeInTheDocument()
    );
  });

  it("renders a fetched puzzle with a board", async () => {
    getNextPuzzleMock.mockResolvedValue({
      id: "p1",
      fen_before: "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
      best_move: "Qh5",
      move_played: "Nf3",
      move_number: 3,
      counter: 2,
      evaluation_before: 0.3,
      evaluation_after: 0.3,
      repetitions: 0,
      interval: 0,
      next_review_at: null,
    });
    render(<PuzzleTrainer />);
    await waitFor(() => expect(screen.getByText(/times/i)).toBeInTheDocument());
    expect(screen.getByTestId("board")).toBeInTheDocument();
  });
});
