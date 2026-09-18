# ProjectScope AI — Frontend

A complete Next.js 14 (App Router) + TypeScript + Tailwind frontend, built
from scratch and wired end-to-end to the real FastAPI backend at
`SalehaBashir/projectscope-ai`.

Every page calls a real backend endpoint. Nothing is mocked. Where the
backend has no GET endpoint for a generated result (requirements, features,
tasks, risks, tech-stack, MVP), the result is cached client-side per project
(see `src/lib/project-store.tsx`) purely so a page refresh doesn't lose it —
re-running any step always calls the real backend again.

## 1. Install

```powershell
cd frontend
npm install
```

## 2. Configure the backend URL

`.env.local` is already created with:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Change this if your backend runs elsewhere. Every API call in the app reads
from this one variable (`src/lib/api.ts`) — nothing is hardcoded per-page.

## 3. Start the backend (in the backend repo)

```powershell
uvicorn app.main:app --reload
```

Make sure `JWT_SECRET_KEY` and the rest of your `.env` are set, Postgres and
Redis are running (`docker-compose up -d` if you're using the repo's
compose file), and `CORS_ORIGINS` includes `http://localhost:3000`.

## 4. Start the frontend

```powershell
npm run dev
```

Open http://localhost:3000

## 5. Test the full flow

1. Register a new account at `/register` (or log in at `/login`)
2. Create a project — this calls `POST /projects/` then
   `POST /projects/{id}/analyze` and polls the job until it finishes
3. Walk through the tabs: Requirements, Features, Questions, Tasks, Team,
   Cost & Timeline, Risks, MVP, Tech Stack, Theme, Start Building, Report,
   Feedback — each "Generate"/"Calculate" button calls its real endpoint
4. Refresh the browser — you stay logged in (token in localStorage) and
   already-generated results are still there (client-side cache)
5. Log out — token is cleared and you're redirected to `/login`
6. Let the token expire (60 min) or manually clear it — the next
   authenticated request gets a clean "Your session has expired" message
   and redirects to `/login`, instead of a raw `{"detail":"Not authenticated"}`

## Architecture notes

- **`src/lib/api.ts`** — the ONLY place that calls `fetch`. One token key in
  localStorage, attaches `Authorization: Bearer <token>` to every
  authenticated call, and centrally handles 401s (clear token → redirect).
- **`src/lib/endpoints.ts`** — one typed function per real backend endpoint.
  Every page imports from here — no page constructs a URL or header itself.
- **`src/lib/auth-context.tsx`** — the single auth flow (login/register set
  the token, `AuthProvider` reads it once on mount, `logout()` clears it).
- **`src/lib/project-store.tsx`** — client-side cache for pipeline results
  the backend doesn't expose via GET (see above). Not a source of truth.
- **`src/components/protected-route.tsx`** — gates every `/dashboard/*`
  page until the auth state is actually known, so there's no flash of
  protected content and no request fires before a token exists.

## Known backend behavior this frontend accounts for

- `POST /projects/{id}/analyze` can return `{status: "completed", result}`
  immediately, or `{status: "queued", job_id}` — the frontend polls
  `GET /projects/jobs/{job_id}` until `status` is `finished` or `failed`.
- `DELETE /users/me` expects a JSON body (`{password}}`) rather than being a
  bodyless DELETE — handled as a direct `fetch` call in `endpoints.ts`.
- `POST /projects/{id}/start-building` and
  `GET /projects/{id}/report?format=pdf|docx` both return binary files
  (not JSON) — downloaded via `Blob` + an in-memory `<a download>` click.
