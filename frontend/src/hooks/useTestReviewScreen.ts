import { useCallback, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import {
  fromTestVersionedReview,
  selectedQuestion,
} from "@/lib/test-machine/versioned-review";
import { pipelineVersionCaption } from "@/config/test-form";
import { formatEstimatedCostUsd } from "@/lib/display/format-usd";
import { optionLabel } from "@/lib/display/mc-option-label";
import { modelDisplayLabel } from "@/lib/model-board/model-label";
import type { TestDisplayProps } from "@/components/TestDisplay/types";

export type ReviewModeProps = Extract<TestDisplayProps, { mode: "review" }>;

export function useTestReviewScreen(props: ReviewModeProps) {
  const {
    comments,
    onCommentChange,
    review,
    onSetQuestionVersion,
    onEditQuestion,
    onQuestionEditClose,
    onCancelQuestionEdit,
    questionEdit,
    topic,
  } = props;

  const resolvedModel = review.generation.modelUsed;
  const exportTest = useMemo(() => fromTestVersionedReview(review), [review]);

  const questions = useMemo(
    () =>
      review.questionVersions.map((_, qIdx) => selectedQuestion(review, qIdx)),
    [review],
  );

  const optionLabelsByQuestion = useMemo(
    () =>
      questions.map((q) => q.options.map((_, optIdx) => optionLabel(optIdx))),
    [questions],
  );

  const [editPanelOpen, setEditPanelOpen] = useState<Record<number, boolean>>(
    {},
  );

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

  const handleConfirmEdit = useCallback(
    (qIdx: number) => {
      onEditQuestion({
        index: qIdx,
        question: questions[qIdx],
        comment: comments[qIdx] ?? "",
        model: resolvedModel,
        topic,
      });
    },
    [onEditQuestion, questions, comments, resolvedModel, topic],
  );

  const toggleEditPanel = useCallback(
    (qIdx: number, open: boolean) => {
      setEditPanelOpen((prev) => ({ ...prev, [qIdx]: open }));
      if (!open) {
        onQuestionEditClose();
      }
    },
    [onQuestionEditClose],
  );

  const openEditPanel = useCallback(
    (qIdx: number) => {
      onQuestionEditClose();
      toggleEditPanel(qIdx, true);
    },
    [onQuestionEditClose, toggleEditPanel],
  );

  const costLabel = useMemo(
    () => formatEstimatedCostUsd(review.generation.costUsd),
    [review.generation.costUsd],
  );

  const modelLabel = useMemo(
    () => modelDisplayLabel(props.models, review.generation.modelUsed),
    [props.models, review.generation.modelUsed],
  );

  const pipelineCaption = pipelineVersionCaption(
    props.formConfig.pipelineVersion,
  );

  return {
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
    formConfig: props.formConfig,
  };
}

export type TestReviewScreen = ReturnType<typeof useTestReviewScreen>;
