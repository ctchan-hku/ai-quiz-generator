import { useCallback, useMemo, useState } from "react";

import type { CourseGroupWithTests } from "@/api";
import {
  buildSelectedTestLabels,
  clearTestIds,
  countSelectedGroups,
  countSelectedInGroup,
  selectAllTestIds,
  toggleTestId,
} from "@/lib/selected-tests";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/cn";
import { SelectedTestsSummary } from "./SelectedTestsSummary";

interface CourseGroupsListProps {
  username: string;
  courseGroups: CourseGroupWithTests[];
  selectedTestIds: string[];
  onSelectedTestIdsChange: (ids: string[]) => void;
}

interface CourseGroupItemProps {
  courseGroup: CourseGroupWithTests;
  selectedTestIds: string[];
  isExpanded: boolean;
  onToggleExpand: () => void;
  onSelectedTestIdsChange: (ids: string[]) => void;
}

function CourseGroupItem({
  courseGroup,
  selectedTestIds,
  isExpanded,
  onToggleExpand,
  onSelectedTestIdsChange,
}: CourseGroupItemProps) {
  const groupTestIds = useMemo(
    () => courseGroup.tests.map((test) => test.id),
    [courseGroup.tests],
  );
  const selectedInGroup = countSelectedInGroup(selectedTestIds, groupTestIds);

  return (
    <li className="flex flex-col rounded-lg border border-border">
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
                onClick={() =>
                  onSelectedTestIdsChange(
                    selectAllTestIds(selectedTestIds, groupTestIds),
                  )
                }
              >
                Select all
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={() =>
                  onSelectedTestIdsChange(
                    clearTestIds(selectedTestIds, groupTestIds),
                  )
                }
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

                return (
                  <li key={test.id}>
                    <Label
                      htmlFor={checkboxId}
                      className={cn(
                        "flex cursor-pointer items-start gap-3 rounded-md border border-border bg-background px-3 py-2",
                        isSelected && "bg-muted/60 ring-1 ring-primary/30",
                      )}
                    >
                      <input
                        id={checkboxId}
                        type="checkbox"
                        className="mt-0.5 size-4 shrink-0 accent-primary"
                        checked={isSelected}
                        onChange={() =>
                          onSelectedTestIdsChange(
                            toggleTestId(selectedTestIds, test.id),
                          )
                        }
                      />
                      <span className="min-w-0 flex-1">
                        <span className="block text-sm font-medium text-foreground">
                          {test.name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {test.num_questions} question
                          {test.num_questions === 1 ? "" : "s"}
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

export function CourseGroupsList({
  username,
  courseGroups,
  selectedTestIds,
  onSelectedTestIdsChange,
}: CourseGroupsListProps) {
  const [expandedCourseGroupId, setExpandedCourseGroupId] = useState<
    string | null
  >(null);

  const selectedLabels = useMemo(
    () => buildSelectedTestLabels(courseGroups, selectedTestIds),
    [courseGroups, selectedTestIds],
  );
  const numSelectedGroups = countSelectedGroups(selectedLabels);

  const handleToggleExpand = useCallback((courseGroupId: string) => {
    setExpandedCourseGroupId((current) =>
      current === courseGroupId ? null : courseGroupId,
    );
  }, []);

  const handleClearAll = useCallback(() => {
    onSelectedTestIdsChange([]);
  }, [onSelectedTestIdsChange]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-xl">Course groups</CardTitle>
        <CardDescription>Signed in as {username}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <SelectedTestsSummary
          labels={selectedLabels}
          numGroups={numSelectedGroups}
          onClearAll={handleClearAll}
        />

        {courseGroups.length === 0 ? (
          <p className="m-0 text-sm text-muted-foreground">
            No course groups found for this account.
          </p>
        ) : (
          <ul className="m-0 flex list-none flex-col gap-2 p-0">
            {courseGroups.map((courseGroup) => (
              <CourseGroupItem
                key={courseGroup.id}
                courseGroup={courseGroup}
                selectedTestIds={selectedTestIds}
                isExpanded={expandedCourseGroupId === courseGroup.id}
                onToggleExpand={() => handleToggleExpand(courseGroup.id)}
                onSelectedTestIdsChange={onSelectedTestIdsChange}
              />
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
