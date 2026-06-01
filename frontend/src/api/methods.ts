import { isAxiosError } from "axios";
import type { TestFormConfig } from "../config/test-form";
import type {
  QuestionEditRequest,
  QuestionEditResponse,
  GenerateTestRequest,
  GenerateTestResponse,
  LoginRequest,
  LoginResponse,
  ModelInfo,
  MultipleChoiceQuestion,
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
  const { data } = await api.post<LoginResponse>("/api/workspace", body);
  return data;
}

export async function generateTest(
  config: TestFormConfig,
  signal?: AbortSignal,
): Promise<GenerateTestResponse> {
  const body: GenerateTestRequest = {
    topic: config.topic,
    num_questions: config.numQuestions,
    model: config.models[0].trim(),
    pipeline_version: config.pipeline_version,
    few_shot_examples: config.few_shot_examples,
    user_instructions: config.user_instructions,
    selected_test_ids: config.selected_test_ids,
  };
  const { data } = await api.post<GenerateTestResponse>(
    "/api/generate/test",
    body,
    {
      ...(signal ? { signal } : {}),
    },
  );
  return data;
}

export async function editQuestion(
  body: QuestionEditRequest,
  signal?: AbortSignal,
): Promise<MultipleChoiceQuestion> {
  const { data } = await api.post<QuestionEditResponse>(
    "/api/edit/question",
    body,
    { ...(signal ? { signal } : {}) },
  );
  return data.question;
}
