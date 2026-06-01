import { describe, expect, it } from "vitest";
import { testFormFieldDefaults } from "@/config/test-form";
import { testMachineReducer } from "./reducer";
import { initialState } from "./initial-state";

describe("testMachineReducer", () => {
  it("START_GENERATE sets status to generating", () => {
    const next = testMachineReducer(initialState, {
      type: "START_GENERATE",
      payload: { ...testFormFieldDefaults, topic: "Biology" },
    });
    expect(next.status).toBe("generating");
    expect(next.formConfig.topic).toBe("Biology");
    expect(next.error).toBeNull();
  });
});
