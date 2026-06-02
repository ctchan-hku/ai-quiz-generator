import type { ChangeEvent } from "react";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { TestReviewScreen } from "@/hooks/useTestReviewScreen";

import { CurrentTestActions } from "./CurrentTestActions";
import { TestRunSummaryHero } from "./TestRunSummary";
import { TestQuestionCard } from "../shared/TestQuestionCard";
import type { TestDisplayProps } from "../types";

type ReviewProps = Extract<TestDisplayProps, { mode: "review" }>;

type TestReviewViewProps = ReviewProps & {
  screen: TestReviewScreen;
};

export function TestReviewView({ screen }: TestReviewViewProps) {
  const {
    exportTest,
    resolvedModel,
    questions,
    optionLabelsByQuestion,
    costLabel,
    modelLabel,
    pipelineCaption,
    editPanelOpen,
    handleVersionChange,
    handleCommentChange,
    handleConfirmEdit,
    toggleEditPanel,
    openEditPanel,
    review,
    questionEdit,
    onCancelQuestionEdit,
    comments,
    formConfig,
  } = screen;

  function renderQuestionHeader(
    qIdx: number,
    nVersions: number,
    isEditing: boolean,
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
          value={String(review.selectedVersionIndex[qIdx])}
          onChange={(e: ChangeEvent<HTMLSelectElement>) =>
            handleVersionChange(qIdx, e)
          }
          disabled={isEditing}
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
    isEditing: boolean,
    editErrorMessage: string | null,
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
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
              handleCommentChange(qIdx, e)
            }
            placeholder="Optional comment..."
            rows={2}
            disabled={isEditing}
          />
        </div>

        <div className="mt-4 flex flex-col gap-2">
          {editPanelOpen[qIdx] ? (
            <div className="flex flex-wrap items-center gap-2">
              <Button
                type="button"
                onClick={() => handleConfirmEdit(qIdx)}
                disabled={isEditing || !resolvedModel.trim()}
              >
                {isEditing ? "Editing…" : "Confirm edit"}
              </Button>
              {isEditing && onCancelQuestionEdit ? (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onCancelQuestionEdit}
                >
                  Stop
                </Button>
              ) : null}
              <Button
                type="button"
                variant="outline"
                onClick={() => toggleEditPanel(qIdx, false)}
                disabled={isEditing}
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              type="button"
              variant="secondary"
              className="w-full sm:w-auto"
              onClick={() => openEditPanel(qIdx)}
              disabled={isEditing}
            >
              Edit this question
            </Button>
          )}
        </div>

        {editErrorMessage ? (
          <p className="mb-0 mt-3 text-sm text-destructive" role="alert">
            {editErrorMessage}
          </p>
        ) : null}
      </>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <TestRunSummaryHero
        modelLabel={modelLabel}
        costLabel={costLabel}
        pipelineCaption={pipelineCaption}
      />

      <div className="flex flex-col gap-6 md:flex-row md:items-start md:gap-6 lg:gap-8">
        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-6">
            {review.questionVersions.map((_, qIdx) => {
              const nVersions = review.questionVersions[qIdx].length;
              const isEditing =
                questionEdit?.status === "pending" &&
                questionEdit.index === qIdx;
              const editErrorMessage =
                questionEdit?.status === "error" && questionEdit.index === qIdx
                  ? questionEdit.message
                  : null;

              return (
                <TestQuestionCard
                  key={qIdx}
                  questionIndex={qIdx}
                  question={questions[qIdx]}
                  optionLabels={optionLabelsByQuestion[qIdx]}
                  header={renderQuestionHeader(qIdx, nVersions, isEditing)}
                  footer={renderQuestionFooter(
                    qIdx,
                    isEditing,
                    editErrorMessage,
                  )}
                />
              );
            })}
          </div>
        </div>

        <div className="w-full shrink-0 md:w-72 md:self-start md:sticky md:top-30 md:z-30 lg:w-80">
          <CurrentTestActions
            test={exportTest}
            comments={comments}
            formConfig={formConfig}
          />
        </div>
      </div>
    </div>
  );
}
