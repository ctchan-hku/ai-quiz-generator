const DEFAULT_SCROLL_DURATION_MS = 280;

function easeInOutCubic(progress: number): number {
  return progress < 0.5
    ? 4 * progress * progress * progress
    : 1 - Math.pow(-2 * progress + 2, 3) / 2;
}

function nearestScrollTargetY(
  element: HTMLElement,
  topOffset: number,
): number | null {
  const rect = element.getBoundingClientRect();
  const visibleTop = topOffset;
  const visibleBottom = window.innerHeight;

  if (rect.top >= visibleTop && rect.bottom <= visibleBottom) {
    return null;
  }

  if (rect.top < visibleTop) {
    return window.scrollY + rect.top - topOffset;
  }

  if (rect.height > visibleBottom - visibleTop) {
    return window.scrollY + rect.top - topOffset;
  }

  return window.scrollY + rect.bottom - visibleBottom;
}

function smoothScrollToY(targetY: number, durationMs: number): () => void {
  const startY = window.scrollY;
  const distance = targetY - startY;

  if (Math.abs(distance) < 1) {
    return () => {};
  }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    window.scrollTo(0, targetY);
    return () => {};
  }

  const startTime = performance.now();
  let frameId = 0;

  function step(currentTime: number) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / durationMs, 1);
    window.scrollTo(0, startY + distance * easeInOutCubic(progress));

    if (progress < 1) {
      frameId = requestAnimationFrame(step);
    }
  }

  frameId = requestAnimationFrame(step);

  return () => {
    cancelAnimationFrame(frameId);
  };
}

export function smoothScrollToNearest(
  element: HTMLElement,
  topOffset: number,
  durationMs = DEFAULT_SCROLL_DURATION_MS,
): () => void {
  const targetY = nearestScrollTargetY(element, topOffset);

  if (targetY === null) {
    return () => {};
  }

  return smoothScrollToY(targetY, durationMs);
}
