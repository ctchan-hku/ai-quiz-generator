import { isAxiosError } from "axios";
import type { QuizFormConfig } from "../types/quiz-machine";
import type {
  GenerateQuestionRequest,
  GenerateQuizRequest,
  ModelInfo,
  MultipleChoiceQuestion,
  QuestionGenerateResponse,
  QuizResponse,
} from "./contracts";
import { api } from "./client";

export function getRequestErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const data = error.response?.data as { detail?: unknown } | undefined;
    if (data?.detail !== undefined) {
      const { detail } = data;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        return detail
          .map((item) =>
            typeof item === "object" && item && "msg" in item
              ? String((item as { msg: string }).msg)
              : String(item),
          )
          .join("; ");
      }
    }
    return error.message || "Request failed";
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong";
}

export async function listModels(): Promise<ModelInfo[]> {
  const { data } = await api.get<{ models: ModelInfo[] }>("/api/models");
  return Array.isArray(data.models) ? data.models : [];
}

export async function generateQuiz(
  config: QuizFormConfig,
  signal?: AbortSignal,
): Promise<QuizResponse> {
  const {
    topic,
    numQuestions,
    model,
    few_shot_examples,
    user_instructions,
    pipeline_version,
  } = config;
  const body: GenerateQuizRequest = {
    topic,
    num_questions: numQuestions,
    model,
  };
  if (pipeline_version !== undefined) {
    body.pipeline_version = pipeline_version;
  }
  if (few_shot_examples && few_shot_examples.length > 0) {
    body.few_shot_examples = few_shot_examples;
  }
  if (user_instructions && user_instructions.length > 0) {
    body.user_instructions = user_instructions;
  }
  const { data } = await api.post<QuizResponse>("/api/generate/quiz", body, {
    ...(signal ? { signal } : {}),
  });
  return data;
}

export async function generateQuestion(
  body: GenerateQuestionRequest,
  signal?: AbortSignal,
): Promise<MultipleChoiceQuestion> {
  const { data } = await api.post<QuestionGenerateResponse>(
    "/api/generate/question",
    body,
    { ...(signal ? { signal } : {}) },
  );
  return data.question;
}
