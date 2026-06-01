import { testFormFieldDefaults } from "../../config/test-form";
import type { TestMachineState } from "./types";

export const initialState: TestMachineState = {
  status: "idle",
  formConfig: structuredClone(testFormFieldDefaults),
  review: null,
  battle: null,
  error: null,
  questionEdit: null,
  reviewEpoch: 0,
};
