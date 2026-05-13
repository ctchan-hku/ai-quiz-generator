import { Switch } from "@/components/ui/switch";

interface BattleModeSwitchProps {
  checked: boolean;
  onCheckedChange: (next: boolean) => void;
  disabled?: boolean;
  /** Associates the switch with visible label copy for accessibility. */
  labelledBy?: string;
}

/** Accessible toggle styled as an on/off switch (`role="switch"`). */
export function BattleModeSwitch({
  checked,
  onCheckedChange,
  disabled,
  labelledBy,
}: BattleModeSwitchProps) {
  return (
    <Switch
      checked={checked}
      onCheckedChange={onCheckedChange}
      disabled={disabled}
      aria-labelledby={labelledBy}
    />
  );
}
