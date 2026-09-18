"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { clearToken, getToken, registerUnauthorizedHandler } from "./api";

interface AuthContextValue {
  /** true once we've checked localStorage on mount, so pages don't flash
   * unauthenticated UI before we actually know the auth state. */
  isReady: boolean;
  isAuthenticated: boolean;
  logout: () => void;
  /** Call after a successful login/register so the app re-reads the token. */
  refreshAuthState: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isReady, setIsReady] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  const refreshAuthState = useCallback(() => {
    setIsAuthenticated(!!getToken());
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setIsAuthenticated(false);
    router.replace("/login");
  }, [router]);

  useEffect(() => {
    // Runs once on mount, client-side only — avoids Next.js hydration
    // mismatches from reading localStorage during SSR.
    refreshAuthState();
    setIsReady(true);

    // Any 401 from any API call anywhere in the app funnels through here,
    // so there is exactly one "session expired" flow.
    registerUnauthorizedHandler(() => {
      setIsAuthenticated(false);
      router.replace("/login?sessionExpired=1");
    });
  }, [refreshAuthState, router]);

  return (
    <AuthContext.Provider
      value={{ isReady, isAuthenticated, logout, refreshAuthState }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
