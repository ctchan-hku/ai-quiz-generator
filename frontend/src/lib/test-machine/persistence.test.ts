import { describe, expect, it } from "vitest";
import { testFormFieldDefaults } from "@/config/test-form";
import type { TestMachineState } from "./types";
import {
  canHydrateMachine,
  createFreshMachineFromGenerating,
  sanitizeMachineAfterLoad,
} from "./persistence";

const idleState: TestMachineState = {
  status: "idle",
  formConfig: structuredClone(testFormFieldDefaults),
  review: null,
  battle: null,
  error: null,
  questionEdit: null,
  reviewEpoch: 0,
};

describe("sanitizeMachineAfterLoad", () => {
  it("resets generating status to idle", () => {
    const generating: TestMachineState = {
      ...idleState,
      status: "generating",
    };
    const next = sanitizeMachineAfterLoad(generating);
    expect(next.status).toBe("idle");
    expect(next.reviewEpoch).toBe(0);
  });

  it("clears pending question edit", () => {
    const withEdit: TestMachineState = {
      ...idleState,
      status: "reviewing",
      questionEdit: { status: "pending", index: 0 },
    };
    const next = sanitizeMachineAfterLoad(withEdit);
    expect(next.questionEdit).toBeNull();
  });
});

describe("canHydrateMachine", () => {
  it("rejects generating state", () => {
    expect(canHydrateMachine({ ...idleState, status: "generating" })).toBe(
      false,
    );
  });
});

describe("createFreshMachineFromGenerating", () => {
  it("preserves formConfig", () => {
    const form = { ...testFormFieldDefaults, topic: "Chem" };
    const next = createFreshMachineFromGenerating(form);
    expect(next.formConfig.topic).toBe("Chem");
  });
});
