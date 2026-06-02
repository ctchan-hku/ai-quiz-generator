import { useState } from "react";

import type { LoginResponse } from "@/api/contracts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin } from "@/hooks/useLogin";

interface LoginFormProps {
  onSuccess: (response: LoginResponse) => void;
  disabled?: boolean;
}

export function LoginForm({ onSuccess, disabled = false }: LoginFormProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const { submit, isPending, error: errorMessage } = useLogin({ onSuccess });

  function handleLogin(event: React.FormEvent) {
    event.preventDefault();
    submit(username, password);
  }

  const isDisabled = disabled || isPending;

  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="flex flex-col gap-2">
          <Label htmlFor="course-load-username">Username</Label>
          <Input
            id="course-load-username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            disabled={isDisabled}
            required
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                handleLogin(event);
              }
            }}
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="course-load-password">Password</Label>
          <Input
            id="course-load-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={isDisabled}
            required
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                handleLogin(event);
              }
            }}
          />
        </div>
      </div>
      {errorMessage ? (
        <p className="m-0 text-sm text-destructive" role="alert">
          {errorMessage}
        </p>
      ) : null}
      <Button
        type="button"
        variant="secondary"
        disabled={isDisabled}
        onClick={handleLogin}
      >
        {isPending ? "Loading courses…" : "Load courses"}
      </Button>
    </div>
  );
}
