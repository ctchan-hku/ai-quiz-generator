import { useQuizMachine } from './hooks/useQuizMachine'

/**
 * Wave 1 shell: verifies providers, design tokens, and state machine wiring.
 * Quiz UI arrives in Wave 2 (03-02-PLAN).
 */
function App() {
  const { state } = useQuizMachine()

  return (
    <main className="mx-auto flex min-h-svh max-w-3xl flex-col px-4 py-8 md:px-6 lg:px-8">
      <div className="card text-left">
        <h1 className="mt-0 text-2xl md:text-3xl">AI Quiz Generator</h1>
        <p className="mb-0 text-base text-[var(--color-text)] opacity-90">
          Phase 3 — Wave 1 scaffold: Vite, Tailwind, academic Glassmorphism tokens, API client, and{' '}
          <code className="rounded bg-white/60 px-1">useQuizMachine</code>.
        </p>
        <p className="mt-4 mb-0 text-sm">
          Status: <strong>{state.status}</strong>
          {state.formConfig.model ? ` · model: ${state.formConfig.model}` : ''}
        </p>
      </div>
    </main>
  )
}

export default App
