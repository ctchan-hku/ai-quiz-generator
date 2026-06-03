import { isAxiosError } from "axios";
import type {
  GenerateTestRequest,
  GenerateTestResponse,
  LoginRequest,
  LoginResponse,
  ModelInfo,
  MultipleChoiceQuestion,
  QuestionEditRequest,
  QuestionEditResponse,
  UploadDocumentsResponse,
} from "./contracts";
import { toCamelCaseKeys, toSnakeCaseKeys } from "./case-keys";
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
  const { data } = await api.post("/api/workspace", body);
  return toCamelCaseKeys(data) as LoginResponse;
}

export async function generateTest(
  body: GenerateTestRequest,
  signal?: AbortSignal,
): Promise<GenerateTestResponse> {
  const { data } = await api.post("/api/generate/test", toSnakeCaseKeys(body), {
    ...(signal ? { signal } : {}),
  });
  return toCamelCaseKeys(data) as GenerateTestResponse;
}

export async function editQuestion(
  body: QuestionEditRequest,
  signal?: AbortSignal,
): Promise<MultipleChoiceQuestion> {
  const { data } = await api.post("/api/edit/question", toSnakeCaseKeys(body), {
    ...(signal ? { signal } : {}),
  });
  return (toCamelCaseKeys(data) as QuestionEditResponse).question;
}

export async function uploadDocuments(
  files: File[],
): Promise<UploadDocumentsResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const { data } = await api.post<UploadDocumentsResponse>(
    "/api/upload/documents",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    },
  );
  return toCamelCaseKeys(data) as UploadDocumentsResponse;
}
