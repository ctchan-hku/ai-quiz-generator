interface BattleModeSwitchProps {
  checked: boolean;
  onCheckedChange: (next: boolean) => void;
  disabled?: boolean;
  /** Associates the switch with visible label copy for accessibility. */
  labelledBy?: string;
}

/** Accessible toggle styled as an on/off switch (`role="switch"`). */
export function BattleModeSwitch({
  checked,
  onCheckedChange,
  disabled,
  labelledBy,
}: BattleModeSwitchProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-labelledby={labelledBy}
      disabled={disabled}
      onClick={() => onCheckedChange(!checked)}
      className={[
        "relative inline-flex h-9 w-[3.5rem] shrink-0 rounded-full transition-colors motion-reduce:transition-none focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-background)] disabled:pointer-events-none disabled:opacity-50",
        checked ? "bg-[var(--color-primary)]" : "bg-[rgb(30_41_59/0.22)]",
      ].join(" ")}
    >
      <span className="sr-only">
        {checked ? "Battle mode on" : "Battle mode off"}
      </span>
      <span
        aria-hidden
        className={[
          "pointer-events-none absolute left-1 top-1 block size-7 rounded-full bg-white shadow-md transition-transform motion-reduce:transition-none",
          checked ? "translate-x-[1.25rem]" : "translate-x-0",
        ].join(" ")}
      />
    </button>
  );
}
