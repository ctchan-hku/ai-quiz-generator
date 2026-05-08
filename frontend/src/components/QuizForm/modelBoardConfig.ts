export type ModelBoardRole =
  /** Single-model quiz generation (full width). */
  | "standard"
  /** Battle mode — maps to quiz compare left column. */
  | "battle-left"
  /** Battle mode — maps to quiz compare right column. */
  | "battle-right";

interface ModelBoardRoleLabels {
  legendSr: string;
  titleBold: string;
  radioGroupAria: string;
}

export const MODEL_BOARD_CONFIG: Record<ModelBoardRole, ModelBoardRoleLabels> = {
  standard: {
    legendSr: "Choose a model",
    titleBold: "Model leaderboard",
    radioGroupAria: "Model choice",
  },
  "battle-left": {
    legendSr: "Choose Left Opponent model",
    titleBold: "Left Opponent",
    radioGroupAria: "Left Opponent model",
  },
  "battle-right": {
    legendSr: "Choose Right Opponent model",
    titleBold: "Right Opponent",
    radioGroupAria: "Right Opponent model",
  },
};
