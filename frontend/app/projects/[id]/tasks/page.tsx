'use client'

import { useParams } from 'next/navigation'
import { ClipboardCheck, Loader2, Wand2, ArrowLeft, Check } from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { ProjectTabs } from '@/components/projects/project-tabs'
import { useProjectData } from '@/hooks/use-project-data'
import { EmptyState, SkeletonCard, PriorityBadge } from '@/components/ui/badges'
import { useState } from 'react'

export default function TasksPage() {
  const params = useParams<{ id: string }>()
  const id = params.id
  const { project, tasks, loading, error, generatingTasks, generateTasks } = useProjectData(id)
  const [doneIds, setDoneIds] = useState<Set<string>>(new Set())

  return (
    <AppShell>
      <a href={`/projects/${id}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--muted-foreground)', textDecoration: 'none', marginBottom: 16 }}>
        <ArrowLeft size={15} /> Back to project
      </a>

      <div className="view" style={{ paddingTop: 0 }}>
        <div className="view-heading">
          <div>
            <div className="eyebrow">TASKS</div>
            <h1>Tasks</h1>
            <p>Decomposed tasks for <strong>{project?.title || 'this project'}</strong>.</p>
          </div>
          <span className="ai-chip"><Wand2 size={14} /> AI generated</span>
        </div>

        <ProjectTabs projectId={id} />

        {error && <div className="auth-error mb-16">{error}</div>}

        {loading ? (
          <div className="task-list">
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
          </div>
        ) : tasks.length === 0 && !generatingTasks ? (
          <EmptyState
            icon={<ClipboardCheck size={26} />}
            title="No tasks generated yet"
            description="Break this project down into actionable tasks."
            action={
              <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }} onClick={() => generateTasks()} disabled={generatingTasks}>
                {generatingTasks ? <Loader2 size={16} className="spin" /> : <Wand2 size={16} />}
                {generatingTasks ? 'Generating tasks...' : 'Generate Tasks'}
              </button>
            }
          />
        ) : (
          <div>
            {generatingTasks && (
              <div className="notice mt-8 mb-16">
                <Loader2 size={15} className="spin" style={{ flexShrink: 0, marginTop: 1 }} />
                <span>Generating tasks, assigning roles, and estimating hours...</span>
              </div>
            )}
            <div className="task-list">
              {tasks.map((t) => {
                const isDone = doneIds.has(t.id)
                return (
                  <div className="task-row" key={t.id}>
                    <button
                      className={`task-check ${isDone ? 'done' : ''}`}
                      onClick={() => {
                        const next = new Set(doneIds)
                        if (next.has(t.id)) next.delete(t.id)
                        else next.add(t.id)
                        setDoneIds(next)
                      }}
                      style={{ background: 'none', border: isDone ? '1.5px solid var(--primary)' : '1.5px solid var(--input)', cursor: 'pointer' }}
                      aria-label={isDone ? 'Mark as not done' : 'Mark as done'}
                    >
                      {isDone && <Check size={11} />}
                    </button>
                    <div className="task-main">
                      <strong style={{ textDecoration: isDone ? 'line-through' : 'none', color: isDone ? 'var(--muted-foreground)' : 'var(--foreground)' }}>{t.title}</strong>
                      {t.description && <p>{t.description}</p>}
                    </div>
                    <div className="task-meta">
                      {t.role && <span className="hours-chip">{t.role}</span>}
                      {t.base_hours > 0 && <span className="hours-chip">{t.base_hours}h</span>}
                    </div>
                  </div>
                )
              })}
              {tasks.length === 0 && <div className="result-empty">No tasks to display.</div>}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}

