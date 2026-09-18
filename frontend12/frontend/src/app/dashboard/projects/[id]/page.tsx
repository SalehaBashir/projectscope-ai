"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import {
  Badge,
  Button,
  Card,
  ErrorBanner,
  PageLoading,
} from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { analyzeAndWait } from "@/lib/endpoints";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

export default function ProjectOverviewPage() {
  const { id } = useParams<{ id: string }>();
  const { project, pipeline, loading, error, reload, refreshPipeline } =
    useProject(id);

  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  async function runAnalysis() {
    if (!project) return;
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const analysis = await analyzeAndWait(project.id, {
        description: project.description,
        budget: project.budget ?? undefined,
        platform: project.platform ?? undefined,
      });
      updatePipelineData(project.id, { analysis });
      refreshPipeline();
    } catch (err) {
      setAnalyzeError(
        err instanceof ApiError
          ? err.message
          : "Analysis failed. Please try again.",
      );
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) return <PageLoading label="Loading project..." />;
  if (error || !project)
    return <ErrorBanner message={error ?? "Project not found."} onRetry={reload} />;

  const analysis = pipeline.analysis;

  return (
    <div>
      <div className="mb-2 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{project.title}</h1>
          <p className="mt-1 text-sm text-muted">{project.description}</p>
        </div>
        <Badge tone="accent">{project.status}</Badge>
      </div>
      <div className="mb-6 flex gap-2 text-xs text-muted">
        {project.platform && <span>Platform: {project.platform}</span>}
        {project.budget && <span>· Budget: {project.budget}</span>}
      </div>

      <ProjectTabs projectId={project.id} />

      {analyzeError && (
        <div className="mb-4">
          <ErrorBanner message={analyzeError} onRetry={runAnalysis} />
        </div>
      )}

      {!analysis && (
        <Card>
          <h3 className="mb-2 font-semibold">Run AI analysis</h3>
          <p className="mb-4 text-sm text-muted">
            Extract structured requirements and features from this
            project&apos;s description using the real AI analyzer.
          </p>
          <Button variant="primary" loading={analyzing} onClick={runAnalysis}>
            {analyzing ? "Analyzing..." : "Run AI analysis"}
          </Button>
        </Card>
      )}

      {analysis && (
        <div className="space-y-6">
          <Card>
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold">Analysis summary</h3>
              <Button
                variant="secondary"
                loading={analyzing}
                onClick={runAnalysis}
              >
                Re-run analysis
              </Button>
            </div>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-xs uppercase text-muted">Project type</dt>
                <dd className="mt-1 text-sm">{analysis.project_type}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase text-muted">Users</dt>
                <dd className="mt-1 text-sm">{analysis.users.join(", ")}</dd>
              </div>
            </dl>
            {analysis.assumptions.length > 0 && (
              <div className="mt-4">
                <p className="mb-1 text-xs uppercase text-muted">
                  Assumptions
                </p>
                <ul className="list-inside list-disc text-sm text-muted">
                  {analysis.assumptions.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </div>
            )}
            {analysis.missing_information.length > 0 && (
              <div className="mt-4">
                <p className="mb-1 text-xs uppercase text-muted">
                  Missing information
                </p>
                <ul className="list-inside list-disc text-sm text-warning">
                  {analysis.missing_information.map((m, i) => (
                    <li key={i}>{m}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>

          <p className="text-sm text-muted">
            Continue through the tabs above — Requirements and Features are
            already extracted; Questions, Tasks, Cost/Timeline, Risks, MVP and
            Tech Stack are each generated with one click on their own tab.
          </p>
        </div>
      )}
    </div>
  );
}
