import {
  useCallback,
  useEffect,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";
import type { TestFormConfig } from "@/config/test-form";
import {
  canHydrateMachine,
  cloneForLastReviewSnapshot,
  isReviewingWithPayload,
  loadPersistedSession,
  savePersistedSession,
  type LastReviewSnapshot,
} from "@/lib/test-machine/persistence";
import type {
  TestMachineAction,
  TestMachineState,
} from "@/lib/test-machine/types";

interface UseAppSessionParams {
  state: TestMachineState;
  dispatch: Dispatch<TestMachineAction>;
}

export function useAppSession({ state, dispatch }: UseAppSessionParams) {
  const [comments, setComments] = useState(
    () => loadPersistedSession()?.comments ?? [],
  );
  const [syncedReviewEpoch, setSyncedReviewEpoch] = useState(
    () => loadPersistedSession()?.machine.reviewEpoch ?? 0,
  );
  const [lastReview, setLastReview] = useState<LastReviewSnapshot | null>(
    () => loadPersistedSession()?.lastReview ?? null,
  );
  const [testFormSurfaceKey, setTestFormSurfaceKey] = useState(0);

  useEffect(() => {
    const testLength =
      state.review?.questionVersions.length ??
      state.battle?.left.questions.length ??
      0;
    if (
      state.status !== "reviewing" ||
      state.reviewEpoch === syncedReviewEpoch ||
      testLength === 0
    ) {
      return;
    }
    const id = window.setTimeout(() => {
      setComments(Array.from({ length: testLength }, () => ""));
      setSyncedReviewEpoch(state.reviewEpoch);
    }, 0);
    return () => window.clearTimeout(id);
  }, [
    state.status,
    state.reviewEpoch,
    state.review?.questionVersions.length,
    state.battle?.left.questions.length,
    syncedReviewEpoch,
  ]);

  const handleCommentChange = useCallback((index: number, value: string) => {
    setComments((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  }, []);

  useEffect(() => {
    savePersistedSession({
      v: 12,
      machine: state,
      comments,
      lastReview,
    });
  }, [state, comments, lastReview]);

  const updateFormDraft = useCallback(
    (action: SetStateAction<TestFormConfig>) => {
      dispatch({ type: "SET_FORM_CONFIG", payload: action });
    },
    [dispatch],
  );

  const handleNewTest = useCallback(() => {
    if (isReviewingWithPayload(state)) {
      setLastReview(cloneForLastReviewSnapshot(state, comments));
      setTestFormSurfaceKey((k) => k + 1);
    }
    setComments([]);
    dispatch({
      type: "RESET",
      form: isReviewingWithPayload(state)
        ? structuredClone(state.formConfig)
        : undefined,
    });
  }, [state, comments, dispatch]);

  const handleViewLastTest = useCallback(() => {
    if (lastReview == null || !canHydrateMachine(lastReview.machine)) {
      return;
    }
    dispatch({
      type: "HYDRATE",
      payload: structuredClone(lastReview.machine),
    });
    setComments([...lastReview.comments]);
    setSyncedReviewEpoch(lastReview.machine.reviewEpoch);
  }, [lastReview, dispatch]);

  return {
    comments,
    lastReview,
    testFormSurfaceKey,
    handleCommentChange,
    handleNewTest,
    handleViewLastTest,
    updateFormDraft,
  };
}
