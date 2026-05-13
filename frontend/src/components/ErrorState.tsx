import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  error: string;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <Card className="border-l-4 border-l-destructive text-left">
      <CardContent className="pt-6">
        <p className="mt-0 mb-2 font-heading text-lg font-semibold text-destructive">
          Oops! Something went wrong.
        </p>
        <p className="mb-0 text-base text-foreground">{error}</p>
        {onRetry ? (
          <Button
            type="button"
            variant="secondary"
            className="mt-4"
            onClick={onRetry}
          >
            Try again
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
}
