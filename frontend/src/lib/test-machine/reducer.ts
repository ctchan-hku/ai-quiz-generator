import { testFormFieldDefaults } from "@/config/test-form";
import {
  canHydrateMachine,
  sanitizeMachineAfterLoad,
} from "../session-persistence";
import {
  appendQuestionVersion,
  selectQuestionVersion,
  toTestVersionedReview,
} from "../test-versioned-review";
import type { TestMachineAction, TestMachineState } from "./types";

export const initialState: TestMachineState = {
  status: "idle",
  formConfig: structuredClone(testFormFieldDefaults),
  review: null,
  battle: null,
  error: null,
  questionEdit: null,
  reviewEpoch: 0,
};

export function testMachineReducer(
  state: TestMachineState,
  action: TestMachineAction,
): TestMachineState {
  switch (action.type) {
    case "START_GENERATE":
      return {
        ...state,
        status: "generating",
        formConfig: action.payload,
        error: null,
        questionEdit: null,
      };
    case "GENERATE_SUCCESS": {
      if (action.payload.mode === "battle") {
        const { left, right } = action.payload.payload;
        return {
          ...state,
          status: "reviewing",
          review: null,
          battle: { left, right },
          error: null,
          questionEdit: null,
          reviewEpoch: state.reviewEpoch + 1,
        };
      }
      const review = toTestVersionedReview(action.payload.payload);
      return {
        ...state,
        status: "reviewing",
        review,
        battle: null,
        error: null,
        questionEdit: null,
        reviewEpoch: state.reviewEpoch + 1,
      };
    }
    case "COMMIT_BATTLE_WINNER": {
      if (state.battle == null) return state;
      const review =
        action.payload.side === "left"
          ? toTestVersionedReview(state.battle.left)
          : toTestVersionedReview(state.battle.right);
      return {
        ...state,
        battle: null,
        review,
        questionEdit: null,
        reviewEpoch: state.reviewEpoch + 1,
      };
    }
    case "GENERATE_ERROR":
      return {
        ...state,
        status: "error",
        error: action.payload,
      };
    case "GENERATE_ABORTED": {
      if (state.status !== "generating") return state;
      const hasPriorReview = state.review != null || state.battle != null;
      return {
        ...state,
        status: hasPriorReview ? "reviewing" : "idle",
        error: null,
        questionEdit: null,
      };
    }
    case "ENTER_EXPORTING":
      if (state.status !== "reviewing") return state;
      return { ...state, status: "exporting" };
    case "EXIT_EXPORTING":
      if (state.status !== "exporting") return state;
      return { ...state, status: "reviewing" };
    case "APPEND_QUESTION_VERSION": {
      if (state.status !== "reviewing" || state.review == null) {
        return state;
      }
      const review = appendQuestionVersion(
        state.review,
        action.payload.index,
        action.payload.question,
      );
      return {
        ...state,
        review,
        questionEdit: null,
      };
    }
    case "SET_QUESTION_VERSION": {
      if (state.status !== "reviewing" || state.review == null) {
        return state;
      }
      const review = selectQuestionVersion(
        state.review,
        action.payload.index,
        action.payload.selected,
      );
      if (review == null) return state;
      return {
        ...state,
        review,
      };
    }
    case "SET_FORM_CONFIG": {
      if (state.status !== "idle" && state.status !== "error") {
        return state;
      }
      const next =
        typeof action.payload === "function"
          ? action.payload(state.formConfig)
          : action.payload;
      return { ...state, formConfig: next };
    }
    case "RESET":
      return {
        ...initialState,
        formConfig:
          action.form != null
            ? structuredClone(action.form)
            : structuredClone(testFormFieldDefaults),
      };
    case "HYDRATE": {
      const next = sanitizeMachineAfterLoad(action.payload);
      return canHydrateMachine(next) ? next : state;
    }
    case "QUESTION_EDIT_START":
      if (state.status !== "reviewing") return state;
      return {
        ...state,
        questionEdit: { status: "pending", index: action.payload.index },
      };
    case "QUESTION_EDIT_ERROR":
      return {
        ...state,
        questionEdit: {
          status: "error",
          index: action.payload.index,
          message: action.payload.message,
        },
      };
    case "QUESTION_EDIT_CLEAR":
      if (state.questionEdit == null) return state;
      return { ...state, questionEdit: null };
    default:
      return state;
  }
}
