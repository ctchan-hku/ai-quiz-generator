export type ModelBoardRole =
  /** Single-model test generation (full width). */
  | "standard"
  /** Battle mode — maps to test compare left column. */
  | "battle-left"
  /** Battle mode — maps to test compare right column. */
  | "battle-right";

/** Visible section title per model board role. */
export const MODEL_BOARD_SECTION_TITLE: Record<ModelBoardRole, string> = {
  standard: "Choose model for generation",
  "battle-left": "Left Opponent",
  "battle-right": "Right Opponent",
};
