interface BattleWinnerPanelProps {
  onPickWinner: (side: "left" | "right") => void;
}

export function BattleWinnerPanel({ onPickWinner }: BattleWinnerPanelProps) {
  return (
    <div className="card text-left">
      <h3 className="m-0 text-sm font-semibold text-[var(--color-text)]">
        Which quiz is better?
      </h3>
      <p className="mb-4 mt-2 text-xs leading-relaxed text-[var(--color-text)] opacity-80">
        Your choice sets the active quiz for “Current Quiz Actions” and
        refinements.
      </p>
      <div className="flex flex-col gap-2">
        <button
          type="button"
          className="btn-primary w-full justify-center px-3 py-2 text-sm"
          onClick={() => onPickWinner("left")}
        >
          Left Opponent wins
        </button>
        <button
          type="button"
          className="btn-primary w-full justify-center px-3 py-2 text-sm"
          onClick={() => onPickWinner("right")}
        >
          Right Opponent wins
        </button>
      </div>
    </div>
  );
}
