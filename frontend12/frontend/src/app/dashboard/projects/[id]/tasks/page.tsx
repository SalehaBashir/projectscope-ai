"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import {
  Button,
  EmptyState,
  ErrorBanner,
  PageLoading,
} from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { generateTasks } from "@/lib/endpoints";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

const ROLE_NAMES: Record<string, string> = {
  "985cf643-0a7a-4395-8ca1-0b0fbcda2a87": "UI/UX Designer",
  "5927e82f-ae41-4f97-b1b1-dcd5ad6060ed": "Backend Developer",
  "1f974fe1-3c4f-40a6-9fc5-4bc5b571a940": "Frontend Developer",
  "6b060868-4210-4fac-841d-d5c01a48fd83": "QA Engineer",
  "6f6765cc-1105-4d82-9e5a-04e3a836bd8c": "DevOps Engineer",
  "9f0ae026-6190-4e6b-a9e3-c2764b931226": "Security Engineer",
  "44a90065-33f9-4366-933b-a5477e0d7ba7": "Technical Writer",
  "2f2f763b-c705-493c-aaf3-bd3af73d4e4b": "Backend Developer",
};

function getRoleName(roleId?: string | null, roleName?: string | null) {
  if (roleName && roleName.trim()) {
    return roleName;
  }

  if (roleId && ROLE_NAMES[roleId]) {
    return ROLE_NAMES[roleId];
  }

  return "Unassigned";
}

export default function TasksPage() {
  const { id } = useParams<{ id: string }>();

  const {
    project,
    pipeline,
    loading,
    error,
    reload,
    refreshPipeline,
  } = useProject(id);

  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);

  async function run() {
    setGenerating(true);
    setGenError(null);

    try {
      const tasks = await generateTasks(id);

      updatePipelineData(id, { tasks });

      refreshPipeline();
    } catch (err) {
      setGenError(
        err instanceof ApiError
          ? err.message
          : "Could not generate tasks.",
      );
    } finally {
      setGenerating(false);
    }
  }

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

  const tasks = pipeline.tasks ?? [];

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">
        {project.title}
      </h1>

      <ProjectTabs projectId={project.id} />

      {genError && (
        <div className="mb-4">
          <ErrorBanner
            message={genError}
            onRetry={run}
          />
        </div>
      )}

      <div className="mb-4 flex justify-end">
        <Button
          variant="secondary"
          loading={generating}
          onClick={run}
        >
          {tasks.length > 0
            ? "Regenerate tasks"
            : "Generate tasks"}
        </Button>
      </div>

      {tasks.length === 0 ? (
        <EmptyState
          title="No tasks yet"
          description="Generate the task breakdown for this project's features."
          action={
            <Button
              variant="primary"
              loading={generating}
              onClick={run}
            >
              Generate tasks
            </Button>
          }
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-border">
          <table className="w-full text-sm">
            <thead className="bg-surface2 text-left text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Task</th>
                <th className="px-4 py-3">Feature</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3 text-right">
                  Base hours
                </th>
              </tr>
            </thead>

            <tbody>
              {tasks.map((t) => (
                <tr
                  key={t.id}
                  className="border-t border-border"
                >
                  <td className="px-4 py-3">
                    {t.title}
                  </td>

                  <td className="px-4 py-3 text-muted">
                    {t.feature_name ?? "—"}
                  </td>

                  <td className="px-4 py-3">
                    <span className="inline-flex rounded-full border border-border bg-surface2 px-2.5 py-1 text-xs font-medium">
                      {getRoleName(
                        t.role_id,
                        t.role_name,
                      )}
                    </span>
                  </td>

                  <td className="px-4 py-3 text-right">
                    {t.base_hours}h
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}