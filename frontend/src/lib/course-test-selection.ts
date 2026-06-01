import type { CourseGroupWithTests } from "@/api/contracts";

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

export function selectAllTestIds(
  selected: string[],
  testIds: string[],
): string[] {
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
        numQuestions: test.numQuestions,
      });
    }
  }

  return labels;
}

export function countSelectedGroups(labels: SelectedTestLabel[]): number {
  return new Set(labels.map((label) => label.groupName)).size;
}

export interface SelectedTestsByGroup {
  groupName: string;
  tests: SelectedTestLabel[];
}

export function groupSelectedTestLabels(
  labels: SelectedTestLabel[],
): SelectedTestsByGroup[] {
  const groups: SelectedTestsByGroup[] = [];
  const indexByName = new Map<string, number>();

  for (const label of labels) {
    const index = indexByName.get(label.groupName);
    if (index !== undefined) {
      groups[index].tests.push(label);
      continue;
    }
    indexByName.set(label.groupName, groups.length);
    groups.push({ groupName: label.groupName, tests: [label] });
  }

  return groups;
}

export function totalSelectedQuestions(labels: SelectedTestLabel[]): number {
  return labels.reduce((total, label) => total + label.numQuestions, 0);
}
