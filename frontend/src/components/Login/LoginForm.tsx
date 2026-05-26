import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { getRequestErrorMessage, login, type LoginResponse } from "@/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface LoginFormProps {
  onSuccess: (response: LoginResponse) => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess,
  });

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    loginMutation.mutate({ username, password });
  }

  const errorMessage =
    loginMutation.isError && loginMutation.error
      ? getRequestErrorMessage(loginMutation.error)
      : null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-xl">Sign in</CardTitle>
        <CardDescription>
          Enter your credentials to view your course groups.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <div className="flex flex-col gap-2">
            <Label htmlFor="login-username">Username</Label>
            <Input
              id="login-username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              disabled={loginMutation.isPending}
              required
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="login-password">Password</Label>
            <Input
              id="login-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={loginMutation.isPending}
              required
            />
          </div>
          {errorMessage ? (
            <p className="m-0 text-sm text-destructive" role="alert">
              {errorMessage}
            </p>
          ) : null}
          <Button
            type="submit"
            className="self-start"
            disabled={loginMutation.isPending}
          >
            {loginMutation.isPending ? "Signing in…" : "Sign in"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
