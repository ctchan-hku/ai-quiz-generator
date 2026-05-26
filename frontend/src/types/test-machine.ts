import type { MultipleChoiceQuestion, GenerateTestResponse } from "../api/contracts";

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

export interface TestBattleBranchState {
  baseTestResponse: GenerateTestResponse;
  questionVersions: MultipleChoiceQuestion[][];
  selectedVersionIndex: number[];
}

export type GenerateTestMachineSuccess =
  | { mode: "single"; payload: GenerateTestResponse }
  | { mode: "battle"; payload: { left: GenerateTestResponse; right: GenerateTestResponse } };

export interface TestMachineState {
  status: TestMachineStatus;
  formConfig: TestFormConfig;
  baseTestResponse: GenerateTestResponse | null;
  questionVersions: MultipleChoiceQuestion[][] | null;
  selectedVersionIndex: number[] | null;
  test: GenerateTestResponse | null;
  battle: { left: TestBattleBranchState; right: TestBattleBranchState } | null;
  error: string | null;
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
      payload:
        | TestFormConfig
        | ((previous: TestFormConfig) => TestFormConfig);
    }
  | { type: "HYDRATE"; payload: TestMachineState }
  | {
      type: "APPEND_QUESTION_VERSION";
      payload: { index: number; question: MultipleChoiceQuestion };
    }
  | {
      type: "SET_QUESTION_VERSION";
      payload: { index: number; selected: number };
    };

export interface RefineQuestionParams {
  index: number;
  question: MultipleChoiceQuestion;
  comment: string;
  model: string;
  topic: string;
}

export function buildResolvedTestResponse(
  base: GenerateTestResponse,
  questionVersions: MultipleChoiceQuestion[][],
  selectedVersionIndex: number[],
): GenerateTestResponse {
  return {
    model_used: base.model_used,
    cost_usd: base.cost_usd,
    questions: questionVersions.map((vers, i) => vers[selectedVersionIndex[i]]),
  };
}
