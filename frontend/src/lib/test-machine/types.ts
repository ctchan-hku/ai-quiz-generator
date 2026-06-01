import type {
  MultipleChoiceQuestion,
  GenerateTestResponse,
  QuestionEditRequest,
} from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import type { TestVersionedReview } from "./versioned-review";

export type TestMachineStatus =
  | "idle"
  | "generating"
  | "reviewing"
  | "exporting"
  | "error";

export type TestBattle = {
  left: GenerateTestResponse;
  right: GenerateTestResponse;
};

export type GenerateTestMachineSuccess =
  | { mode: "single"; payload: GenerateTestResponse }
  | { mode: "battle"; payload: TestBattle };

export type QuestionEditState =
  | { status: "pending"; index: number }
  | { status: "error"; index: number; message: string };

export interface TestMachineState {
  status: TestMachineStatus;
  formConfig: TestFormConfig;
  review: TestVersionedReview | null;
  battle: TestBattle | null;
  error: string | null;
  questionEdit: QuestionEditState | null;
  reviewEpoch: number;
}

export type TestMachineAction =
  | { type: "START_GENERATE"; payload: TestFormConfig }
  | { type: "GENERATE_SUCCESS"; payload: GenerateTestMachineSuccess }
  | { type: "COMMIT_BATTLE_WINNER"; payload: { side: "left" | "right" } }
  | { type: "GENERATE_ERROR"; payload: string }
  | { type: "GENERATE_ABORTED" }
  | { type: "ENTER_EXPORTING" }
  | { type: "EXIT_EXPORTING" }
  | { type: "RESET"; form?: TestFormConfig }
  | {
      type: "SET_FORM_CONFIG";
      payload: TestFormConfig | ((previous: TestFormConfig) => TestFormConfig);
    }
  | { type: "HYDRATE"; payload: TestMachineState }
  | {
      type: "APPEND_QUESTION_VERSION";
      payload: { index: number; question: MultipleChoiceQuestion };
    }
  | {
      type: "SET_QUESTION_VERSION";
      payload: { index: number; selected: number };
    }
  | { type: "QUESTION_EDIT_START"; payload: { index: number } }
  | {
      type: "QUESTION_EDIT_ERROR";
      payload: { index: number; message: string };
    }
  | { type: "QUESTION_EDIT_CLEAR" };

export type QuestionEditParams = QuestionEditRequest & {
  index: number;
};
