import { describe, expect, it } from "vitest";
import { testFormFieldDefaults } from "@/config/test-form";
import { initialState, testMachineReducer } from "./reducer";

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
