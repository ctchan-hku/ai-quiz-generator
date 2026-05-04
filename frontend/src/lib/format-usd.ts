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

export function formatEstimatedCostUsd(costUsd: number): string {
  return formatUsdAmount(costUsd, 0, 6);
}

export function formatUsdPerM(value: number | null): string | null {
  if (value == null || !Number.isFinite(value)) {
    return null;
  }
  return `${formatUsdAmount(value, 0, 2)}/M`;
}
