import { useCallback, useState } from "react";

import type { ChangeEvent } from "react";

import type { ModelInfo } from "../../types/api";
import type {
  QuizBattleBranchState,
  QuizFormConfig,
  RefineQuestionParams,
} from "../../types/quiz-machine";
import type { MultipleChoiceQuestion, QuizResponse } from "../../types/quiz";

import { formatEstimatedCostUsd } from "../../lib/format-usd";

import { BattleOpponentCarousel } from "./BattleOpponentCarousel";
import { CurrentQuizActions } from "./CurrentQuizActions";
import { QuizQuestionCard } from "./QuizQuestionCard";
import { QuizRunSummaryHero } from "./QuizRunSummary";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

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
      generationForm: QuizFormConfig;
      models: ModelInfo[];
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

function BattleQuizQuestions({ quiz }: { quiz: QuizResponse }) {
  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-4">
      {quiz.questions.map((q, qIdx) => (
        <QuizQuestionCard key={qIdx} questionIndex={qIdx} question={q} />
      ))}
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

  const leftTab = {
    roleLabel: "Left",
    modelLabel: labelForModel(models, leftQuiz.model_used),
    estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(leftQuiz.cost_usd)}`,
    wasTruncated: leftQuiz.truncated,
  };
  const rightTab = {
    roleLabel: "Right",
    modelLabel: labelForModel(models, rightQuiz.model_used),
    estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(rightQuiz.cost_usd)}`,
    wasTruncated: rightQuiz.truncated,
  };

  const topicLine =
    topic.trim() !== "" ? (
      <p className="mb-0 mt-0 text-sm text-foreground">
        <span className="font-semibold">Topic: </span>
        {topic.trim()}
      </p>
    ) : null;

  return (
    <div className="flex flex-col gap-6">
      {topicLine}

      <BattleOpponentCarousel
        leftTab={leftTab}
        rightTab={rightTab}
        leftPane={<BattleQuizQuestions quiz={leftQuiz} />}
        rightPane={<BattleQuizQuestions quiz={rightQuiz} />}
        onConfirmSelection={onPickWinner}
      />
    </div>
  );
}

function QuizReviewView(props: Extract<QuizDisplayProps, { mode: "review" }>) {
  const {
    quiz,
    topic,
    generationForm,
    models,
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
        <Label
          className="text-sm font-bold text-foreground"
          htmlFor={`question-version-${qIdx}`}
        >
          Version
        </Label>
        <select
          id={`question-version-${qIdx}`}
          className="flex h-9 w-full max-w-[12rem] items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1"
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
          <Label
            className="mb-2 block text-sm font-bold text-foreground"
            htmlFor={`export-comment-${qIdx}`}
          >
            Comment
          </Label>
          <Textarea
            id={`export-comment-${qIdx}`}
            className="min-h-[4.5rem] resize-y bg-background"
            value={comments[qIdx] ?? ""}
            onChange={(e) => handleCommentChange(qIdx, e)}
            placeholder="Optional comment..."
            rows={2}
            disabled={isRefining}
          />
        </div>

        <div className="mt-4 flex flex-col gap-2">
          {refinePanelOpen[qIdx] ? (
            <div className="flex flex-wrap items-center gap-2">
              <Button
                type="button"
                onClick={() => handleConfirmRefine(qIdx)}
                disabled={isRefining || !resolvedModel.trim()}
              >
                {isRefining ? "Refining…" : "Confirm refinement"}
              </Button>
              {isRefining && onCancelRefine ? (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onCancelRefine}
                >
                  Stop
                </Button>
              ) : null}
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setRefinePanelOpen((prev) => ({ ...prev, [qIdx]: false }));
                  onRefinePanelClose();
                }}
                disabled={isRefining}
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              type="button"
              variant="secondary"
              className="w-full sm:w-auto"
              onClick={() => {
                onRefinePanelClose();
                setRefinePanelOpen((prev) => ({ ...prev, [qIdx]: true }));
              }}
              disabled={isRefining}
            >
              Refine this question
            </Button>
          )}
        </div>

        {showRefineError && refineErrorMessage ? (
          <p className="mb-0 mt-3 text-sm text-destructive" role="alert">
            {refineErrorMessage}
          </p>
        ) : null}
      </>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <QuizRunSummaryHero quiz={quiz} models={models} />

      <div className="flex flex-col gap-6 md:flex-row md:items-start md:gap-6 lg:gap-8">
        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-6">
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
          <CurrentQuizActions
            quiz={quiz}
            topic={topic}
            comments={comments}
            generationForm={generationForm}
          />
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
