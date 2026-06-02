import type { ComponentPropsWithoutRef } from "react";
import { Label } from "@/components/ui/label";

const TITLE_CLASS = "font-heading text-sm font-bold text-foreground";

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
        <legend
          className={className ? `${TITLE_CLASS} ${className}` : TITLE_CLASS}
          {...rest}
        >
          {children}
        </legend>
      );
    }
    case "summary": {
      const { as, className, children, ...rest } = props;
      void as;
      return (
        <summary
          className={className ? `${TITLE_CLASS} ${className}` : TITLE_CLASS}
          {...rest}
        >
          {children}
        </summary>
      );
    }
    case "label": {
      const { as, className, children, ...rest } = props;
      void as;
      return (
        <Label
          className={className ? `${TITLE_CLASS} ${className}` : TITLE_CLASS}
          {...rest}
        >
          {children}
        </Label>
      );
    }
    case "p": {
      const { as, className, children, ...rest } = props;
      void as;
      return (
        <p
          className={className ? `${TITLE_CLASS} ${className}` : TITLE_CLASS}
          {...rest}
        >
          {children}
        </p>
      );
    }
  }
}
