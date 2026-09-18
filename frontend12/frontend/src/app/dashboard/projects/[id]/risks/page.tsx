"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Button, Card, EmptyState, ErrorBanner, PageLoading } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { generateRisks } from "@/lib/endpoints";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

const SEVERITY_TONE: Record<string, "neutral" | "warning" | "danger" | "success"> = {
  low: "success",
  medium: "warning",
  high: "danger",
  critical: "danger",
};

export default function RisksPage() {
  const { id } = useParams<{ id: string }>();
  const { project, pipeline, loading, error, reload, refreshPipeline } =
    useProject(id);

  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setRunError(null);
    try {
      const risks = await generateRisks(id);
      updatePipelineData(id, { risks });
      refreshPipeline();
    } catch (err) {
      setRunError(
        err instanceof ApiError ? err.message : "Could not generate risks.",
      );
    } finally {
      setRunning(false);
    }
  }

  if (loading) return <PageLoading label="Loading..." />;
  if (error || !project)
    return <ErrorBanner message={error ?? "Project not found."} onRetry={reload} />;

  const risks = pipeline.risks ?? [];

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{project.title}</h1>
      <ProjectTabs projectId={project.id} />

      {runError && (
        <div className="mb-4">
          <ErrorBanner message={runError} onRetry={run} />
        </div>
      )}

      <div className="mb-4 flex justify-end">
        <Button variant="secondary" loading={running} onClick={run}>
          {risks.length > 0 ? "Regenerate risks" : "Identify risks"}
        </Button>
      </div>

      {risks.length === 0 ? (
        <EmptyState
          title="No risks identified yet"
          description="Run the risk engine to surface project-specific risks with mitigations."
          action={
            <Button variant="primary" loading={running} onClick={run}>
              Identify risks
            </Button>
          }
        />
      ) : (
        <div className="space-y-3">
          {risks.map((r) => (
            <Card key={r.id}>
              <div className="mb-2 flex items-start justify-between gap-2">
                <h3 className="font-medium">{r.description}</h3>
                <Badge tone={SEVERITY_TONE[r.severity] ?? "neutral"}>
                  {r.severity}
                </Badge>
              </div>
              <div className="mb-2 flex gap-3 text-xs text-muted">
                <span>Category: {r.category}</span>
                <span>Probability: {r.probability}</span>
                <span>Impact: {r.impact}</span>
                <span>Score: {r.risk_score}</span>
              </div>
              <p className="text-sm text-muted">
                <span className="font-medium text-text">Mitigation: </span>
                {r.mitigation}
              </p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
