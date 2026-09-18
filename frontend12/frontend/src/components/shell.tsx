"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";
import { Button } from "./ui";

export function DashboardShell({ children }: { children: ReactNode }) {
  const { logout } = useAuth();
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-bg text-text">
      <header className="sticky top-0 z-10 border-b border-border bg-bg/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
              P
            </span>
            <span className="text-lg font-semibold">ProjectScope AI</span>
          </Link>

          <nav className="flex items-center gap-2">
            <Link
              href="/dashboard"
              className={`rounded-lg px-3 py-2 text-sm font-medium ${
                pathname === "/dashboard"
                  ? "bg-surface2 text-text"
                  : "text-muted hover:text-text"
              }`}
            >
              Dashboard
            </Link>

            <Button variant="ghost" onClick={logout}>
              Log out
            </Button>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}

const WORKSPACE_TABS = [
  { slug: "", label: "Overview" },

  // AI Analysis
  { slug: "ai-analysis", label: "AI Analysis" },

  { slug: "requirements", label: "Requirements" },
  { slug: "features", label: "Features" },
  { slug: "questions", label: "Questions" },
  { slug: "tasks", label: "Tasks" },
  { slug: "team", label: "Team" },
  { slug: "estimate", label: "Cost & Timeline" },
  { slug: "risks", label: "Risks" },
  { slug: "mvp", label: "MVP" },
  { slug: "tech-stack", label: "Tech Stack" },
  { slug: "theme", label: "Theme" },
  { slug: "start-building", label: "Start Building" },
  { slug: "report", label: "Report" },
  { slug: "feedback", label: "Feedback" },
];

export function ProjectTabs({ projectId }: { projectId: string }) {
  const pathname = usePathname();
  const base = `/dashboard/projects/${projectId}`;

  return (
    <div className="mb-6 flex flex-wrap gap-1 border-b border-border pb-3">
      {WORKSPACE_TABS.map((tab) => {
        const href = tab.slug ? `${base}/${tab.slug}` : base;
        const active = pathname === href;

        return (
          <Link
            key={tab.slug || "overview"}
            href={href}
            className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              active
                ? "bg-accent/15 text-accent2"
                : "text-muted hover:bg-surface2 hover:text-text"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}