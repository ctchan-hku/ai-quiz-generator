import { useState, useCallback } from "react";

import type { ChangeEvent } from "react";

import type { MultipleChoiceQuestion, QuizResponse } from "../types/quiz";
import type { RefineQuestionParams } from "../types/quiz-machine";
import { optionLabel } from "../lib/option";
import { CurrentQuizActions } from "./CurrentQuizActions";

interface QuizDisplayProps {
  quiz: QuizResponse;
  topic: string;
  resolvedModel: string;
  comments: string[];
  onCommentChange: (index: number, value: string) => void;
  questionVersions: MultipleChoiceQuestion[][];
  selectedVersionIndex: number[];
  onSetQuestionVersion: (index: number, selected: number) => void;
  onRefine: (params: RefineQuestionParams) => void;
  onRefinePanelClose: () => void;
  refiningIndex: number | null;
  refineErrorIndex: number | null;
  refineErrorMessage: string | null;
}

type RevealState = {
  revealed: boolean;
  pickedIndex: number | null;
};

export function QuizDisplay({
  quiz,
  topic,
  resolvedModel,
  comments,
  onCommentChange,
  questionVersions,
  selectedVersionIndex,
  onSetQuestionVersion,
  onRefine,
  onRefinePanelClose,
  refiningIndex,
  refineErrorIndex,
  refineErrorMessage,
}: QuizDisplayProps) {
  const [revealByIndex, setRevealByIndex] = useState<
    Record<number, RevealState>
  >({});
  const [refinePanelOpen, setRefinePanelOpen] = useState<Record<number, boolean>>(
    {},
  );

  function pickOption(questionIndex: number, optionIndex: number) {
    setRevealByIndex((prev) => ({
      ...prev,
      [questionIndex]: { revealed: true, pickedIndex: optionIndex },
    }));
  }

  const handleVersionChange = useCallback(
    (qIdx: number, e: ChangeEvent<HTMLSelectElement>) => {
      const selected = Number(e.target.value);
      onSetQuestionVersion(qIdx, selected);
      setRevealByIndex((prev) => {
        const next = { ...prev };
        delete next[qIdx];
        return next;
      });
    },
    [onSetQuestionVersion],
  );

  const handleCommentChange = useCallback(
    (index: number, e: ChangeEvent<HTMLTextAreaElement>) => {
      onCommentChange(index, e.target.value);
    },
    [onCommentChange],
  );

  const handleConfirmRefine = useCallback(
    (qIdx: number) => {
      onRefine({
        index: qIdx,
        question: quiz.questions[qIdx],
        comment: comments[qIdx] ?? "",
        model: resolvedModel,
        topic,
      });
    },
    [onRefine, quiz.questions, comments, resolvedModel, topic],
  );

  return (
    <div className="flex flex-col gap-6">
      <div className="card text-left">
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)] opacity-80">
          Model: <strong>{quiz.model_used}</strong>
          {quiz.truncated ? " · Source text was truncated" : null}
        </p>
      </div>

      <div className="flex flex-col gap-6 md:flex-row md:items-start md:gap-6 lg:gap-8">
        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-4">
            {quiz.questions.map((q, qIdx) => {
              const reveal = revealByIndex[qIdx] ?? {
                revealed: false,

                pickedIndex: null,
              };

              const correctSet = new Set(q.correct_indices);
              const nVersions = questionVersions[qIdx].length;
              const isRefining = refiningIndex === qIdx;
              const showRefineError = refineErrorIndex === qIdx;

              return (
                <article
                  key={qIdx}
                  className="card flex flex-col text-left shadow-[var(--shadow-lg)]"
                >
                  <div className="mb-3 flex flex-wrap items-center gap-3">
                    <label
                      className="text-sm font-bold text-[var(--color-text)]"
                      htmlFor={`question-version-${qIdx}`}
                    >
                      Version
                    </label>
                    <select
                      id={`question-version-${qIdx}`}
                      className="input max-w-[12rem] py-2 text-sm"
                      value={String(selectedVersionIndex[qIdx])}
                      onChange={(e) => handleVersionChange(qIdx, e)}
                      disabled={isRefining}
                    >
                      {Array.from({ length: nVersions }, (_, v) => (
                        <option key={v} value={v}>
                          Version {v + 1}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex-grow">
                    <h3 className="mt-0 mb-3 font-[family-name:var(--font-heading)] text-lg font-semibold text-[var(--color-text)]">
                      <span className="text-[var(--color-primary)]">
                        {qIdx + 1}.
                      </span>{" "}
                      {q.question}
                    </h3>

                    <ul className="m-0 flex list-none flex-col gap-2 p-0">
                      {q.options.map((opt, optIdx) => {
                        const label = optionLabel(optIdx);

                        const isCorrect = correctSet.has(optIdx);

                        const isPicked = reveal.pickedIndex === optIdx;

                        let optionClass =
                          "flex w-full cursor-pointer items-start gap-3 rounded-lg border border-[rgb(30_41_59/0.12)] bg-white/50 px-3 py-3 text-left transition-[box-shadow,background-color,border-color] duration-200 ease-out";

                        if (reveal.revealed) {
                          if (isCorrect) {
                            optionClass +=
                              " ring-2 ring-[var(--color-primary)]/50 bg-[var(--color-primary)]/10 border-[var(--color-primary)]/30";
                          } else if (isPicked) {
                            optionClass +=
                              " ring-2 ring-[var(--color-destructive)]/40 bg-[var(--color-destructive)]/5";
                          } else {
                            optionClass += " opacity-60";
                          }
                        } else {
                          optionClass +=
                            " hover:bg-white/80 hover:shadow-[var(--shadow-sm)]";
                        }

                        return (
                          <li key={optIdx}>
                            <button
                              type="button"
                              className={optionClass}
                              onClick={() => {
                                if (!reveal.revealed) pickOption(qIdx, optIdx);
                              }}
                              disabled={reveal.revealed}
                            >
                              <span className="font-bold text-[var(--color-primary)]">
                                {label}.
                              </span>

                              <span className="text-[var(--color-text)]">
                                {opt}
                              </span>
                            </button>
                          </li>
                        );
                      })}
                    </ul>

                    <div className="mt-4">
                      <p className="mb-4 mt-0 text-sm leading-relaxed text-[var(--color-text)]">
                        <span className="font-semibold text-[var(--color-text)]">
                          Explanation:{" "}
                        </span>

                        {q.explanation}
                      </p>
                    </div>
                  </div>

                  <div className="border-t border-[rgb(30_41_59/0.1)] pt-4">
                    <div>
                      <label
                        className="mb-1 block text-sm font-bold text-[var(--color-text)]"
                        htmlFor={`export-comment-${qIdx}`}
                      >
                        Comment
                      </label>

                      <textarea
                        id={`export-comment-${qIdx}`}
                        className="input min-h-[4.5rem] resize-y"
                        value={comments[qIdx] ?? ""}
                        onChange={(e) => handleCommentChange(qIdx, e)}
                        placeholder="Optional comment..."
                        rows={2}
                        disabled={isRefining}
                      />
                    </div>

                    <div className="mt-3 flex flex-col gap-2">
                      {refinePanelOpen[qIdx] ? (
                        <div className="flex flex-wrap items-center gap-2">
                          <button
                            type="button"
                            className="btn-primary px-3 py-2 text-sm"
                            onClick={() => handleConfirmRefine(qIdx)}
                            disabled={isRefining || !resolvedModel.trim()}
                          >
                            {isRefining ? "Refining…" : "Confirm refinement"}
                          </button>
                          <button
                            type="button"
                            className="btn-secondary px-3 py-2 text-sm"
                            onClick={() => {
                              setRefinePanelOpen((prev) => ({
                                ...prev,
                                [qIdx]: false,
                              }));
                              onRefinePanelClose();
                            }}
                            disabled={isRefining}
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          className="btn-secondary w-full justify-center px-3 py-2 text-sm sm:w-auto"
                          onClick={() => {
                            onRefinePanelClose();
                            setRefinePanelOpen((prev) => ({
                              ...prev,
                              [qIdx]: true,
                            }));
                          }}
                          disabled={isRefining}
                        >
                          Refine this question
                        </button>
                      )}
                    </div>

                    {showRefineError && refineErrorMessage ? (
                      <p
                        className="mb-0 mt-2 text-sm text-[var(--color-destructive)]"
                        role="alert"
                      >
                        {refineErrorMessage}
                      </p>
                    ) : null}
                  </div>
                </article>
              );
            })}
          </div>
        </div>

        <div className="w-full shrink-0 md:w-72 md:self-start md:sticky md:top-30 md:z-30 lg:w-80">
          <CurrentQuizActions quiz={quiz} topic={topic} comments={comments} />
        </div>
      </div>
    </div>
  );
}
