import { useEffect } from "react";
import { getWorkspaceMe } from "@/api";
import type { LoginResponse } from "@/api/contracts";
import { isWorkspaceEnabled } from "@/config/feature-flags";
import { clearAccessToken, getAccessToken } from "@/lib/access-token";

export function useRestoreWorkspace(
  onRestored: (user: LoginResponse) => void,
): void {
  useEffect(() => {
    if (!isWorkspaceEnabled || !getAccessToken()) {
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
        clearAccessToken();
      });
    return () => {
      cancelled = true;
    };
  }, [onRestored]);
}
