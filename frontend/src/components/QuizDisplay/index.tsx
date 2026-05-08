import { useCallback, useState } from "react";

import type { ChangeEvent } from "react";

import type { ModelInfo } from "../../types/api";
import type {
  QuizBattleBranchState,
  RefineQuestionParams,
} from "../../types/quiz-machine";
import type { MultipleChoiceQuestion, QuizResponse } from "../../types/quiz";

import { formatEstimatedCostUsd } from "../../lib/format-usd";
import { BattleWinnerPanel } from "./BattleWinnerPanel";
import { CurrentQuizActions } from "./CurrentQuizActions";
import { QuizQuestionCard } from "./QuizQuestionCard";
import { QuizRunSummaryColumn, QuizRunSummaryHero } from "./QuizRunSummary";

export type QuizDisplayProps =
  | {
      mode: "battle";
      battle: { left: QuizBattleBranchState; right: QuizBattleBranchState };
      topic: string;
      models: ModelInfo[];
      onPickWinner: (side: "left" | "right") => void;
    }
  | {
      mode: "review";
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
      onCancelRefine?: () => void;
      refiningIndex: number | null;
      refineErrorIndex: number | null;
      refineErrorMessage: string | null;
    };

function labelForModel(models: ModelInfo[], modelId: string) {
  return models.find((m) => m.id === modelId)?.label ?? modelId;
}

function BattleQuizColumn({
  headerTitle,
  quiz,
}: {
  headerTitle: string;
  quiz: QuizResponse;
}) {
  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-4">
      <QuizRunSummaryColumn title={headerTitle} quiz={quiz} />
      <div className="flex flex-col gap-4">
        {quiz.questions.map((q, qIdx) => (
          <QuizQuestionCard key={qIdx} questionIndex={qIdx} question={q} />
        ))}
      </div>
    </div>
  );
}

function QuizBattleView({
  battle,
  topic,
  models,
  onPickWinner,
}: {
  battle: { left: QuizBattleBranchState; right: QuizBattleBranchState };
  topic: string;
  models: ModelInfo[];
  onPickWinner: (side: "left" | "right") => void;
}) {
  const leftQuiz = battle.left.baseQuizResponse;
  const rightQuiz = battle.right.baseQuizResponse;
  const combinedCostUsd = leftQuiz.cost_usd + rightQuiz.cost_usd;

  return (
    <div className="flex flex-col gap-6">
      <div className="card text-left">
        <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-60">
          Battle mode
        </p>
        <p className="mt-0 mb-3 text-sm text-[var(--color-text)]">
          Two full quizzes were generated from the same settings. Compare Left
          Opponent and Right Opponent, then pick the quiz you prefer — that
          model becomes the one used for the summary, journal export, and
          per-question refinement.
        </p>
        {topic.trim() !== "" ? (
          <p className="mb-2 mt-0 text-sm text-[var(--color-text)]">
            <span className="font-semibold">Topic: </span>
            {topic.trim()}
          </p>
        ) : null}
        <p className="mb-0 mt-0 text-sm text-[var(--color-text)]">
          <span className="font-semibold">Combined cost (est.): </span>
          {formatEstimatedCostUsd(combinedCostUsd)}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(16rem,18rem)] xl:items-start xl:gap-8">
        <BattleQuizColumn
          headerTitle={`Left Opponent · ${labelForModel(models, leftQuiz.model_used)}`}
          quiz={leftQuiz}
        />
        <BattleQuizColumn
          headerTitle={`Right Opponent · ${labelForModel(models, rightQuiz.model_used)}`}
          quiz={rightQuiz}
        />
        <div className="w-full shrink-0 xl:sticky xl:top-30 xl:z-30">
          <BattleWinnerPanel onPickWinner={onPickWinner} />
        </div>
      </div>
    </div>
  );
}

function QuizReviewView(props: Extract<QuizDisplayProps, { mode: "review" }>) {
  const {
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
    onCancelRefine,
    refiningIndex,
    refineErrorIndex,
    refineErrorMessage,
  } = props;

  const [refinePanelOpen, setRefinePanelOpen] = useState<
    Record<number, boolean>
  >({});

  const handleVersionChange = useCallback(
    (qIdx: number, e: ChangeEvent<HTMLSelectElement>) => {
      onSetQuestionVersion(qIdx, Number(e.target.value));
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

  function renderQuestionHeader(
    qIdx: number,
    nVersions: number,
    isRefining: boolean,
  ) {
    return (
      <>
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
      </>
    );
  }

  function renderQuestionFooter(
    qIdx: number,
    isRefining: boolean,
    showRefineError: boolean,
  ) {
    return (
      <>
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
              {isRefining && onCancelRefine ? (
                <button
                  type="button"
                  className="btn-secondary px-3 py-2 text-sm"
                  onClick={onCancelRefine}
                >
                  Stop
                </button>
              ) : null}
              <button
                type="button"
                className="btn-secondary px-3 py-2 text-sm"
                onClick={() => {
                  setRefinePanelOpen((prev) => ({ ...prev, [qIdx]: false }));
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
                setRefinePanelOpen((prev) => ({ ...prev, [qIdx]: true }));
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
      </>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <QuizRunSummaryHero quiz={quiz} />

      <div className="flex flex-col gap-6 md:flex-row md:items-start md:gap-6 lg:gap-8">
        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-4">
            {quiz.questions.map((q, qIdx) => {
              const nVersions = questionVersions[qIdx].length;
              const isRefining = refiningIndex === qIdx;
              const showRefineError = refineErrorIndex === qIdx;

              return (
                <QuizQuestionCard
                  key={qIdx}
                  questionIndex={qIdx}
                  question={q}
                  header={renderQuestionHeader(qIdx, nVersions, isRefining)}
                  footer={renderQuestionFooter(
                    qIdx,
                    isRefining,
                    showRefineError,
                  )}
                />
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

export function QuizDisplay(props: QuizDisplayProps) {
  if (props.mode === "battle") {
    const { battle, topic, models, onPickWinner } = props;
    return (
      <QuizBattleView
        battle={battle}
        topic={topic}
        models={models}
        onPickWinner={onPickWinner}
      />
    );
  }

  return <QuizReviewView {...props} />;
}
