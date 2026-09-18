"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  PageLoading,
} from "@/components/ui";
import { listProjects } from "@/lib/endpoints";
import type { Project } from "@/lib/types";
import { ApiError } from "@/lib/api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);

    try {
      const data = await listProjects();
      setProjects(data);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to load your projects. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">
            Projects
          </h1>

          <p className="text-sm text-muted">
            Manage all your ProjectScope AI projects.
          </p>
        </div>

        <Link href="/dashboard/projects/new">
          <Button variant="primary">
            + New project
          </Button>
        </Link>
      </div>

      {loading && (
        <PageLoading label="Loading your projects..." />
      )}

      {!loading && error && (
        <ErrorBanner
          message={error}
          onRetry={load}
        />
      )}

      {!loading &&
        !error &&
        projects &&
        projects.length === 0 && (
          <EmptyState
            title="No projects yet"
            description="Create your first project and ProjectScope AI will turn your idea into requirements, features, tasks, cost and timeline."
            action={
              <Link href="/dashboard/projects/new">
                <Button variant="primary">
                  Create your first project
                </Button>
              </Link>
            }
          />
        )}

      {!loading &&
        !error &&
        projects &&
        projects.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <Link
                key={project.id}
                href={`/dashboard/projects/${project.id}`}
              >
                <Card className="h-full transition-colors hover:border-accent">
                  <div className="mb-2 flex items-start justify-between gap-2">
                    <h3 className="font-semibold">
                      {project.title}
                    </h3>

                    <Badge tone="accent">
                      {project.status}
                    </Badge>
                  </div>

                  <p className="line-clamp-3 text-sm text-muted">
                    {project.description}
                  </p>

                  <div className="mt-4 flex gap-2 text-xs text-muted">
                    {project.platform && (
                      <span>{project.platform}</span>
                    )}

                    {project.budget && (
                      <span>· {project.budget}</span>
                    )}
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
    </div>
  );
}