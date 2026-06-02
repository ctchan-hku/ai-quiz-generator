import { useRef } from "react";
import type { CourseGroupWithTests } from "@/api/contracts";
import { useCourseGroupItemScroll } from "@/hooks/useCourseTestSelection";
import type {
  SelectedTestLabel,
  SelectedTestsByGroup,
} from "@/hooks/useCourseTestSelection";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { SelectedTestsSummary } from "./SelectedTestsSummary";

const COURSE_GROUP_SCROLL_TOP_OFFSET_PX = 96;

interface CourseGroupItemProps {
  courseGroup: CourseGroupWithTests;
  selectedTestIds: string[];
  selectedInGroup: number;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onToggleTest: (testId: string) => void;
  onSelectAllInGroup: () => void;
  onClearGroup: () => void;
}

function CourseGroupItem({
  courseGroup,
  selectedTestIds,
  selectedInGroup,
  isExpanded,
  onToggleExpand,
  onToggleTest,
  onSelectAllInGroup,
  onClearGroup,
}: CourseGroupItemProps) {
  const itemRef = useRef<HTMLLIElement>(null);
  const { expandButtonRef } = useCourseGroupItemScroll(isExpanded, itemRef);

  return (
    <li
      ref={itemRef}
      className="flex flex-col rounded-lg border border-border"
      style={{ scrollMarginTop: COURSE_GROUP_SCROLL_TOP_OFFSET_PX }}
    >
      <div className="flex items-center justify-between gap-3 px-3 py-2">
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <span className="min-w-0 truncate font-medium text-foreground">
            {courseGroup.name}
          </span>
          {selectedInGroup > 0 ? (
            <Badge variant="secondary" className="shrink-0">
              {selectedInGroup} / {courseGroup.tests.length} selected
            </Badge>
          ) : null}
        </div>
        <Button
          ref={expandButtonRef}
          type="button"
          variant="secondary"
          size="sm"
          className="h-7 shrink-0 px-2 text-xs"
          onClick={onToggleExpand}
          aria-expanded={isExpanded}
        >
          {isExpanded ? "Collapse" : "Expand"}
        </Button>
      </div>

      {isExpanded ? (
        <div className="border-t border-border bg-muted/20 px-3 py-3">
          {courseGroup.tests.length > 0 ? (
            <div className="mb-3 flex flex-wrap gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={onSelectAllInGroup}
              >
                Select all
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={onClearGroup}
                disabled={selectedInGroup === 0}
              >
                Clear
              </Button>
            </div>
          ) : null}

          {courseGroup.tests.length === 0 ? (
            <p className="m-0 text-sm text-muted-foreground">
              No tests found for this course group.
            </p>
          ) : (
            <ul className="m-0 flex list-none flex-col gap-2 p-0">
              {courseGroup.tests.map((test) => {
                const isSelected = selectedTestIds.includes(test.id);
                const checkboxId = `course-test-${test.id}`;
                const rowClass = isSelected
                  ? "flex cursor-pointer items-start gap-3 rounded-md border border-border bg-muted/60 px-3 py-2 ring-1 ring-primary/30"
                  : "flex cursor-pointer items-start gap-3 rounded-md border border-border bg-background px-3 py-2";

                return (
                  <li key={test.id}>
                    <Label htmlFor={checkboxId} className={rowClass}>
                      <input
                        id={checkboxId}
                        type="checkbox"
                        className="mt-0.5 size-4 shrink-0 accent-primary"
                        checked={isSelected}
                        onChange={() => onToggleTest(test.id)}
                      />
                      <span className="min-w-0 flex-1">
                        <span className="block text-sm font-medium text-foreground">
                          {test.name}
                        </span>
                        <span className="block text-xs text-muted-foreground">
                          {test.numQuestions} question
                          {test.numQuestions === 1 ? "" : "s"}
                        </span>
                      </span>
                    </Label>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      ) : null}
    </li>
  );
}

export interface CourseGroupsListProps {
  courseGroups: CourseGroupWithTests[];
  selectedTestIds: string[];
  expandedCourseGroupId: string | null;
  onToggleExpand: (courseGroupId: string) => void;
  selectedLabels: SelectedTestLabel[];
  groupedLabels: SelectedTestsByGroup[];
  numSelectedGroups: number;
  numQuestions: number;
  onClearAll: () => void;
  onToggleTest: (testId: string) => void;
  onSelectAllInGroup: (groupTestIds: string[]) => void;
  onClearGroup: (groupTestIds: string[]) => void;
  selectedInGroup: (groupTestIds: string[]) => number;
}

export function CourseGroupsList({
  courseGroups,
  selectedTestIds,
  expandedCourseGroupId,
  onToggleExpand,
  selectedLabels,
  groupedLabels,
  numSelectedGroups,
  numQuestions,
  onClearAll,
  onToggleTest,
  onSelectAllInGroup,
  onClearGroup,
  selectedInGroup,
}: CourseGroupsListProps) {
  return (
    <div className="flex flex-col gap-4 overflow-visible lg:flex-row lg:items-start">
      <div className="min-w-0 flex-1">
        {courseGroups.length === 0 ? (
          <p className="m-0 text-sm text-muted-foreground">
            No course groups found for this account.
          </p>
        ) : (
          <ul className="m-0 flex list-none flex-col gap-2 p-0">
            {courseGroups.map((courseGroup) => {
              const groupTestIds = courseGroup.tests.map((test) => test.id);
              return (
                <CourseGroupItem
                  key={courseGroup.id}
                  courseGroup={courseGroup}
                  selectedTestIds={selectedTestIds}
                  selectedInGroup={selectedInGroup(groupTestIds)}
                  isExpanded={expandedCourseGroupId === courseGroup.id}
                  onToggleExpand={() => onToggleExpand(courseGroup.id)}
                  onToggleTest={onToggleTest}
                  onSelectAllInGroup={() => onSelectAllInGroup(groupTestIds)}
                  onClearGroup={() => onClearGroup(groupTestIds)}
                />
              );
            })}
          </ul>
        )}
      </div>

      <aside
        className="w-full shrink-0 self-start lg:sticky lg:top-24 lg:z-10 lg:w-72"
        aria-label="Selected reference tests"
      >
        <SelectedTestsSummary
          labels={selectedLabels}
          groupedLabels={groupedLabels}
          numGroups={numSelectedGroups}
          numQuestions={numQuestions}
          onClearAll={onClearAll}
        />
      </aside>
    </div>
  );
}
