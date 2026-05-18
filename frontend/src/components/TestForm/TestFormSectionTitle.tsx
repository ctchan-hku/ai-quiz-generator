import type { ComponentPropsWithoutRef } from "react";
import { cn } from "@/lib/cn";
import { Label } from "@/components/ui/label";

function titleClass(extra?: string) {
  return cn(
    "font-heading text-sm font-bold text-foreground",
    extra,
  );
}

type TestFormSectionTitleProps =
  | ({ as: "legend" } & ComponentPropsWithoutRef<"legend">)
  | ({ as: "p" } & ComponentPropsWithoutRef<"p">)
  | ({ as: "summary" } & ComponentPropsWithoutRef<"summary">)
  | ({ as: "label" } & ComponentPropsWithoutRef<typeof Label>);

export function TestFormSectionTitle(props: TestFormSectionTitleProps) {
  switch (props.as) {
    case "legend": {
      const { as, className, children, ...rest } = props;
      void as;
      return (
        <legend className={titleClass(className)} {...rest}>
          {children}
        </legend>
      );
    }
    case "summary": {
      const { as, className, children, ...rest } = props;
      void as;
      return (
        <summary className={titleClass(className)} {...rest}>
          {children}
        </summary>
      );
    }
    case "label": {
      const { as, className, children, ...rest } = props;
      void as;
      return (
        <Label className={titleClass(className)} {...rest}>
          {children}
        </Label>
      );
    }
    case "p": {
      const { as, className, children, ...rest } = props;
      void as;
      return (
        <p className={titleClass(className)} {...rest}>
          {children}
        </p>
      );
    }
  }
}
