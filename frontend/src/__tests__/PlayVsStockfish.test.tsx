import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import PlayVsStockfish from "@/components/chess/PlayVsStockfish";
import { playMove } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  playMove: vi.fn(),
}));

vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({ token: "test-token" }),
}));

// Expose the board's onPieceDrop handler for testing
let onDrop: ((args: { sourceSquare: string; targetSquare: string }) => boolean) | undefined;
vi.mock("react-chessboard", () => ({
  Chessboard: (props: any) => {
    onDrop = props.options.onPieceDrop;
    return <div data-testid="board" />;
  },
}));

const playMoveMock = playMove as unknown as ReturnType<typeof vi.fn>;

describe("PlayVsStockfish", () => {
  it("renders title and board", () => {
    render(<PlayVsStockfish />);
    expect(screen.getByText(/Play vs Stockfish/i)).toBeInTheDocument();
    expect(screen.getByTestId("board")).toBeInTheDocument();
  });

  it("rejects moving the opponent's pieces on your turn", () => {
    render(<PlayVsStockfish />);
    // White to move; a black move must be rejected
    const rejected = onDrop!({ sourceSquare: "e7", targetSquare: "e5" });
    expect(rejected).toBe(false);
  });

  it("sends a valid move and shows a good-move message", async () => {
    playMoveMock.mockResolvedValue({
      evaluation: 0.3,
      best_move: "e5",
      uci_move: "e7e5",
      stockfish_move: "e5",
      stockfish_uci: "e7e5",
      is_mistake: false,
      mistake_level: null,
      repeated_mistake: false,
      repeated_count: 0,
      message: "✅ Nice move!",
    });

    render(<PlayVsStockfish />);
    const moved = onDrop!({ sourceSquare: "e2", targetSquare: "e4" });
    expect(moved).toBe(true);
    expect(playMoveMock).toHaveBeenCalled();
    await waitFor(() => expect(screen.getByText("✅ Nice move!")).toBeInTheDocument());
  });
});
