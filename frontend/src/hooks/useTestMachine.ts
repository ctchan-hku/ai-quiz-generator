import { useReducer, useCallback, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { CanceledError, isAxiosError } from "axios";
import {
  canHydrateMachine,
  loadPersistedSession,
  sanitizeMachineAfterLoad,
} from "../lib/session-persistence";
import { generateTest, editQuestion, getRequestErrorMessage } from "../api";
import {
  appendQuestionVersion,
  selectQuestionVersion,
  toVersionedTestReview,
} from "../lib/versioned-test-review";
import { testFormFieldDefaults } from "../config/test-form";
import {
  type GenerateTestMachineSuccess,
  type TestFormConfig,
  type TestMachineAction,
  type TestMachineState,
  type RefineQuestionParams,
} from "../types/test-machine";

const initialFormConfig: TestFormConfig = structuredClone(
  testFormFieldDefaults,
);

const initialState: TestMachineState = {
  status: "idle",
  formConfig: initialFormConfig,
  review: null,
  battle: null,
  error: null,
  refine: null,
  reviewEpoch: 0,
};

function testReducer(
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

function isMutationCanceled(err: unknown): boolean {
  if (!isAxiosError(err)) return false;
  return err.code === "ERR_CANCELED" || err instanceof CanceledError;
}

async function runGenerateTest(
  config: TestFormConfig,
  signal: AbortSignal,
): Promise<GenerateTestMachineSuccess> {
  if (config.battleEnabled) {
    const sharedFields = {
      topic: config.topic,
      numQuestions: config.numQuestions,
      pipeline_version: config.pipeline_version,
      few_shot_examples: config.few_shot_examples,
      user_instructions: config.user_instructions,
      selected_test_ids: config.selected_test_ids,
    };

    const singleGenerateConfig = (modelId: string): TestFormConfig => ({
      ...sharedFields,
      models: [modelId, ""],
      battleEnabled: false,
    });

    const [left, right] = await Promise.all([
      generateTest(singleGenerateConfig(config.models[0]), signal),
      generateTest(singleGenerateConfig(config.models[1]), signal),
    ]);
    return { mode: "battle", payload: { left, right } };
  }

  const test = await generateTest(config, signal);
  return { mode: "single", payload: test };
}

export function useTestMachine() {
  const [state, dispatch] = useReducer(
    testReducer,
    undefined,
    (): TestMachineState => {
      const s = loadPersistedSession();
      if (!s) {
        return initialState;
      }
      return sanitizeMachineAfterLoad(s.machine);
    },
  );
  const generateAbortControllerRef = useRef<AbortController | null>(null);
  const refineAbortControllerRef = useRef<AbortController | null>(null);
  const generateMutationApiRef = useRef<{ reset: () => void } | null>(null);
  const refineMutationApiRef = useRef<{ reset: () => void } | null>(null);

  const generateMutation = useMutation({
    mutationFn: (formConfig: TestFormConfig) =>
      runGenerateTest(formConfig, generateAbortControllerRef.current!.signal),
    onMutate: (variables) => {
      dispatch({ type: "START_GENERATE", payload: variables });
    },
    onSuccess: (data) => {
      dispatch({ type: "GENERATE_SUCCESS", payload: data });
    },
    onError: (err) => {
      if (isMutationCanceled(err)) {
        dispatch({ type: "GENERATE_ABORTED" });
        generateMutationApiRef.current?.reset();
        return;
      }
      dispatch({
        type: "GENERATE_ERROR",
        payload: getRequestErrorMessage(err),
      });
    },
  });
  useEffect(() => {
    generateMutationApiRef.current = generateMutation;
  }, [generateMutation]);

  const refineMutation = useMutation({
    mutationFn: (p: RefineQuestionParams) =>
      editQuestion(
        {
          model: p.model,
          topic: p.topic,
          question: p.question,
          comment: p.comment.trim(),
        },
        refineAbortControllerRef.current!.signal,
      ),
    onMutate: (variables) => {
      dispatch({
        type: "REFINE_START",
        payload: { index: variables.index },
      });
    },
    onSuccess: (data, variables) => {
      dispatch({
        type: "APPEND_QUESTION_VERSION",
        payload: { index: variables.index, question: data },
      });
    },
    onError: (err, variables) => {
      if (isMutationCanceled(err)) {
        dispatch({ type: "REFINE_CLEAR" });
        refineMutationApiRef.current?.reset();
        return;
      }
      dispatch({
        type: "REFINE_ERROR",
        payload: {
          index: variables.index,
          message: getRequestErrorMessage(err),
        },
      });
    },
  });
  useEffect(() => {
    refineMutationApiRef.current = refineMutation;
  }, [refineMutation]);

  const submitGenerate = useCallback(
    (config: TestFormConfig) => {
      generateAbortControllerRef.current?.abort();
      generateAbortControllerRef.current = new AbortController();
      generateMutation.mutate(config);
    },
    [generateMutation],
  );

  const refineQuestion = useCallback(
    (params: RefineQuestionParams) => {
      refineAbortControllerRef.current?.abort();
      refineAbortControllerRef.current = new AbortController();
      refineMutation.mutate(params);
    },
    [refineMutation],
  );

  const cancelGenerate = useCallback(() => {
    generateAbortControllerRef.current?.abort();
  }, []);

  const commitBattleWinner = useCallback((side: "left" | "right") => {
    dispatch({ type: "COMMIT_BATTLE_WINNER", payload: { side } });
  }, []);

  const cancelRefine = useCallback(() => {
    refineAbortControllerRef.current?.abort();
  }, []);

  const resetRefine = useCallback(() => {
    dispatch({ type: "REFINE_CLEAR" });
    refineMutation.reset();
  }, [refineMutation]);

  return {
    state,
    dispatch,
    submitGenerate,
    commitBattleWinner,
    cancelGenerate,
    cancelRefine,
    isGenerating: generateMutation.isPending,
    refineQuestion,
    resetRefine,
  };
}
