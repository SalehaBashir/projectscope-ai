"use client";

import { useCallback, useEffect, useState } from "react";
import { getProject } from "./endpoints";
import { loadPipelineData, ProjectPipelineData } from "./project-store";
import type { Project } from "./types";
import { ApiError } from "./api";

export function useProject(projectId: string) {
  const [project, setProject] = useState<Project | null>(null);
  const [pipeline, setPipelineState] = useState<ProjectPipelineData>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProject(projectId);
      setProject(data);
      setPipelineState(loadPipelineData(projectId));
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to load this project. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  const refreshPipeline = useCallback(() => {
    setPipelineState(loadPipelineData(projectId));
  }, [projectId]);

  return { project, pipeline, loading, error, reload: load, refreshPipeline };
}
