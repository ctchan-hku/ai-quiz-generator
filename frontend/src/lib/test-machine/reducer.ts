import { testFormFieldDefaults } from "../../config/test-form";
import {
  canHydrateMachine,
  sanitizeMachineAfterLoad,
} from "../session-persistence";
import {
  appendQuestionVersion,
  selectQuestionVersion,
  toVersionedTestReview,
} from "../versioned-test-review";
import { initialState } from "./initial-state";
import type { TestMachineAction, TestMachineState } from "./types";

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
        refine: null,
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
          refine: null,
          reviewEpoch: state.reviewEpoch + 1,
        };
      }
      const review = toVersionedTestReview(action.payload.payload);
      return {
        ...state,
        status: "reviewing",
        review,
        battle: null,
        error: null,
        refine: null,
        reviewEpoch: state.reviewEpoch + 1,
      };
    }
    case "COMMIT_BATTLE_WINNER": {
      if (state.battle == null) return state;
      const review =
        action.payload.side === "left"
          ? toVersionedTestReview(state.battle.left)
          : toVersionedTestReview(state.battle.right);
      return {
        ...state,
        battle: null,
        review,
        refine: null,
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
        refine: null,
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
        refine: null,
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
    case "REFINE_START":
      if (state.status !== "reviewing") return state;
      return {
        ...state,
        refine: { status: "pending", index: action.payload.index },
      };
    case "REFINE_ERROR":
      return {
        ...state,
        refine: {
          status: "error",
          index: action.payload.index,
          message: action.payload.message,
        },
      };
    case "REFINE_CLEAR":
      if (state.refine == null) return state;
      return { ...state, refine: null };
    default:
      return state;
  }
}
