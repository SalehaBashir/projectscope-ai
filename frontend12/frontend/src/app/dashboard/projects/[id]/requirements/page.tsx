"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import {
  Badge,
  Card,
  EmptyState,
  PageLoading,
  ErrorBanner,
  Button,
} from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";

const CATEGORY_TONE: Record<
  string,
  "neutral" | "accent" | "warning" | "success"
> = {
  functional: "accent",
  non_functional: "success",
  integration: "warning",
  constraint: "neutral",
};

export default function RequirementsPage() {
  const { id } = useParams<{ id: string }>();
  const { project, pipeline, loading, error, reload } = useProject(id);

  const [selectedRequirement, setSelectedRequirement] = useState<{
    id: string;
    description: string;
    category: string;
  } | null>(null);

  if (loading) {
    return <PageLoading label="Loading..." />;
  }

  if (error || !project) {
    return (
      <ErrorBanner
        message={error ?? "Project not found."}
        onRetry={reload}
      />
    );
  }

  const requirements = pipeline.analysis?.requirements ?? [];

  return (
    <div>
      {/* Page Header */}
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">{project.title}</h1>
        <p className="mt-1 text-sm text-muted">
          Extracted and structured project requirements
        </p>
      </div>

      {/* Project Navigation */}
      <ProjectTabs projectId={project.id} />

      {requirements.length === 0 ? (
        <EmptyState
          title="No requirements yet"
          description="Run AI analysis from the Overview tab first — requirements are extracted from your project description."
          action={
            <Link href={`/dashboard/projects/${project.id}`}>
              <Button variant="primary">Go to Overview</Button>
            </Link>
          }
        />
      ) : (
        <Card className="overflow-hidden p-0">
          {/* Table Header */}
          <div className="grid grid-cols-[1fr_180px_150px] border-b border-border bg-surface/60 px-5 py-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-muted">
              Requirement
            </div>

            <div className="text-xs font-semibold uppercase tracking-wide text-muted">
              Type
            </div>

            <div className="text-xs font-semibold uppercase tracking-wide text-muted">
              Status
            </div>
          </div>

          {/* Requirements */}
          <div className="divide-y divide-border">
            {requirements.map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() =>
                  setSelectedRequirement({
                    id: r.id,
                    description: r.description,
                    category: r.category,
                  })
                }
                className="grid w-full grid-cols-[1fr_180px_150px] items-center gap-4 px-5 py-4 text-left transition hover:bg-surface/60"
              >
                {/* Requirement */}
                <div className="min-w-0">
                  <p className="text-sm font-medium leading-6 text-text">
                    {r.description}
                  </p>

                  <p className="mt-1 text-xs text-muted">
                    ID: {r.id.slice(0, 8)}
                  </p>
                </div>

                {/* Type */}
                <div>
                  <Badge
                    tone={CATEGORY_TONE[r.category] ?? "neutral"}
                  >
                    {r.category.replace("_", " ")}
                  </Badge>
                </div>

                {/* Status */}
                <div>
                  <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 text-xs font-medium text-muted">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    Identified
                  </span>
                </div>
              </button>
            ))}
          </div>
        </Card>
      )}

      {/* Requirement Details Modal */}
      {selectedRequirement && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
          onClick={() => setSelectedRequirement(null)}
        >
          <div
            className="w-full max-w-lg rounded-xl border border-border bg-surface p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold">
                  Requirement Details
                </h2>

                <p className="mt-1 text-xs text-muted">
                  Requirement ID: {selectedRequirement.id}
                </p>
              </div>

              <button
                type="button"
                onClick={() => setSelectedRequirement(null)}
                className="text-xl text-muted transition hover:text-text"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {/* Type */}
            <div className="mb-5">
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted">
                Type
              </p>

              <Badge
                tone={
                  CATEGORY_TONE[selectedRequirement.category] ?? "neutral"
                }
              >
                {selectedRequirement.category.replace("_", " ")}
              </Badge>
            </div>

            {/* Status */}
            <div className="mb-5">
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted">
                Status
              </p>

              <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 text-xs font-medium text-muted">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                Identified
              </span>
            </div>

            {/* Description */}
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted">
                Description
              </p>

              <div className="rounded-lg border border-border bg-background/40 p-4">
                <p className="text-sm leading-6">
                  {selectedRequirement.description}
                </p>
              </div>
            </div>

            {/* Close */}
            <div className="mt-6 flex justify-end">
              <Button
                variant="secondary"
                onClick={() => setSelectedRequirement(null)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}