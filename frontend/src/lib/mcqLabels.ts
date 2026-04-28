/** Option row label — letters A-Z for indexes 0..25 (backend allows up to 6). */
export function mcqOptionLabel(optionIndex: number): string {
  if (optionIndex < 26) {
    return String.fromCharCode(65 + optionIndex)
  }
  return String(optionIndex + 1)
}
