/**
 * Central API client for ProjectScope AI.
 *
 * This is the ONLY place that talks to the backend. Every page/component
 * must go through the functions here instead of calling fetch() directly,
 * so there is exactly one token storage mechanism and one place that
 * attaches the Authorization header.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
  "http://127.0.0.1:8000";

const API_PREFIX = "/api/v1";

// Single source of truth for the token storage key. Never duplicate this
// string anywhere else in the app.
const TOKEN_KEY = "projectscope_access_token";

/** Basic shape of FastAPI's default error body: { "detail": "..." } */
interface ApiErrorBody {
  detail?: string | { msg?: string }[] | Record<string, unknown>;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Raised specifically for 401s so callers/UI can special-case "session expired". */
export class UnauthorizedError extends ApiError {
  constructor(message = "Your session has expired. Please log in again.") {
    super(message, 401);
    this.name = "UnauthorizedError";
  }
}

// ---------------------------------------------------------------------
// Token storage (client-side only — guarded for Next.js SSR/hydration)
// ---------------------------------------------------------------------

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------
// 401 handling: a single hook other parts of the app (AuthContext) can
// register so that any request, anywhere, that gets a 401 triggers one
// consistent "log the user out" flow instead of each page reinventing it.
// ---------------------------------------------------------------------

type UnauthorizedHandler = () => void;
let onUnauthorized: UnauthorizedHandler | null = null;

export function registerUnauthorizedHandler(handler: UnauthorizedHandler) {
  onUnauthorized = handler;
}

// ---------------------------------------------------------------------
// Core request helper
// ---------------------------------------------------------------------

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  auth?: boolean; // default true — attach Authorization header
  query?: Record<string, string | number | undefined>;
  /** Set true when expecting a binary/file response (report download). */
  raw?: boolean;
}

function buildUrl(path: string, query?: RequestOptions["query"]): string {
  const url = new URL(`${API_BASE_URL}${API_PREFIX}${path}`);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) url.searchParams.set(key, String(value));
    });
  }
  return url.toString();
}

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body: ApiErrorBody = await res.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      const first = body.detail[0];
      if (first && typeof first === "object" && "msg" in first) {
        return String((first as { msg?: string }).msg ?? "Request failed.");
      }
    }
  } catch {
    // response wasn't JSON — fall through to generic message
  }
  return "Something went wrong. Please try again.";
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true, query, raw = false } = options;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";

  if (auth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  let res: Response;
  try {
    res = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Is the backend running?",
      0,
    );
  }

  if (res.status === 401) {
    // Only clear/redirect for authenticated requests — a 401 on the
    // login/register endpoints themselves just means bad credentials.
    if (auth) {
      clearToken();
      onUnauthorized?.();
    }
    const detail = await parseErrorDetail(res);
    throw new UnauthorizedError(
      auth ? "Your session has expired. Please log in again." : detail,
    );
  }

  if (!res.ok) {
    const detail = await parseErrorDetail(res);
    throw new ApiError(detail, res.status);
  }

  if (raw) {
    return res as unknown as T;
  }

  if (res.status === 204) {
    return undefined as unknown as T;
  }

  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export const api = {
  get: <T>(path: string, query?: RequestOptions["query"]) =>
    request<T>(path, { method: "GET", query }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  /** Public (no Authorization header) POST — used for login/register. */
  postPublic: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body, auth: false }),
  /** Raw fetch for binary downloads (reports). Returns the Response. */
  getRaw: (path: string, query?: RequestOptions["query"]) =>
    request<Response>(path, { method: "GET", query, raw: true }),
};

export { API_BASE_URL };
