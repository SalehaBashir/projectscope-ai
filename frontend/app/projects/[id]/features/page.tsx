'use client'

import { useParams } from 'next/navigation'
import { ListChecks, Loader2, Wand2, ArrowLeft } from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { ProjectTabs } from '@/components/projects/project-tabs'
import { useProjectData } from '@/hooks/use-project-data'
import { EmptyState, SkeletonCard, PriorityBadge, ComplexityBadge } from '@/components/ui/badges'

export default function FeaturesPage() {
  const params = useParams<{ id: string }>()
  const id = params.id
  const { project, features, loading, analyzing, analyze } = useProjectData(id)

  return (
    <AppShell>
      <a href={`/projects/${id}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--muted-foreground)', textDecoration: 'none', marginBottom: 16 }}>
        <ArrowLeft size={15} /> Back to project
      </a>

      <div className="view" style={{ paddingTop: 0 }}>
        <div className="view-heading">
          <div>
            <div className="eyebrow">FEATURES</div>
            <h1>Features</h1>
            <p>Extracted features for <strong>{project?.title || 'this project'}</strong>.</p>
          </div>
          <span className="ai-chip"><Wand2 size={14} /> AI generated</span>
        </div>

        <ProjectTabs projectId={id} />

        {loading ? (
          <div className="data-grid">
            <SkeletonCard lines={3} />
            <SkeletonCard lines={3} />
            <SkeletonCard lines={3} />
          </div>
        ) : features.length === 0 ? (
          <EmptyState
            icon={<ListChecks size={26} />}
            title="No features yet"
            description="Analyze the project to extract its features."
            action={
              <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }} onClick={() => analyze()} disabled={analyzing}>
                {analyzing ? <Loader2 size={16} className="spin" /> : <Wand2 size={16} />}
                {analyzing ? 'Analyzing...' : 'Analyze Project'}
              </button>
            }
          />
        ) : (
          <div className="data-grid">
            {features.map((f) => (
              <div className="req-card" key={f.id || f.canonical_name}>
                <div className="req-card-top">
                  <div className="req-card-category"><ListChecks size={13} /> Feature</div>
                  <ComplexityBadge complexity={f.complexity} />
                </div>
                <h3 style={{ textTransform: 'capitalize' }}>{f.canonical_name.replace(/_/g, ' ')}</h3>
                <p>{f.description}</p>
                <div className="req-card-footer">
                  <PriorityBadge priority={f.priority} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  )
}
