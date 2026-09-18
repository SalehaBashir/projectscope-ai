"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Card,
  EmptyState,
  ErrorBanner,
  PageLoading,
  Button,
} from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";

const ROLE_NAMES: Record<string, string> = {
  "985cf643-0a7a-4395-8ca1-0b0fbcda2a87": "UI/UX Designer",
  "5927e82f-ae41-4f97-b1b1-dcd5ad6060ed": "Backend Developer",
  "1f974fe1-3c4f-40a6-9fc5-4bc5b571a940": "Frontend Developer",
  "6b060868-4210-4fac-841d-d5c01a48fd83": "QA Engineer",
  "6f6765cc-1105-4d82-9e5a-04e3a836bd8c": "DevOps Engineer",
  "c5198837-a84e-4ea6-aee4-7231af83adca": "SEO Specialist",
  "9f0ae026-6190-4e6b-a9e3-c2764b931226": "Security Engineer",
  "44a90065-33f9-4366-933b-a5477e0d7ba7": "Technical Writer",
  "2f2f763b-c705-493c-aaf3-bd3af73d4e4b": "Backend Developer",
};

function getRoleName(
  roleId?: string | null,
  roleName?: string | null,
) {
  if (roleName && roleName.trim()) {
    return roleName;
  }

  if (roleId && ROLE_NAMES[roleId]) {
    return ROLE_NAMES[roleId];
  }

  return "Unassigned";
}

export default function TeamPage() {
  const { id } = useParams<{ id: string }>();

  const {
    project,
    pipeline,
    loading,
    error,
    reload,
  } = useProject(id);

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

  const byRole = tasks.reduce<
    Record<string, { count: number; hours: number }>
  >((acc, t) => {
    const role = getRoleName(
      t.role_id,
      t.role_name,
    );

    if (!acc[role]) {
      acc[role] = {
        count: 0,
        hours: 0,
      };
    }

    acc[role].count += 1;
    acc[role].hours += t.base_hours;

    return acc;
  }, {});

  const roles = Object.entries(byRole);

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">
        {project.title}
      </h1>

      <ProjectTabs projectId={project.id} />

      {roles.length === 0 ? (
        <EmptyState
          title="No team allocation yet"
          description="Generate tasks first — role allocation is derived from the task breakdown."
          action={
            <Link
              href={`/dashboard/projects/${project.id}/tasks`}
            >
              <Button variant="primary">
                Go to Tasks
              </Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {roles.map(([role, data]) => (
            <Card key={role}>
              <h3 className="mb-1 font-semibold">
                {role}
              </h3>

              <p className="text-sm text-muted">
                {data.count} task
                {data.count !== 1 ? "s" : ""} ·{" "}
                {data.hours}h total
              </p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}