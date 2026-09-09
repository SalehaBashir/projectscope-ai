'use client'

import { useParams } from 'next/navigation'
import { BarChart3, Loader2, Wand2, ArrowLeft, Sparkles, Clock, DollarSign, Calendar } from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { ProjectTabs } from '@/components/projects/project-tabs'
import { useProjectData } from '@/hooks/use-project-data'
import { EmptyState, SkeletonCard } from '@/components/ui/badges'

export default function EstimatePage() {
  const params = useParams<{ id: string }>()
  const id = params.id
  const {
    project, estimate, loading, error, estimating,
    generateEstimate, generateTasks, tasks,
  } = useProjectData(id)

  const runFullEstimate = async () => {
    if (tasks.length === 0) {
      await generateTasks()
    }
    await generateEstimate()
  }

  return (
    <AppShell>
      <a href={`/projects/${id}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--muted-foreground)', textDecoration: 'none', marginBottom: 16 }}>
        <ArrowLeft size={15} /> Back to project
      </a>

      <div className="view" style={{ paddingTop: 0 }}>
        <div className="view-heading">
          <div>
            <div className="eyebrow">ESTIMATION</div>
            <h1>Estimate</h1>
            <p>Effort, cost, and timeline for <strong>{project?.title || 'this project'}</strong>.</p>
          </div>
          <span className="ai-chip"><Sparkles size={14} /> AI calculated</span>
        </div>

        <ProjectTabs projectId={id} />

        {error && <div className="auth-error mb-16">{error}</div>}

        {loading ? (
          <div className="estimate-cards">
            <SkeletonCard lines={3} />
            <SkeletonCard lines={3} />
            <SkeletonCard lines={3} />
          </div>
        ) : !estimate ? (
          <EmptyState
            icon={<BarChart3 size={26} />}
            title="No estimate yet"
            description="Calculate hours, cost, and timeline for this project."
            action={
              <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }} onClick={runFullEstimate} disabled={estimating}>
                {estimating ? <Loader2 size={16} className="spin" /> : <Wand2 size={16} />}
                {estimating ? 'Calculating estimate...' : 'Calculate Estimate'}
              </button>
            }
          />
        ) : (
          <>
            {estimating && (
              <div className="notice mt-8 mb-16">
                <Loader2 size={15} className="spin" style={{ flexShrink: 0, marginTop: 1 }} />
                <span>Calculating estimate based on tasks and scope...</span>
              </div>
            )}
            <div className="estimate-cards">
              <div className="est-card">
                <small>ESTIMATED HOURS</small>
                <div className="est-value">{Math.round(estimate.expected_hours)} <span>hrs</span></div>
                <div className="est-range">{Math.round(estimate.min_hours)} min · {Math.round(estimate.max_hours)} max</div>
              </div>
              <div className="est-card">
                <small>ESTIMATED COST</small>
                <div className="est-value">${Math.round(estimate.expected_cost).toLocaleString()}</div>
                <div className="est-range">${Math.round(estimate.min_cost).toLocaleString()} min · ${Math.round(estimate.max_cost).toLocaleString()} max</div>
              </div>
              <div className="est-card">
                <small>ESTIMATED TIMELINE</small>
                <div className="est-value">{estimate.timeline_weeks_min}–{estimate.timeline_weeks_max} <span>weeks</span></div>
                <div className="est-range">Expected: {estimate.timeline_weeks_expected} weeks</div>
              </div>
            </div>

            <div className="hours-bar">
              <div className="hours-bar-item">
                <small>MIN</small>
                <strong>{Math.round(estimate.min_hours)}h</strong>
                <div className="est-bar"><div className="est-bar-fill" style={{ width: '30%', background: 'var(--success)' }} /></div>
              </div>
              <div className="hours-bar-item">
                <small>EXPECTED</small>
                <strong>{Math.round(estimate.expected_hours)}h</strong>
                <div className="est-bar"><div className="est-bar-fill" style={{ width: '65%', background: 'var(--primary)' }} /></div>
              </div>
              <div className="hours-bar-item">
                <small>MAX</small>
                <strong>{Math.round(estimate.max_hours)}h</strong>
                <div className="est-bar"><div className="est-bar-fill" style={{ width: '100%', background: 'var(--warning)' }} /></div>
              </div>
            </div>

            <div className="complexity-card" style={{ marginTop: 16 }}>
              <div>
                <small>COMPLEXITY SCORE</small>
                <h2>{Math.round(estimate.complexity_score)} <span>/ 100</span></h2>
                <p>Based on {estimate.task_count} generated tasks across all features.</p>
              </div>
              <div className="gauge">
                <div className="gauge-value" style={{ left: `${Math.min(estimate.complexity_score, 100)}%` }} />
                <span>Low</span><span>Moderate</span><span>High</span>
              </div>
            </div>

            {estimate.ml_predicted_hours != null && estimate.hybrid_expected_hours != null && (
              <div className="reasoning" style={{ marginTop: 14 }}>
                <Sparkles size={17} />
                <p><b>Hybrid estimate:</b> Our ML model (trained on past project data) predicts {Math.round(estimate.ml_predicted_hours)}h. Combined with rule-based calculation, the hybrid estimate is {Math.round(estimate.hybrid_expected_hours)}h.</p>
              </div>
            )}

            {estimate.complexity_explanation && (
              <div className="notice mt-16">
                <Sparkles size={15} style={{ flexShrink: 0, marginTop: 1 }} />
                <span><b>Complexity breakdown:</b> {estimate.complexity_explanation}</span>
              </div>
            )}

            <div className="button-row">
              <button
                className="auth-login-btn"
                style={{ width: 'auto', display: 'inline-flex', background: 'var(--primary)', border: '1px solid var(--primary)' }}
                onClick={() => generateEstimate()}
                disabled={estimating}
              >
                {estimating ? <Loader2 size={16} className="spin" /> : <Wand2 size={16} />}
                {estimating ? 'Recalculating...' : 'Recalculate'}
              </button>
            </div>
          </>
        )}
      </div>
    </AppShell>
  )
}