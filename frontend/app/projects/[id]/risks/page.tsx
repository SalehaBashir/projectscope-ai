'use client'

import { useParams } from 'next/navigation'
import { ShieldAlert, Loader2, Wand2, ArrowLeft, ShieldCheck } from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { ProjectTabs } from '@/components/projects/project-tabs'
import { useProjectData } from '@/hooks/use-project-data'
import { EmptyState, SkeletonCard } from '@/components/ui/badges'

function levelTone(level: string) {
  return level === 'high' ? 'high' : level === 'medium' ? 'medium' : 'low'
}

export default function RisksPage() {
  const params = useParams<{ id: string }>()
  const id = params.id
  const { project, risks, loading, error, generatingRisks, generateRisks } = useProjectData(id)

  return (
    <AppShell>
      <a href={`/projects/${id}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--muted-foreground)', textDecoration: 'none', marginBottom: 16 }}>
        <ArrowLeft size={15} /> Back to project
      </a>

      <div className="view" style={{ paddingTop: 0 }}>
        <div className="view-heading">
          <div>
            <div className="eyebrow">RISKS</div>
            <h1>Risks</h1>
            <p>Identified risks for <strong>{project?.title || 'this project'}</strong>.</p>
          </div>
          <span className="ai-chip"><Wand2 size={14} /> AI identified</span>
        </div>

        <ProjectTabs projectId={id} />

        {error && <div className="auth-error mb-16">{error}</div>}

        {loading ? (
          <div className="data-grid">
            <SkeletonCard lines={4} />
            <SkeletonCard lines={4} />
            <SkeletonCard lines={4} />
          </div>
        ) : risks.length === 0 && !generatingRisks ? (
          <EmptyState
            icon={<ShieldAlert size={26} />}
            title="No risks identified yet"
            description="Analyze the project to uncover potential risks."
            action={
              <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }} onClick={() => generateRisks()} disabled={generatingRisks}>
                {generatingRisks ? <Loader2 size={16} className="spin" /> : <Wand2 size={16} />}
                {generatingRisks ? 'Generating risks...' : 'Generate Risks'}
              </button>
            }
          />
        ) : (
          <div className="data-grid">
            {risks.map((r) => {
              const severity = r.severity
              return (
                <div className="risk-card-modern" key={r.id}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
                    <h3>{r.description}</h3>
                    <span className={`risk-sev ${levelTone(severity)}`}>{severity} severity</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
                    {r.probability != null && <span className="risk-sev">▲ {r.probability} probability</span>}
                    {r.impact && <span className={`risk-sev ${levelTone(r.impact)}`}>◉ {r.impact} impact</span>}
                  </div>
                  {r.mitigation && (
                    <div className="mitigation-box">
                      <ShieldCheck size={14} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: 1 }} />
                      <span><b>MITIGATION</b>{r.mitigation}</span>
                    </div>
                  )}
                </div>
              )
            })}
            {risks.length === 0 && <div className="result-empty">No risks to display.</div>}
          </div>
        )}
      </div>
    </AppShell>
  )
}
