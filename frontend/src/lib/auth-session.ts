const SESSION_TOKEN_KEY = "auth_session_token";

function storage(): Storage | null {
  return typeof window === "undefined" ? null : window.sessionStorage;
}

export function getSessionToken(): string | null {
  return storage()?.getItem(SESSION_TOKEN_KEY) ?? null;
}

export function setSessionToken(token: string): void {
  storage()?.setItem(SESSION_TOKEN_KEY, token);
}

export function clearSessionToken(): void {
  storage()?.removeItem(SESSION_TOKEN_KEY);
}
