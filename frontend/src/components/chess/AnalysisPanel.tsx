"use client";

type Props = {
  evaluation: number | null;
  bestMove: string | null;
  message: string | null;
  loading: boolean;
};


export default function AnalysisPanel({
  evaluation,
  bestMove,
  message,
  loading,
}: Props) {

  return (
    <div className="rounded bg-gray-900 p-4 text-white">

      <h2 className="mb-4 text-lg font-semibold">
        Engine Analysis
      </h2>


      {loading ? (
        <p>
          Analyzing position...
        </p>
      ) : (
        <div className="flex flex-col gap-2">

          <div>
            Evaluation:
            <b className="ml-2">
              {evaluation ?? "-"}
            </b>
          </div>


          <div>
            Best move:
            <b className="ml-2">
              {bestMove ?? "-"}
            </b>
          </div>


          <p className="text-gray-400">
            {message}
          </p>

        </div>
      )}

    </div>
  );
}