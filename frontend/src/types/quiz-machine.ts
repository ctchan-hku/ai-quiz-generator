import { quizFormFieldDefaults } from "../config/quiz-form";
import type { MultipleChoiceQuestion, QuizResponse } from "../api/contracts";

export type QuizMachineStatus =
  | "idle"
  | "generating"
  | "reviewing"
  | "exporting"
  | "error";

/**
 * Canonical quiz-topic form snapshot: held on the machine after submit, persisted, and copied to the export journal as-is.
 * `models[0]` = primary model id; `models[1]` = battle opponent id (empty string when not battling).
 */
export interface QuizFormConfig {
  topic: string;
  /** Enforced client-side to match `GenerateQuizRequest` / `config/quiz.ts` bounds. */
  numQuestions: number;
  models: [string, string];
  /** Sent as `pipeline_version` on `POST /api/generate/quiz`. */
  pipeline_version: 1 | 2;
  few_shot_examples: string[];
  user_instructions: string[];
}

export function createDefaultQuizFormConfig(): QuizFormConfig {
  return {
    topic: quizFormFieldDefaults.topic,
    numQuestions: quizFormFieldDefaults.numQuestions,
    models: [
      quizFormFieldDefaults.models[0],
      quizFormFieldDefaults.models[1],
    ],
    pipeline_version: quizFormFieldDefaults.pipeline_version,
    few_shot_examples: [...quizFormFieldDefaults.few_shot_examples],
    user_instructions: [...quizFormFieldDefaults.user_instructions],
  };
}

/** One branch of a battle compare session (immutable API response + optional version stacks later). */
export interface QuizBattleBranchState {
  baseQuizResponse: QuizResponse;
  questionVersions: MultipleChoiceQuestion[][];
  selectedVersionIndex: number[];
}

export type GenerateQuizMachineSuccess =
  | { mode: "single"; payload: QuizResponse }
  | { mode: "battle"; payload: { left: QuizResponse; right: QuizResponse } };

export interface QuizMachineState {
  status: QuizMachineStatus;
  formConfig: QuizFormConfig;
  /** First full-quiz `POST /api/generate/quiz` response; `model_used` / `source` / `truncated` stay fixed for the session. */
  baseQuizResponse: QuizResponse | null;
  /** Per-question version stacks (non-empty while reviewing after a successful generate). */
  questionVersions: MultipleChoiceQuestion[][] | null;
  selectedVersionIndex: number[] | null;
  /** Resolved quiz: `questions[i]` = `questionVersions[i][selectedVersionIndex[i]]` for export and display. */
  quiz: QuizResponse | null;
  /** Dual-column comparison before the user commits a winner (summary / refine follow the winner). */
  battle: { left: QuizBattleBranchState; right: QuizBattleBranchState } | null;
  error: string | null;
  /** Drives `key` on review UI so local state (e.g. export notes) resets per generation without effects. */
  reviewGeneration: number;
}

export type QuizMachineAction =
  | { type: "START_GENERATE"; payload: QuizFormConfig }
  | { type: "GENERATE_SUCCESS"; payload: GenerateQuizMachineSuccess }
  | { type: "COMMIT_BATTLE_WINNER"; payload: { side: "left" | "right" } }
  | { type: "GENERATE_ERROR"; payload: string }
  | { type: "GENERATE_ABORTED" }
  | { type: "ENTER_EXPORTING" }
  | { type: "EXIT_EXPORTING" }
  | { type: "RESET" }
  | { type: "HYDRATE"; payload: QuizMachineState }
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

export function buildResolvedQuizResponse(
  base: QuizResponse,
  questionVersions: MultipleChoiceQuestion[][],
  selectedVersionIndex: number[],
): QuizResponse {
  return {
    model_used: base.model_used,
    source: base.source,
    truncated: base.truncated,
    cost_usd: base.cost_usd,
    questions: questionVersions.map((vers, i) => vers[selectedVersionIndex[i]]),
  };
}
