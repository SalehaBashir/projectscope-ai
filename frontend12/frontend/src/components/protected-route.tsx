"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { PageLoading } from "./ui";

/**
 * Wrap any protected page/layout with this. It never renders the
 * protected content until we've actually checked localStorage for a
 * token (isReady), which avoids a flash of protected UI followed by a
 * redirect, and avoids firing API requests before the token exists.
 */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isReady, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isReady && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isReady, isAuthenticated, router]);

  if (!isReady || !isAuthenticated) {
    return <PageLoading label="Checking your session..." />;
  }

  return <>{children}</>;
}
