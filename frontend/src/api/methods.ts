import { isAxiosError } from "axios";
import type { TestFormConfig } from "../types/test-machine";
import type {
  GenerateQuestionRequest,
  GenerateTestRequest,
  LoginRequest,
  LoginResponse,
  ModelInfo,
  MultipleChoiceQuestion,
  QuestionGenerateResponse,
  TestResponse,
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

export async function login(body: LoginRequest): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/api/login", body);
  return data;
}

export async function generateTest(
  config: TestFormConfig,
  signal?: AbortSignal,
): Promise<TestResponse> {
  const body: GenerateTestRequest = {
    topic: config.topic,
    num_questions: config.numQuestions,
    model: config.models[0].trim(),
    pipeline_version: config.pipeline_version,
    few_shot_examples: config.few_shot_examples,
    user_instructions: config.user_instructions,
  };
  const { data } = await api.post<TestResponse>("/api/generate/test", body, {
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
