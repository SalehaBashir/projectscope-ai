"use client";

/**
 * The backend does not expose GET endpoints for requirements, features,
 * tasks, risks, tech-stack or MVP — each of those is only returned once,
 * at the moment its POST endpoint runs (see backend/app/api/*.py).
 *
 * So this app caches each project's pipeline output client-side,
 * persisted to localStorage per project id, purely so a page refresh or
 * a trip back to the dashboard doesn't lose what was already generated.
 * This is a UI convenience cache, NOT a source of truth — the project
 * record itself, and the real numbers on re-run, always come from the
 * live backend.
 */

import type {
  AnalysisResult,
  EstimateResult,
  MvpResult,
  Question,
  Risk,
  TaskItem,
  TechStackResult,
  Theme,
} from "./types";

export interface ProjectPipelineData {
  analysis?: AnalysisResult;
  questions?: Question[];
  tasks?: TaskItem[];
  estimate?: EstimateResult;
  risks?: Risk[];
  mvp?: MvpResult;
  techStack?: TechStackResult;
  theme?: Theme;
}

const STORAGE_PREFIX = "projectscope_pipeline_";

export function loadPipelineData(projectId: string): ProjectPipelineData {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_PREFIX + projectId);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function savePipelineData(
  projectId: string,
  data: ProjectPipelineData,
): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      STORAGE_PREFIX + projectId,
      JSON.stringify(data),
    );
  } catch {
    // storage full/unavailable — non-fatal, just means cache is skipped
  }
}

export function updatePipelineData(
  projectId: string,
  patch: Partial<ProjectPipelineData>,
): ProjectPipelineData {
  const current = loadPipelineData(projectId);
  const next = { ...current, ...patch };
  savePipelineData(projectId, next);
  return next;
}

export function clearPipelineData(projectId: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_PREFIX + projectId);
}
