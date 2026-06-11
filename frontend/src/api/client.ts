import axios from "axios";
import { getAccessToken } from "@/lib/access-token";
import { getAppApiBaseUrl } from "./config";
import { HTTP_CLIENT_TIMEOUT_MS } from "./config";

export const api = axios.create({
  baseURL: getAppApiBaseUrl(),
  headers: { "Content-Type": "application/json" },
  timeout: HTTP_CLIENT_TIMEOUT_MS,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
