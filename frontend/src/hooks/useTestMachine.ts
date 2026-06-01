import { useReducer, useCallback, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { CanceledError, isAxiosError } from "axios";
import {
  loadPersistedSession,
  sanitizeMachineAfterLoad,
} from "../lib/session-persistence";
import {
  editQuestion as editQuestionApi,
  getRequestErrorMessage,
} from "../api";
import type { TestFormConfig } from "../config/test-form";
import { initialState, testMachineReducer } from "../lib/test-machine/reducer";
import { runGenerateTest } from "../lib/test-machine/generate";
import type {
  QuestionEditParams,
  TestMachineState,
} from "../lib/test-machine/types";

function isMutationCanceled(err: unknown): boolean {
  if (!isAxiosError(err)) return false;
  return err.code === "ERR_CANCELED" || err instanceof CanceledError;
}

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
  const questionEditAbortControllerRef = useRef<AbortController | null>(null);
  const generateMutationApiRef = useRef<{ reset: () => void } | null>(null);
  const questionEditMutationApiRef = useRef<{ reset: () => void } | null>(null);

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

  const questionEditMutation = useMutation({
    mutationFn: ({ comment, ...body }: QuestionEditParams) =>
      editQuestionApi(
        { ...body, comment: comment.trim() },
        questionEditAbortControllerRef.current!.signal,
      ),
    onMutate: (variables) => {
      dispatch({
        type: "QUESTION_EDIT_START",
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
        dispatch({ type: "QUESTION_EDIT_CLEAR" });
        questionEditMutationApiRef.current?.reset();
        return;
      }
      dispatch({
        type: "QUESTION_EDIT_ERROR",
        payload: {
          index: variables.index,
          message: getRequestErrorMessage(err),
        },
      });
    },
  });
  useEffect(() => {
    questionEditMutationApiRef.current = questionEditMutation;
  }, [questionEditMutation]);

  const submitGenerate = useCallback(
    (config: TestFormConfig) => {
      generateAbortControllerRef.current?.abort();
      generateAbortControllerRef.current = new AbortController();
      generateMutation.mutate(config);
    },
    [generateMutation],
  );

  const editQuestion = useCallback(
    (params: QuestionEditParams) => {
      questionEditAbortControllerRef.current?.abort();
      questionEditAbortControllerRef.current = new AbortController();
      questionEditMutation.mutate(params);
    },
    [questionEditMutation],
  );

  const cancelGenerate = useCallback(() => {
    generateAbortControllerRef.current?.abort();
  }, []);

  const commitBattleWinner = useCallback((side: "left" | "right") => {
    dispatch({ type: "COMMIT_BATTLE_WINNER", payload: { side } });
  }, []);

  const cancelQuestionEdit = useCallback(() => {
    questionEditAbortControllerRef.current?.abort();
  }, []);

  const clearQuestionEdit = useCallback(() => {
    dispatch({ type: "QUESTION_EDIT_CLEAR" });
    questionEditMutation.reset();
  }, [questionEditMutation]);

  return {
    state,
    dispatch,
    submitGenerate,
    commitBattleWinner,
    cancelGenerate,
    cancelQuestionEdit,
    isGenerating: generateMutation.isPending,
    editQuestion,
    clearQuestionEdit,
  };
}
