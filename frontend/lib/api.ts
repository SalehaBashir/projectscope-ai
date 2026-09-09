import type {
  Project,
  Requirement,
  Feature,
  Question,
  TaskItem,
  Estimate,
  Risk,
  TechStackResult,
  Theme,
} from './types'

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

const TOKEN_KEY = 'projectscope_token'

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(TOKEN_KEY, token)
  }
}

export function clearToken(): void {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(TOKEN_KEY)
  }
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type RequestOptions = {
  method?: string
  body?: unknown
  headers?: Record<string, string>
  auth?: boolean
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, auth = true } = options

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  }

  if (auth) {
    const token = getToken()
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`
    }
  }

  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers: requestHeaders,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError('Network error. Please check your connection and try again.', 0)
  }

  if (res.status === 401) {
    clearToken()
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      window.location.href = '/login'
    }
    throw new ApiError('Your session has expired. Please log in again.', 401)
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (data && typeof data.detail === 'string') {
        message = data.detail
      }
    } catch {
      // ignore parse errors
    }
    throw new ApiError(message, res.status)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return (await res.json()) as T
}

export const api = {
  // ---- Auth ----
  register: (data: { email: string; password: string; full_name?: string; organization_name?: string }) =>
    request<{ access_token: string; token_type: string }>('/auth/register', {
      method: 'POST',
      body: data,
      auth: false,
    }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      body: data,
      auth: false,
    }),

  // ---- Projects ----
  listProjects: () => request<Project[]>('/projects/'),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (data: { title: string; description: string; budget?: string; platform?: string }) =>
    request<Project>('/projects/', { method: 'POST', body: data }),

  // ---- Analysis ----
  analyzeProject: (id: string, data: { description: string; budget?: string; platform?: string }) =>
    request<{
      project_type: string
      users: string[]
      requirements: Requirement[]
      features: Feature[]
    }>(`/projects/${id}/analyze`, { method: 'POST', body: data }),

  // ---- Questions ----
  getQuestions: (id: string) => request<Question[]>(`/projects/${id}/questions`),
  answerQuestion: (id: string, data: { question_id: string; answer: string }) =>
    request<unknown>(`/projects/${id}/questions/answer`, { method: 'POST', body: data }),

  // ---- Tasks ----
  generateTasks: (id: string) => request<TaskItem[]>(`/projects/${id}/generate-tasks`, { method: 'POST' }),

  // ---- Estimate ----
  generateEstimate: (id: string) => request<Estimate>(`/projects/${id}/estimate`, { method: 'POST' }),

  // ---- Risks ----
  generateRisks: (id: string) => request<Risk[]>(`/projects/${id}/risks`, { method: 'POST' }),

  // ---- Tech stack ----
  generateTechStack: (id: string) => request<TechStackResult>(`/projects/${id}/tech-stack`, { method: 'POST' }),

  // ---- Themes ----
  listThemes: () => request<Theme[]>('/themes'),
  suggestTheme: (id: string) => request<Theme>(`/projects/${id}/theme-suggestion`, { method: 'POST' }),

  // ---- Scaffold ----
  startBuilding: async (id: string): Promise<Blob> => {
    const token = getToken()
    const headers: Record<string, string> = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(`${API_BASE}/projects/${id}/start-building`, {
      method: 'POST',
      headers,
    })
    if (!res.ok) {
      let message = 'Could not generate starter project'
      try {
        const data = await res.json()
        if (data && typeof data.detail === 'string') message = data.detail
      } catch {
        // ignore
      }
      throw new ApiError(message, res.status)
    }
    return res.blob()
  },
}
