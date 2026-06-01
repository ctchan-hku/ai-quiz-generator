import type { ModelInfo } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import type {
  QuestionEditParams,
  QuestionEditState,
  TestBattle,
} from "@/lib/test-machine/types";
import type { TestVersionedReview } from "@/lib/test-machine/versioned-review";

export type TestDisplayProps =
  | {
      mode: "battle";
      battle: TestBattle;
      topic: string;
      pipelineVersion: 1 | 2;
      models: ModelInfo[];
      onPickWinner: (side: "left" | "right") => void;
    }
  | {
      mode: "review";
      topic: string;
      generationForm: TestFormConfig;
      models: ModelInfo[];
      comments: string[];
      onCommentChange: (index: number, value: string) => void;
      review: TestVersionedReview;
      onSetQuestionVersion: (index: number, selected: number) => void;
      onEditQuestion: (params: QuestionEditParams) => void;
      onQuestionEditClose: () => void;
      onCancelQuestionEdit?: () => void;
      questionEdit: QuestionEditState | null;
    };
