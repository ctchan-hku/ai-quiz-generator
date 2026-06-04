import { useEffect } from "react";
import { getWorkspaceMe } from "@/api";
import type { LoginResponse } from "@/api/contracts";
import { clearSessionToken, getSessionToken } from "@/lib/auth-session";

export function useRestoreWorkspace(
  onRestored: (user: LoginResponse) => void,
): void {
  useEffect(() => {
    if (!getSessionToken()) {
      return;
    }
    let cancelled = false;
    getWorkspaceMe()
      .then((user) => {
        if (!cancelled) {
          onRestored(user);
        }
      })
      .catch(() => {
        clearSessionToken();
      });
    return () => {
      cancelled = true;
    };
  }, [onRestored]);
}
