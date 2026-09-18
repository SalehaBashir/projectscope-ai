"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Button, Card, EmptyState, ErrorBanner, PageLoading } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { getTechStack } from "@/lib/endpoints";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

export default function TechStackPage() {
  const { id } = useParams<{ id: string }>();
  const { project, pipeline, loading, error, reload, refreshPipeline } =
    useProject(id);

  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setRunError(null);
    try {
      const result = await getTechStack(id);
      updatePipelineData(id, { techStack: result });
      refreshPipeline();
    } catch (err) {
      setRunError(
        err instanceof ApiError
          ? err.message
          : "Could not get a tech stack recommendation. Please try again.",
      );
    } finally {
      setRunning(false);
    }
  }

  if (loading) return <PageLoading label="Loading..." />;
  if (error || !project)
    return <ErrorBanner message={error ?? "Project not found."} onRetry={reload} />;

  const techStack = pipeline.techStack;

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
          {techStack ? "Regenerate recommendation" : "Recommend tech stack"}
        </Button>
      </div>

      {!techStack ? (
        <EmptyState
          title="No recommendation yet"
          description="Get an AI-generated tech stack, folder structure and development guidelines based on this project's features."
          action={
            <Button variant="primary" loading={running} onClick={run}>
              Recommend tech stack
            </Button>
          }
        />
      ) : (
        <div className="space-y-6">
          <Card>
            <h3 className="mb-4 font-semibold">Recommended stack</h3>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div>
                <p className="text-xs uppercase text-muted">Frontend</p>
                <p className="mt-1 text-sm font-medium">
                  {techStack.tech_stack.frontend}
                </p>
              </div>
              <div>
                <p className="text-xs uppercase text-muted">Backend</p>
                <p className="mt-1 text-sm font-medium">
                  {techStack.tech_stack.backend}
                </p>
              </div>
              <div>
                <p className="text-xs uppercase text-muted">Database</p>
                <p className="mt-1 text-sm font-medium">
                  {techStack.tech_stack.database}
                </p>
              </div>
              <div>
                <p className="text-xs uppercase text-muted">Hosting</p>
                <p className="mt-1 text-sm font-medium">
                  {techStack.tech_stack.hosting}
                </p>
              </div>
            </div>
            <p className="mt-4 text-sm text-muted">
              {techStack.tech_stack.reasoning}
            </p>
          </Card>

          <Card>
            <h3 className="mb-3 font-semibold">Folder structure</h3>
            <ul className="space-y-1 font-mono text-xs text-muted">
              {techStack.folder_structure.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </ul>
          </Card>

          <Card>
            <h3 className="mb-3 font-semibold">Development guidelines</h3>
            <ul className="list-inside list-disc space-y-1 text-sm text-muted">
              {techStack.guidelines.map((g, i) => (
                <li key={i}>{g}</li>
              ))}
            </ul>
          </Card>
        </div>
      )}
    </div>
  );
}
