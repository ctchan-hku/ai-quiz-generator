import type {
  MultipleChoiceQuestion,
  GenerateTestResponse,
} from "../api/contracts";

export type TestMachineStatus =
  | "idle"
  | "generating"
  | "reviewing"
  | "exporting"
  | "error";

export interface TestFormConfig {
  topic: string;
  numQuestions: number;
  models: [string, string];
  pipeline_version: 1 | 2;
  few_shot_examples: string[];
  user_instructions: string[];
  battleEnabled: boolean;
  selected_test_ids: string[];
}

export interface VersionedTestReview {
  generation: GenerateTestResponse;
  questionVersions: MultipleChoiceQuestion[][];
  selectedVersionIndex: number[];
}

export type TestBattle = {
  left: GenerateTestResponse;
  right: GenerateTestResponse;
};

export type GenerateTestMachineSuccess =
  | { mode: "single"; payload: GenerateTestResponse }
  | { mode: "battle"; payload: TestBattle };

export type RefineState =
  | { status: "pending"; index: number }
  | { status: "error"; index: number; message: string };

export interface TestMachineState {
  status: TestMachineStatus;
  formConfig: TestFormConfig;
  review: VersionedTestReview | null;
  battle: TestBattle | null;
  error: string | null;
  refine: RefineState | null;
  reviewGeneration: number;
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
  | { type: "REFINE_START"; payload: { index: number } }
  | {
      type: "REFINE_ERROR";
      payload: { index: number; message: string };
    }
  | { type: "REFINE_CLEAR" };

export interface RefineQuestionParams {
  index: number;
  question: MultipleChoiceQuestion;
  comment: string;
  model: string;
  topic: string;
}
