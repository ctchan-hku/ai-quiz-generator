import { useCallback, useMemo, useState } from "react";

function clampPageIndex(page: number, totalPages: number): number {
  if (totalPages <= 0) {
    return 0;
  }
  return Math.min(Math.max(0, page), totalPages - 1);
}

/** Navigation state and handlers from {@link usePagination} for {@link PageNav}. */
export interface PaginationNavModel {
  safePage: number;
  totalPages: number;
  pageSize: number;
  goPrevious: () => void;
  goNext: () => void;
}

export interface UsePaginationResult<T> {
  pageItems: T[];
  nav: PaginationNavModel;
  resetToFirstPage: () => void;
}

/**
 * Client-side pagination: clamps the page when the list shrinks, exposes a slice
 * of `items` and a `nav` object for the `PageNav` component.
 */
export function usePagination<T>(
  items: readonly T[],
  pageSize: number,
): UsePaginationResult<T> {
  const [page, setPage] = useState(0);

  const totalPages =
    items.length === 0 ? 0 : Math.ceil(items.length / pageSize);

  const safePage = clampPageIndex(page, totalPages);

  const pageItems = useMemo(() => {
    const start = safePage * pageSize;
    return items.slice(start, start + pageSize);
  }, [items, safePage, pageSize]);

  const goPrevious = useCallback(() => {
    setPage((p) =>
      clampPageIndex(clampPageIndex(p, totalPages) - 1, totalPages),
    );
  }, [totalPages]);

  const goNext = useCallback(() => {
    setPage((p) =>
      clampPageIndex(clampPageIndex(p, totalPages) + 1, totalPages),
    );
  }, [totalPages]);

  const resetToFirstPage = useCallback(() => {
    setPage(0);
  }, []);

  const nav = useMemo<PaginationNavModel>(
    () => ({
      safePage,
      totalPages,
      pageSize,
      goPrevious,
      goNext,
    }),
    [safePage, totalPages, pageSize, goPrevious, goNext],
  );

  return { pageItems, nav, resetToFirstPage };
}
