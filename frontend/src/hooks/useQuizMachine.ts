import { useMutation } from "@tanstack/react-query";
import { CanceledError, isAxiosError } from "axios";
import { useCallback, useEffect, useReducer, useRef } from "react";
import { quizFormFieldDefaults } from "../config/quiz";
import {
  generateQuiz,
  generateQuestion,
  getRequestErrorMessage,
} from "../lib/api";
import type {
  QuizFormConfig,
  QuizMachineAction,
  QuizMachineState,
  RefineQuestionParams,
} from "../types/quiz-machine";
import { buildResolvedQuizResponse as buildResolved } from "../types/quiz-machine";

const initialFormConfig: QuizFormConfig = {
  topic: quizFormFieldDefaults.topic,
  numQuestions: quizFormFieldDefaults.numQuestions,
  model: "",
};

const initialState: QuizMachineState = {
  status: "idle",
  formConfig: initialFormConfig,
  baseQuizResponse: null,
  questionVersions: null,
  selectedVersionIndex: null,
  quiz: null,
  error: null,
  reviewGeneration: 0,
};

function quizReducer(
  state: QuizMachineState,
  action: QuizMachineAction,
): QuizMachineState {
  switch (action.type) {
    case "START_GENERATE":
      return {
        ...state,
        status: "generating",
        formConfig: action.payload,
        error: null,
      };
    case "GENERATE_SUCCESS": {
      const questionVersions = action.payload.questions.map((q) => [q]);
      const selectedVersionIndex = action.payload.questions.map(() => 0);
      return {
        ...state,
        status: "reviewing",
        baseQuizResponse: action.payload,
        questionVersions,
        selectedVersionIndex,
        quiz: buildResolved(
          action.payload,
          questionVersions,
          selectedVersionIndex,
        ),
        error: null,
        reviewGeneration: state.reviewGeneration + 1,
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
      return {
        ...state,
        status: state.baseQuizResponse != null ? "reviewing" : "idle",
        error: null,
      };
    }
    case "ENTER_EXPORTING":
      if (state.status !== "reviewing") return state;
      return { ...state, status: "exporting" };
    case "EXIT_EXPORTING":
      if (state.status !== "exporting") return state;
      return { ...state, status: "reviewing" };
    case "APPEND_QUESTION_VERSION": {
      if (
        state.status !== "reviewing" ||
        state.baseQuizResponse == null ||
        state.questionVersions == null ||
        state.selectedVersionIndex == null
      ) {
        return state;
      }
      const { index, question } = action.payload;
      const newVersions = state.questionVersions.map((arr, i) =>
        i === index ? [...arr, question] : arr,
      );
      const newSelected = state.selectedVersionIndex.map((s, i) =>
        i === index ? newVersions[i].length - 1 : s,
      );
      return {
        ...state,
        questionVersions: newVersions,
        selectedVersionIndex: newSelected,
        quiz: buildResolved(state.baseQuizResponse, newVersions, newSelected),
      };
    }
    case "SET_QUESTION_VERSION": {
      if (
        state.status !== "reviewing" ||
        state.baseQuizResponse == null ||
        state.questionVersions == null ||
        state.selectedVersionIndex == null
      ) {
        return state;
      }
      const { index, selected } = action.payload;
      const slot = state.questionVersions[index];
      if (selected < 0 || selected >= slot.length) return state;
      const newSelected = state.selectedVersionIndex.map((s, i) =>
        i === index ? selected : s,
      );
      return {
        ...state,
        selectedVersionIndex: newSelected,
        quiz: buildResolved(
          state.baseQuizResponse,
          state.questionVersions,
          newSelected,
        ),
      };
    }
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

function isMutationCanceled(err: unknown): boolean {
  if (!isAxiosError(err)) return false;
  return err.code === "ERR_CANCELED" || err instanceof CanceledError;
}

export function useQuizMachine() {
  const [state, dispatch] = useReducer(quizReducer, initialState);
  const generateAbortControllerRef = useRef<AbortController | null>(null);
  const refineAbortControllerRef = useRef<AbortController | null>(null);
  const generateMutationApiRef = useRef<{ reset: () => void } | null>(null);
  const refineMutationApiRef = useRef<{ reset: () => void } | null>(null);

  const generateMutation = useMutation({
    mutationFn: (formConfig: QuizFormConfig) =>
      generateQuiz(formConfig, generateAbortControllerRef.current!.signal),
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
      generateQuestion(
        {
          model: p.model,
          topic: p.topic,
          question: p.question,
          comment: p.comment.trim(),
        },
        refineAbortControllerRef.current!.signal,
      ),
    onSuccess: (data, variables) => {
      dispatch({
        type: "APPEND_QUESTION_VERSION",
        payload: { index: variables.index, question: data },
      });
    },
    onError: (err) => {
      if (isMutationCanceled(err)) {
        refineMutationApiRef.current?.reset();
      }
    },
  });
  useEffect(() => {
    refineMutationApiRef.current = refineMutation;
  }, [refineMutation]);

  const submitGenerate = useCallback(
    (config: QuizFormConfig) => {
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

  const cancelRefine = useCallback(() => {
    refineAbortControllerRef.current?.abort();
  }, []);

  const resetRefine = useCallback(() => {
    refineMutation.reset();
  }, [refineMutation]);

  return {
    state,
    dispatch,
    submitGenerate,
    cancelGenerate,
    cancelRefine,
    isGenerating: generateMutation.isPending,
    refineQuestion,
    isRefining: refineMutation.isPending,
    refiningIndex: refineMutation.isPending
      ? (refineMutation.variables?.index ?? null)
      : null,
    refineErrorMessage:
      refineMutation.isError &&
      refineMutation.error != null &&
      refineMutation.variables != null &&
      !isMutationCanceled(refineMutation.error)
        ? getRequestErrorMessage(refineMutation.error)
        : null,
    refineErrorIndex:
      refineMutation.isError && refineMutation.variables != null
        ? refineMutation.variables.index
        : null,
    resetRefine,
  };
}
