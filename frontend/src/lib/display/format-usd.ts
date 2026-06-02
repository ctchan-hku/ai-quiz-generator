const LOCALE = "en-US";

export function formatEstimatedCostUsd(costUsd: number): string {
  return new Intl.NumberFormat(LOCALE, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 6,
  }).format(costUsd);
}
