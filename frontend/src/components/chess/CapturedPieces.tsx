"use client";

import { Chess } from "chess.js";

type Props = {
  game: Chess;
};

const initialPieces = {
  w: {
    p: 8,
    n: 2,
    b: 2,
    r: 2,
    q: 1,
    k: 1,
  },
  b: {
    p: 8,
    n: 2,
    b: 2,
    r: 2,
    q: 1,
    k: 1,
  },
};


const symbols = {
  w: {
    p: "♟",
    n: "♞",
    b: "♝",
    r: "♜",
    q: "♛",
    k: "♚",
  },
  b: {
    p: "♙",
    n: "♘",
    b: "♗",
    r: "♖",
    q: "♕",
    k: "♔",
  },
};


export default function CapturedPieces({ game }: Props) {

  const board = game.board();

  const remaining = {
    w: { ...initialPieces.w },
    b: { ...initialPieces.b },
  };


  board.flat().forEach((piece) => {
    if (!piece) return;

    remaining[piece.color][piece.type]--;
  });


  function renderCaptured(color: "w" | "b") {
    const captured = [];

    for (const piece of Object.keys(
      remaining[color]
    ) as Array<keyof typeof remaining.w>) {

      for (
        let i = 0;
        i < remaining[color][piece];
        i++
      ) {
        captured.push(
          symbols[color][piece]
        );
      }
    }

    return captured.join(" ");
  }


  return (
    <div className="rounded bg-gray-900 p-4 text-white">

      <h2 className="mb-3 font-semibold">
        Captured
      </h2>


      <div>
        White:
        <span className="ml-2">
          {renderCaptured("w")}
        </span>
      </div>


      <div>
        Black:
        <span className="ml-2">
          {renderCaptured("b")}
        </span>
      </div>

    </div>
  );
}