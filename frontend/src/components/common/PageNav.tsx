import type { PaginationNavModel } from "../../hooks/usePagination";

export interface PageNavProps {
  pagination: PaginationNavModel;
  disabled?: boolean;
  /** `aria-label` for the `<nav>` element. */
  navAriaLabel?: string;
}

export function PageNav({
  pagination,
  disabled = false,
  navAriaLabel = "Pages",
}: PageNavProps) {
  const { safePage, totalPages, pageSize, goPrevious, goNext } = pagination;

  if (totalPages <= 1) {
    return null;
  }

  return (
    <nav
      className="flex flex-wrap items-center justify-between gap-3 text-sm text-[var(--color-text)]"
      aria-label={navAriaLabel}
    >
      <span className="opacity-90">
        Page {safePage + 1} of {totalPages}
        <span className="sr-only">, {pageSize} items per page maximum</span>
      </span>
      <div className="flex gap-2">
        <button
          type="button"
          className="btn-secondary px-3 py-1.5 text-xs"
          disabled={safePage <= 0 || disabled}
          onClick={goPrevious}
        >
          Previous
        </button>
        <button
          type="button"
          className="btn-secondary px-3 py-1.5 text-xs"
          disabled={safePage >= totalPages - 1 || disabled}
          onClick={goNext}
        >
          Next
        </button>
      </div>
    </nav>
  );
}
