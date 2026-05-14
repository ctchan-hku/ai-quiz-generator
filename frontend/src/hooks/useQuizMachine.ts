import { useReducer, useCallback, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { CanceledError, isAxiosError } from "axios";
import {
  canHydrateMachine,
  loadPersistedSession,
  sanitizeMachineAfterLoad,
} from "../lib/session-persistence";
import {
  generateQuiz,
  generateQuestion,
  getRequestErrorMessage,
} from "../api";
import { quizFormFieldDefaults } from "../config/quiz-form";
import {
  buildResolvedQuizResponse as buildResolved,
  type GenerateQuizMachineSuccess,
  type QuizFormConfig,
  type QuizMachineAction,
  type QuizMachineState,
  type RefineQuestionParams,
} from "../types/quiz-machine";

const initialFormConfig: QuizFormConfig = structuredClone(quizFormFieldDefaults);

const initialState: QuizMachineState = {
  status: "idle",
  formConfig: initialFormConfig,
  baseQuizResponse: null,
  questionVersions: null,
  selectedVersionIndex: null,
  quiz: null,
  battle: null,
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
      if (action.payload.mode === "battle") {
        const { left, right } = action.payload.payload;
        const leftVersions = left.questions.map((q) => [q]);
        const rightVersions = right.questions.map((q) => [q]);
        const leftSelected = left.questions.map(() => 0);
        const rightSelected = right.questions.map(() => 0);
        return {
          ...state,
          status: "reviewing",
          baseQuizResponse: null,
          questionVersions: null,
          selectedVersionIndex: null,
          quiz: null,
          battle: {
            left: {
              baseQuizResponse: left,
              questionVersions: leftVersions,
              selectedVersionIndex: leftSelected,
            },
            right: {
              baseQuizResponse: right,
              questionVersions: rightVersions,
              selectedVersionIndex: rightSelected,
            },
          },
          error: null,
          reviewGeneration: state.reviewGeneration + 1,
        };
      }
      const quizResponse = action.payload.payload;
      const questionVersions = quizResponse.questions.map((q) => [q]);
      const selectedVersionIndex = quizResponse.questions.map(() => 0);
      return {
        ...state,
        status: "reviewing",
        baseQuizResponse: quizResponse,
        questionVersions,
        selectedVersionIndex,
        quiz: buildResolved(
          quizResponse,
          questionVersions,
          selectedVersionIndex,
        ),
        battle: null,
        error: null,
        reviewGeneration: state.reviewGeneration + 1,
      };
    }
    case "COMMIT_BATTLE_WINNER": {
      if (state.battle == null) return state;
      const branch =
        action.payload.side === "left" ? state.battle.left : state.battle.right;
      return {
        ...state,
        battle: null,
        baseQuizResponse: branch.baseQuizResponse,
        questionVersions: branch.questionVersions,
        selectedVersionIndex: branch.selectedVersionIndex,
        quiz: buildResolved(
          branch.baseQuizResponse,
          branch.questionVersions,
          branch.selectedVersionIndex,
        ),
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
      const hasPriorReview =
        state.baseQuizResponse != null || state.battle != null;
      return {
        ...state,
        status: hasPriorReview ? "reviewing" : "idle",
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
      return {
        ...initialState,
        formConfig: structuredClone(quizFormFieldDefaults),
      };
    case "HYDRATE": {
      const next = sanitizeMachineAfterLoad(action.payload);
      return canHydrateMachine(next) ? next : state;
    }
    default:
      return state;
  }
}

function isMutationCanceled(err: unknown): boolean {
  if (!isAxiosError(err)) return false;
  return err.code === "ERR_CANCELED" || err instanceof CanceledError;
}

async function runGenerateQuiz(
  config: QuizFormConfig,
  signal: AbortSignal,
): Promise<GenerateQuizMachineSuccess> {
  const primary = config.models[0].trim();
  const opponent = config.models[1].trim();
  const hasBattlePair =
    config.battleEnabled && opponent.length > 0 && opponent !== primary;

  if (hasBattlePair) {
    const sharedFields = {
      topic: config.topic,
      numQuestions: config.numQuestions,
      pipeline_version: config.pipeline_version,
      few_shot_examples: config.few_shot_examples,
      user_instructions: config.user_instructions,
    };

    const singleGenerateConfig = (modelId: string): QuizFormConfig => ({
      ...sharedFields,
      models: [modelId, ""],
      battleEnabled: false,
    });

    const [left, right] = await Promise.all([
      generateQuiz(singleGenerateConfig(primary), signal),
      generateQuiz(singleGenerateConfig(opponent), signal),
    ]);
    return { mode: "battle", payload: { left, right } };
  }

  const quiz = await generateQuiz(config, signal);
  return { mode: "single", payload: quiz };
}

export function useQuizMachine() {
  const [state, dispatch] = useReducer(
    quizReducer,
    undefined,
    (): QuizMachineState => {
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
    mutationFn: (formConfig: QuizFormConfig) =>
      runGenerateQuiz(formConfig, generateAbortControllerRef.current!.signal),
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

  const commitBattleWinner = useCallback((side: "left" | "right") => {
    dispatch({ type: "COMMIT_BATTLE_WINNER", payload: { side } });
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
    commitBattleWinner,
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
