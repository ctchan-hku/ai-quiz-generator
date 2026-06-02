import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type RefObject,
} from "react";
import type { CourseGroupWithTests } from "@/api/contracts";
import {
  buildSelectedTestLabels,
  clearTestIds,
  countSelectedGroups,
  countSelectedInGroup,
  groupSelectedTestLabels,
  selectAllTestIds,
  toggleTestId,
  totalSelectedQuestions,
} from "@/lib/course-test-selection";
import { smoothScrollToNearest } from "@/lib/animations/smooth-scroll-to";
export interface SelectedTestLabel {
  testId: string;
  testName: string;
  groupName: string;
  numQuestions: number;
}

export interface SelectedTestsByGroup {
  groupName: string;
  tests: SelectedTestLabel[];
}

const COURSE_GROUP_SCROLL_TOP_OFFSET_PX = 96;

export function useCourseGroupItemScroll(
  isExpanded: boolean,
  itemRef: RefObject<HTMLElement | null>,
) {
  const wasExpandedRef = useRef(isExpanded);
  const expandButtonRef = useRef<HTMLButtonElement>(null);

  useLayoutEffect(() => {
    if (!isExpanded && wasExpandedRef.current) {
      expandButtonRef.current?.focus({ preventScroll: true });
    }
    wasExpandedRef.current = isExpanded;
  }, [isExpanded]);

  useEffect(() => {
    if (!isExpanded) return;
    const item = itemRef.current;
    if (!item) return;
    return smoothScrollToNearest(item, COURSE_GROUP_SCROLL_TOP_OFFSET_PX);
  }, [isExpanded, itemRef]);

  return { expandButtonRef };
}

export function useCourseTestSelection(params: {
  courseGroups: CourseGroupWithTests[];
  selectedTestIds: string[];
  onSelectedTestIdsChange: (ids: string[]) => void;
}) {
  const { courseGroups, selectedTestIds, onSelectedTestIdsChange } = params;

  const [expandedCourseGroupId, setExpandedCourseGroupId] = useState<
    string | null
  >(null);

  const selectedLabels = useMemo(
    () => buildSelectedTestLabels(courseGroups, selectedTestIds),
    [courseGroups, selectedTestIds],
  );

  const groupedLabels = useMemo(
    () => groupSelectedTestLabels(selectedLabels),
    [selectedLabels],
  );

  const numSelectedGroups = countSelectedGroups(selectedLabels);
  const numQuestions = totalSelectedQuestions(selectedLabels);

  const handleToggleExpand = useCallback((courseGroupId: string) => {
    setExpandedCourseGroupId((current) =>
      current === courseGroupId ? null : courseGroupId,
    );
  }, []);

  const handleClearAll = useCallback(() => {
    onSelectedTestIdsChange([]);
  }, [onSelectedTestIdsChange]);

  const handleToggleTest = useCallback(
    (testId: string) => {
      onSelectedTestIdsChange(toggleTestId(selectedTestIds, testId));
    },
    [selectedTestIds, onSelectedTestIdsChange],
  );

  const handleSelectAllInGroup = useCallback(
    (groupTestIds: string[]) => {
      onSelectedTestIdsChange(selectAllTestIds(selectedTestIds, groupTestIds));
    },
    [selectedTestIds, onSelectedTestIdsChange],
  );

  const handleClearGroup = useCallback(
    (groupTestIds: string[]) => {
      onSelectedTestIdsChange(clearTestIds(selectedTestIds, groupTestIds));
    },
    [selectedTestIds, onSelectedTestIdsChange],
  );

  const selectedInGroup = useCallback(
    (groupTestIds: string[]) =>
      countSelectedInGroup(selectedTestIds, groupTestIds),
    [selectedTestIds],
  );

  return {
    expandedCourseGroupId,
    onToggleExpand: handleToggleExpand,
    selectedLabels,
    groupedLabels,
    numSelectedGroups,
    numQuestions,
    onClearAll: handleClearAll,
    onToggleTest: handleToggleTest,
    onSelectAllInGroup: handleSelectAllInGroup,
    onClearGroup: handleClearGroup,
    selectedInGroup,
  };
}
