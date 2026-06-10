import axios, { isAxiosError } from "axios";
import type {
  GenerateTestRequest,
  GenerateTestResponse,
  KnowledgeDocumentSummary,
  LoginRequest,
  LoginResponse,
  ModelInfo,
  MultipleChoiceQuestion,
  QuestionEditRequest,
  QuestionEditResponse,
  UploadDocumentsResponse,
} from "./contracts";
import { getCmsApiBaseUrl } from "@/config/cms-api";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/lib/access-token";
import { toCamelCaseKeys, toSnakeCaseKeys } from "./case-keys";
import { api } from "./client";

interface CmsLoginResponse {
  success: boolean;
  access_token: string;
  message?: string;
}

export function getRequestErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const data = error.response?.data as
      | { detail?: unknown; message?: unknown }
      | undefined;
    if (data?.message !== undefined && typeof data.message === "string") {
      return data.message;
    }
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
  const { data } = await axios.post<CmsLoginResponse>(
    `${getCmsApiBaseUrl()}/api/authentication/login`,
    body,
  );
  if (!data.success) {
    throw new Error(data.message || "Login failed");
  }
  setAccessToken(data.access_token);
  return getWorkspaceMe();
}

export async function getWorkspaceMe(): Promise<LoginResponse> {
  const { data } = await api.get("/api/workspace/me");
  return toCamelCaseKeys(data) as LoginResponse;
}

export async function logout(): Promise<void> {
  const accessToken = getAccessToken();
  if (accessToken) {
    try {
      await axios.post(`${getCmsApiBaseUrl()}/api/authentication/logout`, {
        access_token: accessToken,
      });
    } catch {
      // Best-effort CMS logout; local token is always cleared.
    }
  }
  clearAccessToken();
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
  // api client defaults to application/json; with that set, axios JSON-serializes FormData
  // and FastAPI never receives multipart "files" (422 Field required).
  const { data } = await api.post<UploadDocumentsResponse>(
    "/api/upload/documents",
    formData,
    {
      headers: { "Content-Type": false },
    },
  );
  return toCamelCaseKeys(data) as UploadDocumentsResponse;
}

export async function listKnowledgeDocuments(): Promise<
  KnowledgeDocumentSummary[]
> {
  const { data } = await api.get<KnowledgeDocumentSummary[]>(
    "/api/knowledge/documents",
  );
  return toCamelCaseKeys(data) as KnowledgeDocumentSummary[];
}

export async function toggleKnowledgeDocument(
  documentId: string,
  isActive: boolean,
): Promise<KnowledgeDocumentSummary> {
  const { data } = await api.patch<KnowledgeDocumentSummary>(
    `/api/knowledge/documents/${documentId}`,
    null,
    { params: { is_active: isActive } },
  );
  return toCamelCaseKeys(data) as KnowledgeDocumentSummary;
}
