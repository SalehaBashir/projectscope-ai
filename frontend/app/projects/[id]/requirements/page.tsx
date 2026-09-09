'use client'

import { useParams } from 'next/navigation'
import { FileText, Loader2, Wand2, ArrowLeft } from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { ProjectTabs } from '@/components/projects/project-tabs'
import { useProjectData } from '@/hooks/use-project-data'
import { EmptyState, SkeletonCard, PriorityBadge, CategoryTag } from '@/components/ui/badges'

export default function RequirementsPage() {
  const params = useParams<{ id: string }>()
  const id = params.id
  const { project, requirements, loading, analyzing, analyze } = useProjectData(id)

  return (
    <AppShell>
      <a href={`/projects/${id}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--muted-foreground)', textDecoration: 'none', marginBottom: 16 }}>
        <ArrowLeft size={15} /> Back to project
      </a>

      <div className="view" style={{ paddingTop: 0 }}>
        <div className="view-heading">
          <div>
            <div className="eyebrow">REQUIREMENTS</div>
            <h1>Requirements</h1>
            <p>AI-extracted requirements for <strong>{project?.title || 'this project'}</strong>.</p>
          </div>
          <span className="ai-chip"><Wand2 size={14} /> AI generated</span>
        </div>

        <ProjectTabs projectId={id} />

        {loading ? (
          <div className="data-grid">
            <SkeletonCard lines={4} />
            <SkeletonCard lines={4} />
            <SkeletonCard lines={4} />
          </div>
        ) : requirements.length === 0 ? (
          <EmptyState
            icon={<FileText size={26} />}
            title="No requirements yet"
            description="Analyze the project to extract its requirements."
            action={
              <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }} onClick={() => analyze()} disabled={analyzing}>
                {analyzing ? <Loader2 size={16} className="spin" /> : <Wand2 size={16} />}
                {analyzing ? 'Analyzing...' : 'Analyze Project'}
              </button>
            }
          />
        ) : (
          <div className="data-grid">
            {requirements.map((r) => {
              const description = r.description || r.text
              return (
                <div className="req-card" key={r.id || `${r.category}-${r.description}`}>
                  <div className="req-card-top">
                    <CategoryTag category={r.category} />
                    <PriorityBadge priority={r.priority || 'medium'} />
                  </div>
                  <h3>{description}</h3>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </AppShell>
  )
}
