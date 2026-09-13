import type { ReactNode } from "react";

export type VisualModeOption<T extends string = string> = {
  id: T;
  label: string;
  shortLabel?: string;
};

export type UtilityItem = {
  id: string;
  label: string;
  icon: ReactNode;
};

export type RailItem = {
  id: string;
  index?: string;
  label: string;
  accent?: string;
};
