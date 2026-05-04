const usdBudgetFormat = Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

/** Formats backend `cost_usd` for display and export (estimate). */
export function formatEstimatedCostUsd(costUsd: number): string {
  return usdBudgetFormat.format(costUsd);
}
