import type { CourseGroupWithTests } from "@/api";

export interface SelectedTestLabel {
  testId: string;
  testName: string;
  groupName: string;
  numQuestions: number;
}

export function toggleTestId(selected: string[], testId: string): string[] {
  if (selected.includes(testId)) {
    return selected.filter((id) => id !== testId);
  }
  return [...selected, testId];
}

export function selectAllTestIds(selected: string[], testIds: string[]): string[] {
  const next = new Set(selected);
  for (const testId of testIds) {
    next.add(testId);
  }
  return [...next];
}

export function clearTestIds(selected: string[], testIds: string[]): string[] {
  const remove = new Set(testIds);
  return selected.filter((id) => !remove.has(id));
}

export function countSelectedInGroup(
  selected: string[],
  groupTestIds: string[],
): number {
  const selectedSet = new Set(selected);
  return groupTestIds.filter((id) => selectedSet.has(id)).length;
}

export function buildSelectedTestLabels(
  courseGroups: CourseGroupWithTests[],
  selected: string[],
): SelectedTestLabel[] {
  const selectedSet = new Set(selected);
  const labels: SelectedTestLabel[] = [];

  for (const courseGroup of courseGroups) {
    for (const test of courseGroup.tests) {
      if (!selectedSet.has(test.id)) {
        continue;
      }
      labels.push({
        testId: test.id,
        testName: test.name,
        groupName: courseGroup.name,
        numQuestions: test.num_questions,
      });
    }
  }

  return labels;
}

export function countSelectedGroups(labels: SelectedTestLabel[]): number {
  return new Set(labels.map((label) => label.groupName)).size;
}
