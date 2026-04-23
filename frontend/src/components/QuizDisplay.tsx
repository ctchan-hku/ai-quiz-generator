import { useState } from 'react'
import type { MultipleChoiceQuestion, QuizResponse } from '../types/quiz'

interface QuizDisplayProps {
  quiz: QuizResponse
}

type RevealState = {
  revealed: boolean
  pickedIndex: number | null
}

function isMultipleChoice(q: QuizResponse['questions'][number]): q is MultipleChoiceQuestion {
  return q.question_type === 'multiple_choice'
}

const LABELS = ['A', 'B', 'C', 'D'] as const

export function QuizDisplay({ quiz }: QuizDisplayProps) {
  const [revealByIndex, setRevealByIndex] = useState<Record<number, RevealState>>({})

  function pickOption(questionIndex: number, optionIndex: number) {
    setRevealByIndex((prev) => ({
      ...prev,
      [questionIndex]: { revealed: true, pickedIndex: optionIndex },
    }))
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="card text-left">
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)] opacity-80">
          Model: <strong>{quiz.model_used}</strong>
          {quiz.truncated ? ' · Source text was truncated' : null}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {quiz.questions.map((q, qIdx) => {
          if (!isMultipleChoice(q)) {
            return (
              <div key={`skip-${qIdx}`} className="card text-left">
                <p className="text-sm text-[var(--color-destructive)]">
                  Unsupported question type in v1 UI: {q.question_type}
                </p>
              </div>
            )
          }

          const reveal = revealByIndex[qIdx] ?? { revealed: false, pickedIndex: null }
          const correctSet = new Set(q.correct_indices)

          return (
            <article key={qIdx} className="card text-left shadow-[var(--shadow-lg)]">
              <h3 className="mt-0 mb-3 font-[family-name:var(--font-heading)] text-lg font-semibold text-[var(--color-text)]">
                <span className="text-[var(--color-primary)]">{qIdx + 1}.</span> {q.question}
              </h3>
              <ul className="m-0 flex list-none flex-col gap-2 p-0">
                {q.options.map((opt, optIdx) => {
                  const label = LABELS[optIdx] ?? String(optIdx + 1)
                  const isCorrect = correctSet.has(optIdx)
                  const isPicked = reveal.pickedIndex === optIdx
                  let optionClass =
                    'flex w-full cursor-pointer items-start gap-3 rounded-lg border border-[rgb(30_41_59/0.12)] bg-white/50 px-3 py-3 text-left transition-[box-shadow,background-color,border-color] duration-200 ease-out'

                  if (reveal.revealed) {
                    if (isCorrect) {
                      optionClass +=
                        ' ring-2 ring-[var(--color-primary)]/50 bg-[var(--color-primary)]/10 border-[var(--color-primary)]/30'
                    } else if (isPicked) {
                      optionClass +=
                        ' ring-2 ring-[var(--color-destructive)]/40 bg-[var(--color-destructive)]/5'
                    } else {
                      optionClass += ' opacity-60'
                    }
                  } else {
                    optionClass += ' hover:bg-white/80 hover:shadow-[var(--shadow-sm)]'
                  }

                  return (
                    <li key={optIdx}>
                      <button
                        type="button"
                        className={optionClass}
                        onClick={() => {
                          if (!reveal.revealed) pickOption(qIdx, optIdx)
                        }}
                        disabled={reveal.revealed}
                      >
                        <span className="font-bold text-[var(--color-primary)]">{label}.</span>
                        <span className="text-[var(--color-text)]">{opt}</span>
                      </button>
                    </li>
                  )
                })}
              </ul>
              {reveal.revealed ? (
                <p className="mt-4 mb-0 border-t border-[rgb(30_41_59/0.1)] pt-4 text-sm leading-relaxed text-[var(--color-text)]">
                  <span className="font-semibold text-[var(--color-text)]">Explanation: </span>
                  {q.explanation}
                </p>
              ) : null}
            </article>
          )
        })}
      </div>
    </div>
  )
}
