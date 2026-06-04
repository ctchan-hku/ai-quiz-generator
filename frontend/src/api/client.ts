import axios from "axios";
import { getSessionToken } from "@/lib/auth-session";
import { HTTP_CLIENT_TIMEOUT_MS } from "./config";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: HTTP_CLIENT_TIMEOUT_MS,
});

api.interceptors.request.use((config) => {
  const token = getSessionToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
