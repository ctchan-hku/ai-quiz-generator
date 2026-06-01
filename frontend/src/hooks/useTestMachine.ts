import { useReducer, useCallback, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  loadPersistedSession,
  sanitizeMachineAfterLoad,
} from "../lib/session-persistence";
import { editQuestion, getRequestErrorMessage } from "../api";
import type { TestFormConfig } from "../config/test-form";
import { initialState } from "../lib/test-machine/initial-state";
import { isMutationCanceled } from "../lib/test-machine/is-mutation-canceled";
import { testMachineReducer } from "../lib/test-machine/reducer";
import { runGenerateTest } from "../lib/test-machine/run-generate-test";
import type {
  RefineQuestionParams,
  TestMachineState,
} from "../lib/test-machine/types";

export function useTestMachine() {
  const [state, dispatch] = useReducer(
    testMachineReducer,
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
