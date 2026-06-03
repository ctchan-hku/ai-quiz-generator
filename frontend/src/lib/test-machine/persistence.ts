/** Browser localStorage for the app session. Side effects only. */

import { loadFromLocalStorage, saveToLocalStorage } from "@/lib/local-storage";
import type { TestMachineState } from "./types";

export const SESSION_STORAGE_KEY = "ai-test-generator-session-v12";

export interface LastReviewSnapshot {
  machine: TestMachineState;
  comments: string[];
}

export interface PersistedAppSession {
  v: 12;
  machine: TestMachineState;
  comments: string[];
  lastReview: LastReviewSnapshot | null;
}

function parseSession(parsed: unknown): PersistedAppSession | null {
  if (!parsed || typeof parsed !== "object") {
    return null;
  }
  const rec = parsed as Partial<PersistedAppSession>;
  if (rec.v !== 12 || rec.machine == null) {
    return null;
  }
  return {
    v: 12,
    machine: sanitizeMachineAfterLoad(rec.machine),
    comments: Array.isArray(rec.comments)
      ? rec.comments.filter((c): c is string => typeof c === "string")
      : [],
    lastReview:
      rec.lastReview &&
      rec.lastReview.machine &&
      isReviewingWithPayload(rec.lastReview.machine)
        ? {
            machine: sanitizeMachineAfterLoad(rec.lastReview.machine),
            comments: Array.isArray(rec.lastReview.comments)
              ? rec.lastReview.comments.filter(
                  (c): c is string => typeof c === "string",
                )
              : [],
          }
        : null,
  };
}

export function loadSession(): PersistedAppSession | null {
  return loadFromLocalStorage(SESSION_STORAGE_KEY, parseSession, null);
}

export function cloneForLastReviewSnapshot(
  state: TestMachineState,
  comments: string[],
): LastReviewSnapshot {
  return {
    machine: structuredClone(state),
    comments: [...comments],
  };
}

export function createFreshMachineFromGenerating(
  formConfig: TestMachineState["formConfig"],
): TestMachineState {
  return {
    status: "idle",
    formConfig,
    review: null,
    battle: null,
    error: null,
    questionEdit: null,
    reviewEpoch: 0,
  };
}

/** After reload, in-flight generate/edit requests are gone. */
export function sanitizeMachineAfterLoad(
  s: TestMachineState,
): TestMachineState {
  if (s.status === "generating") {
    return createFreshMachineFromGenerating(s.formConfig);
  }
  if (s.questionEdit?.status === "pending") {
    return { ...s, questionEdit: null };
  }
  return s;
}

export function isReviewingWithPayload(s: TestMachineState): boolean {
  if (s.status !== "reviewing") {
    return false;
  }
  if (s.battle != null) {
    return true;
  }
  return s.review != null;
}

export function canHydrateMachine(s: TestMachineState): boolean {
  if (s.status === "generating") {
    return false;
  }
  if (s.status === "reviewing") {
    return isReviewingWithPayload(s);
  }
  return true;
}

export function saveSession(session: PersistedAppSession): void {
  saveToLocalStorage(SESSION_STORAGE_KEY, session);
}
