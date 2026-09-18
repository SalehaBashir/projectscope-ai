"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Button, Card, ErrorBanner, PageLoading } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { getMvpRecommendation } from "@/lib/endpoints";
import type { MvpFeature, MvpResult } from "@/lib/types";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

function FeatureList({ title, features, tone }: { title: string; features: MvpFeature[]; tone: "accent" | "warning" | "neutral" }) {
  if (features.length === 0) return null;
  return (
    <Card>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">{title}</h3>
        <Badge tone={tone}>{features.length}</Badge>
      </div>
      <ul className="space-y-2">
        {features.map((f) => (
          <li key={f.id} className="text-sm">
            <span className="font-medium">{f.canonical_name}</span>
            <span className="text-muted"> — {f.description}</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

export default function MvpPage() {
  const { id } = useParams<{ id: string }>();
  const { project, loading: projectLoading, error: projectError, reload } =
    useProject(id);

  const [mvp, setMvp] = useState<MvpResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMvpRecommendation(id);
      setMvp(data);
      updatePipelineData(id, { mvp: data });
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not load the MVP recommendation.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  if (projectLoading) return <PageLoading label="Loading..." />;
  if (projectError || !project)
    return (
      <ErrorBanner message={projectError ?? "Project not found."} onRetry={reload} />
    );

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{project.title}</h1>
      <ProjectTabs projectId={project.id} />

      {loading && <PageLoading label="Loading MVP recommendation..." />}
      {!loading && error && <ErrorBanner message={error} onRetry={load} />}

      {!loading && mvp && !mvp.recommendation_possible && (
        <Card>
          <p className="text-sm text-muted">{mvp.reasoning}</p>
        </Card>
      )}

      {!loading && mvp && mvp.recommendation_possible && (
        <div className="space-y-6">
          <Card>
            <h3 className="mb-2 font-semibold">Recommendation</h3>
            <p className="text-sm text-muted">{mvp.reasoning}</p>
            {mvp.estimated_hours_range && (
              <div className="mt-4 grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs uppercase text-muted">Min hours</p>
                  <p className="mt-1 font-semibold">
                    {mvp.estimated_hours_range.min}h
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase text-muted">Expected hours</p>
                  <p className="mt-1 font-semibold">
                    {mvp.estimated_hours_range.expected}h
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase text-muted">Max hours</p>
                  <p className="mt-1 font-semibold">
                    {mvp.estimated_hours_range.max}h
                  </p>
                </div>
              </div>
            )}
          </Card>

          <FeatureList title="MVP (build first)" features={mvp.mvp_features} tone="accent" />
          <FeatureList title="Phase 2" features={mvp.phase_2_features} tone="warning" />
          <FeatureList title="Later" features={mvp.later_features} tone="neutral" />
        </div>
      )}

      <div className="mt-6">
        <Button variant="secondary" loading={loading} onClick={load}>
          Refresh recommendation
        </Button>
      </div>
    </div>
  );
}
