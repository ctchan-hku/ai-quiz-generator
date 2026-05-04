const LOCALE = "en-US";

function formatUsdAmount(
  value: number,
  minimumFractionDigits: number,
  maximumFractionDigits: number,
): string {
  return new Intl.NumberFormat(LOCALE, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits,
    maximumFractionDigits,
  }).format(value);
}

/** Estimated full-quiz charge from backend (`cost_usd`) — UX: dollars + cents readability. */
export function formatEstimatedCostUsd(costUsd: number): string {
  return formatUsdAmount(costUsd, 2, 4);
}

/** USD per 1M tokens for model-board; ~3 significant figures, optional `/M` suffix elsewhere. */
export function formatUsdPerM(value: number | null): string | null {
  if (value == null || !Number.isFinite(value)) {
    return null;
  }
  const rounded = Number(value.toPrecision(3));
  return `${formatUsdAmount(rounded, 0, 6)}/M`;
}
