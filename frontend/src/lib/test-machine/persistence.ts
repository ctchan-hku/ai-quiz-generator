/** Browser localStorage for the app session. Side effects only. */

import { loadVersioned, saveVersioned } from "@/lib/local-storage";
import type { TestMachineState } from "./types";

const SESSION_KEY = "app_session";
const SESSION_VERSION = 1;

export interface LastReviewSnapshot {
  machine: TestMachineState;
  comments: string[];
}

export interface PersistedAppSession {
  machine: TestMachineState;
  comments: string[];
  lastReview: LastReviewSnapshot | null;
}

export function hasReviewContent(s: TestMachineState): boolean {
  return s.status === "reviewing" && (s.battle != null || s.review != null);
}

export function canHydrateMachine(s: TestMachineState): boolean {
  return (
    s.status !== "generating" &&
    (s.status !== "reviewing" || hasReviewContent(s))
  );
}

export function sanitizeMachineAfterLoad(
  s: TestMachineState,
): TestMachineState {
  if (s.status === "generating") {
    return {
      status: "idle",
      formConfig: s.formConfig,
      review: null,
      battle: null,
      error: null,
      questionEdit: null,
      reviewEpoch: 0,
    };
  }
  if (s.questionEdit?.status === "pending") {
    return { ...s, questionEdit: null };
  }
  if (s.status === "reviewing" && s.battle == null && s.review == null) {
    return { ...s, status: "idle" };
  }
  return s;
}

function stringList(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((c): c is string => typeof c === "string")
    : [];
}

function parseSession(stored: PersistedAppSession): PersistedAppSession | null {
  if (stored.machine == null || typeof stored.machine !== "object") {
    return null;
  }
  const machine = sanitizeMachineAfterLoad(stored.machine);
  const lr = stored.lastReview;
  const lastReview =
    lr?.machine && hasReviewContent(lr.machine)
      ? {
          machine: sanitizeMachineAfterLoad(lr.machine),
          comments: stringList(lr.comments),
        }
      : null;
  return {
    machine,
    comments: stringList(stored.comments),
    lastReview,
  };
}

export function loadSession(): PersistedAppSession | null {
  const stored = loadVersioned<PersistedAppSession>(
    SESSION_KEY,
    SESSION_VERSION,
  );
  return stored ? parseSession(stored) : null;
}

export function saveSession(session: PersistedAppSession): void {
  saveVersioned(SESSION_KEY, SESSION_VERSION, session);
}
