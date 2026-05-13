import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  MUTATION_DEFAULT_RETRY,
  QUERY_DEFAULT_RETRY,
} from "./config/api";
import "./index.css";
import App from "./App.tsx";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: QUERY_DEFAULT_RETRY },
    mutations: { retry: MUTATION_DEFAULT_RETRY },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
);
