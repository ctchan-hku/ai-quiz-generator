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
