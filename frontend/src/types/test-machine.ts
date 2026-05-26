import type { MultipleChoiceQuestion, GenerateTestResponse } from "../api/contracts";

export type TestMachineStatus =
  | "idle"
  | "generating"
  | "reviewing"
  | "exporting"
  | "error";

/**
 * Canonical test-topic form snapshot: held on the machine after submit, persisted, and copied to the export journal as-is.
 * `models[0]` = primary model id; `models[1]` = battle opponent id (empty string when `battleEnabled` is false).
 */
export interface TestFormConfig {
  topic: string;
  /** Enforced client-side to match `GenerateTestRequest` / `config/test.ts` bounds. */
  numQuestions: number;
  models: [string, string];
  /** Sent as `pipeline_version` on `POST /api/generate/test`. */
  pipeline_version: 1 | 2;
  few_shot_examples: string[];
  user_instructions: string[];
  /** Parallel dual-column test generation (`models[1]` must be set when true). */
  battleEnabled: boolean;
}

/** One branch of a battle compare session (immutable API response + optional version stacks later). */
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
  /** First full-test `POST /api/generate/test` response; `model_used` / `cost_usd` stay fixed for the session. */
  baseTestResponse: GenerateTestResponse | null;
  /** Per-question version stacks (non-empty while reviewing after a successful generate). */
  questionVersions: MultipleChoiceQuestion[][] | null;
  selectedVersionIndex: number[] | null;
  /** Resolved test: `questions[i]` = `questionVersions[i][selectedVersionIndex[i]]` for export and display. */
  test: GenerateTestResponse | null;
  /** Dual-column comparison before the user commits a winner (summary / refine follow the winner). */
  battle: { left: TestBattleBranchState; right: TestBattleBranchState } | null;
  error: string | null;
  /** Drives `key` on review UI so local state (e.g. export notes) resets per generation without effects. */
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

/** Arguments for `POST /api/generate/question` from the review UI (resolved MCQ + form `topic` / `model`). */
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
