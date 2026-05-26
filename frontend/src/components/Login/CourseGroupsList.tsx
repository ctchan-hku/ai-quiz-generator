import { useCallback, useState } from "react";

import type { CourseGroupWithTests } from "@/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface CourseGroupsListProps {
  username: string;
  courseGroups: CourseGroupWithTests[];
}

interface CourseGroupItemProps {
  courseGroup: CourseGroupWithTests;
  isExpanded: boolean;
  onToggle: () => void;
}

function CourseGroupItem({
  courseGroup,
  isExpanded,
  onToggle,
}: CourseGroupItemProps) {
  return (
    <li className="flex flex-col rounded-lg border border-border">
      <div className="flex items-center justify-between gap-3 px-3 py-2">
        <span className="min-w-0 truncate font-medium text-foreground">
          {courseGroup.name}
        </span>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="h-7 shrink-0 px-2 text-xs"
          onClick={onToggle}
          aria-expanded={isExpanded}
        >
          {isExpanded ? "Collapse" : "Expand"}
        </Button>
      </div>

      {isExpanded ? (
        <div className="border-t border-border bg-muted/20 px-3 py-3">
          {courseGroup.tests.length === 0 ? (
            <p className="m-0 text-sm text-muted-foreground">
              No tests found for this course group.
            </p>
          ) : (
            <ul className="m-0 flex list-none flex-col gap-2 p-0">
              {courseGroup.tests.map((test) => (
                <li
                  key={test.id}
                  className="rounded-md border border-border bg-background px-3 py-2"
                >
                  <span className="block text-sm font-medium text-foreground">
                    {test.name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {test.num_questions} question
                    {test.num_questions === 1 ? "" : "s"}
                  </span>
                </li>
              ))}
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
}: CourseGroupsListProps) {
  const [expandedCourseGroupId, setExpandedCourseGroupId] = useState<
    string | null
  >(null);

  const handleToggle = useCallback((courseGroupId: string) => {
    setExpandedCourseGroupId((current) =>
      current === courseGroupId ? null : courseGroupId,
    );
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-xl">Course groups</CardTitle>
        <CardDescription>Signed in as {username}</CardDescription>
      </CardHeader>
      <CardContent>
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
                isExpanded={expandedCourseGroupId === courseGroup.id}
                onToggle={() => handleToggle(courseGroup.id)}
              />
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
