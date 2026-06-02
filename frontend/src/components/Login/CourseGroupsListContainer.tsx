import type { CourseGroupWithTests } from "@/api/contracts";
import { useCourseTestSelection } from "@/hooks/useCourseTestSelection";
import { CourseGroupsList } from "./CourseGroupsList";

export interface CourseGroupsListContainerProps {
  courseGroups: CourseGroupWithTests[];
  selectedTestIds: string[];
  onSelectedTestIdsChange: (ids: string[]) => void;
}

export function CourseGroupsListContainer({
  courseGroups,
  selectedTestIds,
  onSelectedTestIdsChange,
}: CourseGroupsListContainerProps) {
  const selection = useCourseTestSelection({
    courseGroups,
    selectedTestIds,
    onSelectedTestIdsChange,
  });

  return (
    <CourseGroupsList
      courseGroups={courseGroups}
      selectedTestIds={selectedTestIds}
      {...selection}
    />
  );
}
