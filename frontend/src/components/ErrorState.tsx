interface ErrorStateProps {
  error: string
  onRetry?: () => void
}

/**
 * API / rate-limit / network errors — message comes from the server or axios layer.
 */
export function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <div
      className="card border-l-4 text-left"
      style={{ borderLeftColor: 'var(--color-destructive)' }}
      role="alert"
    >
      <p className="mt-0 mb-2 font-[family-name:var(--font-heading)] text-lg font-semibold text-[var(--color-destructive)]">
        Oops! Something went wrong.
      </p>
      <p className="mb-0 text-base text-[var(--color-text)]">{error}</p>
      {onRetry ? (
        <button type="button" className="btn-secondary mt-4" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  )
}
