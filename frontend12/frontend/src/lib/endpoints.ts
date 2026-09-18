import { api, API_BASE_URL, getToken, setToken } from "./api";
import type {
  AnalysisResult,
  EstimateResult,
  FeedbackItem,
  FeedbackSummary,
  MvpResult,
  Project,
  Question,
  Risk,
  TaskItem,
  TechStackResult,
  Theme,
} from "./types";

// ---------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(email: string, password: string) {
  const res = await api.postPublic<TokenResponse>("/auth/login", {
    email,
    password,
  });
  setToken(res.access_token);
  return res;
}

export async function register(data: {
  email: string;
  password: string;
  full_name?: string;
  organization_name?: string;
}) {
  const res = await api.postPublic<TokenResponse>("/auth/register", data);
  setToken(res.access_token);
  return res;
}

/** DELETE /users/me — requires a JSON body, so it's issued as a raw fetch. */
export async function deleteMyAccount(password: string) {
  const token = getToken();
  const res = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Account deletion failed.");
  }
  return res.json();
}

// ---------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------

export function createProject(data: {
  title: string;
  description: string;
  budget?: string;
  platform?: string;
}) {
  return api.post<Project>("/projects/", data);
}

export function listProjects() {
  return api.get<Project[]>("/projects/");
}

export function getProject(id: string) {
  return api.get<Project>(`/projects/${id}`);
}

export function updateProject(
  id: string,
  data: Partial<Pick<Project, "title" | "description" | "budget" | "platform">>,
) {
  return api.patch<Project>(`/projects/${id}`, data);
}

export function deleteProject(id: string) {
  return api.del<{ detail: string }>(`/projects/${id}`);
}

export function recalculateProject(
  id: string,
  data?: { description?: string; budget?: string; platform?: string },
) {
  return api.post<{ project: Project; estimate: EstimateResult }>(
    `/projects/${id}/recalculate`,
    data ?? {},
  );
}

// ---------------------------------------------------------------------
// AI Analysis (async job)
// ---------------------------------------------------------------------

interface AnalyzeQueuedResponse {
  status: "queued" | "completed";
  job_id?: string;
  result?: AnalysisResult;
}

interface JobStatusResponse {
  status: "queued" | "started" | "finished" | "failed";
  result?: AnalysisResult;
  error?: string;
}

export function analyzeProject(
  id: string,
  data: { description: string; budget?: string; platform?: string },
) {
  return api.post<AnalyzeQueuedResponse>(`/projects/${id}/analyze`, data);
}

export function getJobStatus(jobId: string) {
  return api.get<JobStatusResponse>(`/projects/jobs/${jobId}`);
}

/**
 * Kicks off analysis and polls until the background job finishes.
 * The backend can either run the job inline (test env) and return the
 * result immediately, or queue it and require polling — this handles both.
 */
export async function analyzeAndWait(
  id: string,
  data: { description: string; budget?: string; platform?: string },
  opts: { intervalMs?: number; timeoutMs?: number } = {},
): Promise<AnalysisResult> {
  const { intervalMs = 1500, timeoutMs = 120000 } = opts;
  const initial = await analyzeProject(id, data);

  if (initial.status === "completed" && initial.result) {
    return initial.result;
  }

  const jobId = initial.job_id;
  if (!jobId) {
    throw new Error("Analysis could not be started. Please try again.");
  }

  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    await new Promise((r) => setTimeout(r, intervalMs));
    const status = await getJobStatus(jobId);
    if (status.status === "finished" && status.result) {
      return status.result;
    }
    if (status.status === "failed") {
      throw new Error(status.error || "Analysis failed. Please try again.");
    }
  }
  throw new Error("Analysis is taking longer than expected. Please try again.");
}

// ---------------------------------------------------------------------
// Follow-up questions
// ---------------------------------------------------------------------

export function getQuestions(projectId: string) {
  return api.get<Question[]>(`/projects/${projectId}/questions`);
}

