"use client";

import { Chess } from "chess.js";

type Props = {
  game: Chess;
};

export default function PositionPanel({ game }: Props) {
  const turn =
    game.turn() === "w"
      ? "White"
      : "Black";


  const moveNumber = game.moveNumber();


  const status = game.isCheckmate()
    ? "Checkmate"
    : game.isCheck()
    ? "Check"
    : game.isDraw()
    ? "Draw"
    : "Normal";


  return (
    <div className="rounded bg-gray-900 p-4 text-white">

      <h2 className="mb-4 text-lg font-semibold">
        Position
      </h2>


      <div className="flex flex-col gap-2 text-sm">

        <div>
          Turn:
          <span className="ml-2 font-bold">
            {turn}
          </span>
        </div>


        <div>
          Move:
          <span className="ml-2 font-bold">
            {moveNumber}
          </span>
        </div>


        <div>
          Status:
          <span className="ml-2 font-bold">
            {status}
          </span>
        </div>


      </div>

    </div>
  );
}