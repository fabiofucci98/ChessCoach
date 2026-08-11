"use client";

type Props = {
  onPrevious: () => void;
  onNext: () => void;
  onReset: () => void;
  onFlip: () => void;
};

export default function ChessControls({
  onPrevious,
  onNext,
  onReset,
  onFlip,
}: Props) {
  return (
    <div className="flex flex-wrap gap-3">
      <button
        onClick={onPrevious}
        className="rounded bg-gray-700 px-4 py-2 text-white"
      >
        ◀ Previous
      </button>

      <button
        onClick={onNext}
        className="rounded bg-gray-700 px-4 py-2 text-white"
      >
        Next ▶
      </button>

      <button
        onClick={onReset}
        className="rounded bg-gray-700 px-4 py-2 text-white"
      >
        Reset
      </button>

      <button
        onClick={onFlip}
        className="rounded bg-gray-700 px-4 py-2 text-white"
      >
        Flip
      </button>
    </div>
  );
}