export function answerQuestion(
  projectId: string,
  questionId: string,
  answer: string,
) {
  return api.post<{ id: string; category: string; description: string }>(
    `/projects/${projectId}/questions/answer`,
    { question_id: questionId, answer },
  );
}

// ---------------------------------------------------------------------
// Tasks / roles
// ---------------------------------------------------------------------

export function generateTasks(projectId: string) {
  return api.post<TaskItem[]>(`/projects/${projectId}/generate-tasks`);
}

// ---------------------------------------------------------------------
// Estimation (effort + cost + timeline)
// ---------------------------------------------------------------------

export function calculateEstimate(projectId: string) {
  return api.post<EstimateResult>(`/projects/${projectId}/estimate`);
}

// ---------------------------------------------------------------------
// Risks
// ---------------------------------------------------------------------

export function generateRisks(projectId: string) {
  return api.post<Risk[]>(`/projects/${projectId}/risks`);
}

// ---------------------------------------------------------------------
// MVP recommendation
// ---------------------------------------------------------------------

export function getMvpRecommendation(projectId: string) {
  return api.get<MvpResult>(`/projects/${projectId}/mvp`);
}

// ---------------------------------------------------------------------
// Tech stack
// ---------------------------------------------------------------------

export function getTechStack(projectId: string) {
  return api.post<TechStackResult>(`/projects/${projectId}/tech-stack`);
}

// ---------------------------------------------------------------------
// Themes
// ---------------------------------------------------------------------

export function listThemes() {
  return api.get<Theme[]>("/themes");
}

export function getThemeSuggestion(projectId: string) {
  return api.post<Theme>(`/projects/${projectId}/theme-suggestion`);
}

export function chooseTheme(projectId: string, themeId?: string) {
  return api.post<Theme>(`/projects/${projectId}/theme`, {
    theme_id: themeId,
  });
}

export function getSavedTheme(projectId: string) {
  return api.get<Theme>(`/projects/${projectId}/theme`);
}

// ---------------------------------------------------------------------
// Start Building (scaffold ZIP download) — POST that returns a binary file
// ---------------------------------------------------------------------

export async function downloadScaffoldZip(projectId: string): Promise<Blob> {
  const token = getToken();
  const res = await fetch(
    `${API_BASE_URL}/api/v1/projects/${projectId}/start-building`,
    {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    },
  );
  if (!res.ok) {
    throw new Error("Could not generate the starter project. Please try again.");
  }
  return res.blob();
}

// ---------------------------------------------------------------------
// Report export (PDF / DOCX download)
// ---------------------------------------------------------------------

export async function downloadReport(
  projectId: string,
  format: "pdf" | "docx",
): Promise<Blob> {
  const token = getToken();
  const res = await fetch(
    `${API_BASE_URL}/api/v1/projects/${projectId}/report?format=${format}`,
    { headers: token ? { Authorization: `Bearer ${token}` } : {} },
  );
  if (!res.ok) {
    throw new Error("Could not generate the report. Please try again.");
  }
  return res.blob();
}

// ---------------------------------------------------------------------
// Feedback
// ---------------------------------------------------------------------

export function submitFeedback(
  projectId: string,
  data: {
    task_id?: string;
    estimated_hours?: number;
    actual_hours: number;
    notes?: string;
  },
) {
  return api.post<FeedbackItem>(`/projects/${projectId}/feedback`, data);
}

export function listFeedback(projectId: string) {
  return api.get<FeedbackItem[]>(`/projects/${projectId}/feedback`);
}

export function getFeedbackSummary(projectId: string) {
  return api.get<FeedbackSummary>(`/projects/${projectId}/feedback/summary`);
}

export function deleteFeedback(projectId: string, feedbackId: string) {
  return api.del<{ detail: string }>(
    `/projects/${projectId}/feedback/${feedbackId}`,
  );
}
