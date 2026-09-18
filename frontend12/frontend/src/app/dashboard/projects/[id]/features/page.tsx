"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Badge, Card, EmptyState, PageLoading, ErrorBanner, Button } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";

const PRIORITY_TONE: Record<string, "neutral" | "accent" | "warning" | "danger"> = {
  high: "danger",
  medium: "warning",
  low: "neutral",
};

export default function FeaturesPage() {
  const { id } = useParams<{ id: string }>();
  const { project, pipeline, loading, error, reload } = useProject(id);

  if (loading) return <PageLoading label="Loading..." />;
  if (error || !project)
    return <ErrorBanner message={error ?? "Project not found."} onRetry={reload} />;

  const features = pipeline.analysis?.features ?? [];

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{project.title}</h1>
      <ProjectTabs projectId={project.id} />

      {features.length === 0 ? (
        <EmptyState
          title="No features yet"
          description="Run AI analysis from the Overview tab first — features are extracted alongside requirements."
          action={
            <Link href={`/dashboard/projects/${project.id}`}>
              <Button variant="primary">Go to Overview</Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {features.map((f) => (
            <Card key={f.id}>
              <div className="mb-2 flex items-start justify-between gap-2">
                <h3 className="font-semibold">{f.canonical_name}</h3>
                <Badge tone={PRIORITY_TONE[f.priority] ?? "neutral"}>
                  {f.priority} priority
                </Badge>
              </div>
              <p className="mb-3 text-sm text-muted">{f.description}</p>
              <div className="flex items-center gap-2 text-xs text-muted">
                <span>Complexity: {f.complexity}</span>
                <span>· Confidence: {Math.round(f.confidence * 100)}%</span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
