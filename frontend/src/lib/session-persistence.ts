import type { QuizMachineState } from "../types/quiz-machine";

export const SESSION_STORAGE_KEY = "ai-quiz-generator-session-v5";

export interface LastReviewSnapshot {
  machine: QuizMachineState;
  comments: string[];
}

export interface PersistedAppSession {
  v: 5;
  machine: QuizMachineState;
  comments: string[];
  lastReview: LastReviewSnapshot | null;
}

export function createFreshMachineFromGenerating(
  formConfig: QuizMachineState["formConfig"],
): QuizMachineState {
  return {
    status: "idle",
    formConfig,
    baseQuizResponse: null,
    questionVersions: null,
    selectedVersionIndex: null,
    quiz: null,
    battle: null,
    error: null,
    reviewGeneration: 0,
  };
}

/** After reload, a stuck `generating` state has no in-flight request. */
export function sanitizeMachineAfterLoad(
  s: QuizMachineState,
): QuizMachineState {
  if (s.status === "generating") {
    return createFreshMachineFromGenerating(s.formConfig);
  }
  return s;
}

export function isReviewingWithPayload(s: QuizMachineState): boolean {
  if (s.status !== "reviewing") {
    return false;
  }
  if (s.battle != null) {
    return true;
  }
  return (
    s.quiz != null &&
    s.questionVersions != null &&
    s.selectedVersionIndex != null
  );
}

export function canHydrateMachine(s: QuizMachineState): boolean {
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
    if (rec.v !== 5 || rec.machine == null) {
      return null;
    }
    return {
      v: 5,
      machine: sanitizeMachineAfterLoad(rec.machine as QuizMachineState),
      comments: Array.isArray(rec.comments)
        ? rec.comments.filter((c): c is string => typeof c === "string")
        : [],
      lastReview:
        rec.lastReview &&
        rec.lastReview.machine &&
        isReviewingWithPayload(rec.lastReview.machine as QuizMachineState)
          ? {
              machine: sanitizeMachineAfterLoad(
                rec.lastReview.machine as QuizMachineState,
              ),
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
  state: QuizMachineState,
  comments: string[],
): LastReviewSnapshot {
  return {
    machine: structuredClone(state),
    comments: [...comments],
  };
}
