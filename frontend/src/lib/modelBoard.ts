import type { ModelInfo } from "../types/api";

export type ModelSortDirection = "price_asc" | "price_desc";

/** Both input and output missing — listed after all priced models. */
export function isPricingUnavailable(m: ModelInfo): boolean {
  return m.price == null || (m.price.input == null && m.price.output == null);
}

function priceSortKey(m: ModelInfo): number {
  const normalizedInput = m.price?.input ?? Number.POSITIVE_INFINITY;
  const normalizedOutput = m.price?.output ?? Number.POSITIVE_INFINITY;
  return normalizedInput + normalizedOutput;
}

function compareLabelThenId(a: ModelInfo, b: ModelInfo): number {
  const byLabel = a.label.localeCompare(b.label);
  if (byLabel !== 0) {
    return byLabel;
  }
  return a.id.localeCompare(b.id);
}

export function sortedModels(
  models: ModelInfo[],
  direction: ModelSortDirection,
): ModelInfo[] {
  const priced: ModelInfo[] = [];
  const unpriced: ModelInfo[] = [];
  for (const m of models) {
    if (isPricingUnavailable(m)) {
      unpriced.push(m);
    } else {
      priced.push(m);
    }
  }

  priced.sort((a, b) => {
    let cmp = priceSortKey(a) - priceSortKey(b);
    if (direction === "price_desc") {
      cmp = -cmp;
    }
    if (cmp !== 0) {
      return cmp;
    }
    return compareLabelThenId(a, b);
  });

  unpriced.sort(compareLabelThenId);

  return [...priced, ...unpriced];
}

export function getNextOpponentId(primaryId: string, list: ModelInfo[]) {
  if (list.length < 2) {
    return "";
  }
  const i = list.findIndex((m) => m.id === primaryId);
  if (i >= 0 && i + 1 < list.length) {
    const next = list[i + 1];
    if (next.id !== primaryId) {
      return next.id;
    }
  }
  return list.find((m) => m.id !== primaryId)?.id ?? "";
}

/**
 * Build model-board price cell text from {@link formatUsdPerM} values (or `null`).
 * Strips trailing `/M`, uses `—` for missing sides, and sets `label` for aria.
 */
export function priceCellParts(
  inputFormatted: string | null,
  outputFormatted: string | null,
): { input: string; output: string; label: string } {
  const input = inputFormatted ? inputFormatted.replace(/\/M$/, "") : "—";
  const output = outputFormatted ? outputFormatted.replace(/\/M$/, "") : "—";

  return {
    input,
    output,
    label: `${input} / ${output}`,
  };
}
