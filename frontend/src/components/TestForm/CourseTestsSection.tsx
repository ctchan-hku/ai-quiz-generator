import { useState, type Dispatch, type SetStateAction } from "react";
import { ChevronRight } from "lucide-react";

import type { LoginResponse } from "@/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { CourseGroupsList } from "@/components/Login/CourseGroupsList";
import { LoginForm } from "@/components/Login/LoginForm";
import { TestFormSectionTitle } from "./TestFormSectionTitle";

interface CourseTestsSectionProps {
  loggedInUser: LoginResponse | null;
  onLoggedInUserChange: (user: LoginResponse | null) => void;
  selectedTestIds: string[];
  onSelectedTestIdsChange: Dispatch<SetStateAction<string[]>>;
  isLoading: boolean;
}

export function CourseTestsSection({
  loggedInUser,
  onLoggedInUserChange,
  selectedTestIds,
  onSelectedTestIdsChange,
  isLoading,
}: CourseTestsSectionProps) {
  const [isOpen, setIsOpen] = useState(true);

  function handleDisconnect() {
    onLoggedInUserChange(null);
    onSelectedTestIdsChange([]);
  }

  return (
    <details
      className="mb-4 overflow-visible text-left"
      open={isOpen}
      onToggle={(event) => setIsOpen(event.currentTarget.open)}
    >
      <TestFormSectionTitle
        as="summary"
        className="flex cursor-pointer list-none items-center gap-2 [&::-webkit-details-marker]:hidden"
      >
        <ChevronRight
          className={cn(
            "h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200",
            isOpen && "rotate-90",
          )}
          aria-hidden
        />
        Course tests
        <span className="sr-only">
          {isOpen ? "Collapse section" : "Expand section"}
        </span>
      </TestFormSectionTitle>

      <div className="mt-3 space-y-4 overflow-visible">
        <p className="m-0 text-xs leading-relaxed text-muted-foreground">
          Load your course groups and select tests to use as reference examples
          for generation.
        </p>

        {loggedInUser ? (
          <>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm text-muted-foreground">
                Courses loaded for{" "}
                <span className="font-medium text-foreground">
                  {loggedInUser.username}
                </span>
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={isLoading}
                onClick={handleDisconnect}
              >
                Disconnect
              </Button>
            </div>
            <CourseGroupsList
              courseGroups={loggedInUser.course_groups}
              selectedTestIds={selectedTestIds}
              onSelectedTestIdsChange={(ids) => onSelectedTestIdsChange(ids)}
            />
          </>
        ) : (
          <LoginForm
            onSuccess={onLoggedInUserChange}
            disabled={isLoading}
          />
        )}
      </div>
    </details>
  );
}
