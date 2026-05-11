import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

/** Shown inside each opponent tab — model identity and estimated cost live here only. */
export interface BattleOpponentSwitchItem {
  roleLabel: string;
  modelLabel: string;
  estimatedCostDisplay: string;
  wasTruncated?: boolean;
}

export interface BattleOpponentCarouselProps {
  leftTab: BattleOpponentSwitchItem;
  rightTab: BattleOpponentSwitchItem;
  leftPane: ReactNode;
  rightPane: ReactNode;
  onConfirmSelection: (side: "left" | "right") => void;
}

export function BattleOpponentCarousel({
  leftTab,
  rightTab,
  leftPane,
  rightPane,
  onConfirmSelection,
}: BattleOpponentCarouselProps) {
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const syncActiveFromScroll = useCallback(() => {
    const el = scrollerRef.current;
    if (!el || el.clientWidth === 0) return;
    const next = Math.min(
      1,
      Math.max(0, Math.round(el.scrollLeft / el.clientWidth)),
    );
    setActiveIndex((prev) => (prev === next ? prev : next));
  }, []);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    syncActiveFromScroll();
    el.addEventListener("scroll", syncActiveFromScroll, { passive: true });
    return () => {
      el.removeEventListener("scroll", syncActiveFromScroll);
    };
  }, [syncActiveFromScroll]);

  const goToSlide = useCallback((index: number) => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTo({
      left: index * el.clientWidth,
      behavior: "smooth",
    });
  }, []);

  function renderSwitchButton(
    tab: BattleOpponentSwitchItem,
    index: 0 | 1,
  ) {
    const isActive = activeIndex === index;
    return (
      <button
        type="button"
        role="tab"
        aria-selected={isActive}
        id={index === 0 ? "battle-tab-left" : "battle-tab-right"}
        tabIndex={isActive ? 0 : -1}
        className={`flex min-h-24 min-w-0 flex-1 flex-col gap-1 rounded-lg border px-3 py-2 text-left transition-colors ${
          isActive
            ? "border-[var(--color-primary)] bg-[var(--color-primary)]/10"
            : "border-[rgb(30_41_59/0.15)] bg-white/40 opacity-85"
        }`}
        onClick={() => goToSlide(index)}
      >
        <span className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-60">
          {tab.roleLabel}
        </span>
        <span className="line-clamp-2 text-sm font-medium leading-snug text-[var(--color-text)]">
          {tab.modelLabel}
        </span>
        <span className="mt-auto text-xs text-[var(--color-text)] opacity-75">
          {tab.estimatedCostDisplay}
        </span>
        {tab.wasTruncated ? (
          <span className="text-[0.65rem] italic text-[var(--color-text)] opacity-55">
            Source truncated
          </span>
        ) : null}
      </button>
    );
  }

  return (
    <div className="flex min-w-0 flex-col gap-3">
      <div className="flex gap-2" role="tablist" aria-label="Switch opponent">
        {renderSwitchButton(leftTab, 0)}
        {renderSwitchButton(rightTab, 1)}
      </div>

      <div
        ref={scrollerRef}
        className="-mx-1 flex w-full min-w-0 overflow-x-auto overflow-y-hidden scroll-smooth pb-1 [scrollbar-width:none] snap-x snap-mandatory [&::-webkit-scrollbar]:hidden"
        style={{ WebkitOverflowScrolling: "touch" }}
        aria-label="Swipe horizontally to compare quizzes"
      >
        <div
          className="w-full min-w-full shrink-0 snap-start snap-always px-1"
          role="tabpanel"
          aria-labelledby="battle-tab-left"
          id="battle-panel-left"
        >
          {leftPane}
        </div>
        <div
          className="w-full min-w-full shrink-0 snap-start snap-always px-1"
          role="tabpanel"
          aria-labelledby="battle-tab-right"
          id="battle-panel-right"
        >
          {rightPane}
        </div>
      </div>

      <button
        type="button"
        className="btn-primary w-full justify-center px-3 py-2 text-sm"
        onClick={() =>
          onConfirmSelection(activeIndex === 0 ? "left" : "right")
        }
      >
        Continue with selected model
      </button>
    </div>
  );
}
