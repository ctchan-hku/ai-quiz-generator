/** Letter (A, B, …) or numeric label for an option row by zero-based index. */
export function optionLabel(optionIndex: number): string {
  if (optionIndex < 26) {
    return String.fromCharCode(65 + optionIndex)
  }
  return String(optionIndex + 1)
}
