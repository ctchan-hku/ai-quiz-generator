import type { CourseGroupSummary } from "@/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface CourseGroupsListProps {
  username: string;
  courseGroups: CourseGroupSummary[];
}

export function CourseGroupsList({
  username,
  courseGroups,
}: CourseGroupsListProps) {
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
              <li
                key={courseGroup.id}
                className="rounded-lg border border-border px-3 py-2 font-medium text-foreground"
              >
                {courseGroup.name}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
