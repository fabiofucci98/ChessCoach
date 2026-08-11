"use client";

type Props = {
  moves: string[];
  currentMove: number;
  onMoveClick: (index: number) => void;
};

export default function MoveHistory({
  moves,
  currentMove,
  onMoveClick,
}: Props) {

  const rows = [];

  for (let i = 0; i < moves.length; i += 2) {
    rows.push({
      number: i / 2 + 1,
      white: moves[i],
      black: moves[i + 1],
    });
  }


  return (
    <div className="rounded bg-gray-900 p-4 text-white">

      <div className="mb-3 grid grid-cols-3 text-sm text-gray-400">
        <span>Move</span>
        <span>White</span>
        <span>Black</span>
      </div>


      {rows.map((row) => {

        const whiteIndex = row.number * 2 - 2;
        const blackIndex = row.number * 2 - 1;


        return (
          <div
            key={row.number}
            className="grid grid-cols-3 gap-2 text-sm"
          >

            <span className="text-gray-400">
              {row.number}.
            </span>


            <button
              onClick={() => onMoveClick(whiteIndex + 1)}
              className={
                currentMove === whiteIndex + 1
                  ? "rounded bg-blue-600"
                  : "text-left"
              }
            >
              {row.white}
            </button>


            <button
              onClick={() =>
                row.black &&
                onMoveClick(blackIndex + 1)
              }
              className={
                currentMove === blackIndex + 1
                  ? "rounded bg-blue-600"
                  : "text-left"
              }
            >
              {row.black}
            </button>

          </div>
        );
      })}

    </div>
  );
}