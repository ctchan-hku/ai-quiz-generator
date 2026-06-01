import type { TestMachineState } from "./test-machine/types";
import { testFormFieldDefaults } from "../config/test-form";

export const SESSION_STORAGE_KEY = "ai-test-generator-session-v10";

export interface LastReviewSnapshot {
  machine: TestMachineState;
  comments: string[];
}

export interface PersistedAppSession {
  v: 10;
  machine: TestMachineState;
  comments: string[];
  lastReview: LastReviewSnapshot | null;
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
    refine: null,
    reviewEpoch: 0,
  };
}

/** After reload, a stuck `generating` state has no in-flight request. */
export function sanitizeMachineAfterLoad(
  s: TestMachineState,
): TestMachineState {
  const formConfig = {
    ...testFormFieldDefaults,
    ...s.formConfig,
    selected_test_ids: Array.isArray(s.formConfig.selected_test_ids)
      ? s.formConfig.selected_test_ids
      : testFormFieldDefaults.selected_test_ids,
  };
  if (s.status === "generating") {
    return createFreshMachineFromGenerating(formConfig);
  }
  const refine = s.refine?.status === "pending" ? null : s.refine;
  return { ...s, formConfig, refine };
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

export function loadPersistedSession(): PersistedAppSession | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object") {
      return null;
    }
    const rec = parsed as Partial<PersistedAppSession>;
    if (rec.v !== 10 || rec.machine == null) {
      return null;
    }
    return {
      v: 10,
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
  } catch {
    return null;
  }
}

export function savePersistedSession(session: PersistedAppSession): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
  } catch {
    // Quota or private mode — ignore.
  }
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
