'use client'

import { useParams } from 'next/navigation'
import {
  Sparkles, Printer, ArrowLeft, Check, ShieldAlert, Clock, DollarSign,
  Calendar, Users, Boxes, ListChecks, ClipboardCheck, FileText,
} from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { ProjectTabs } from '@/components/projects/project-tabs'
import { useProjectData } from '@/hooks/use-project-data'
import { EmptyState, SkeletonCard, PriorityBadge, ComplexityBadge } from '@/components/ui/badges'

export default function PlanPage() {
  const params = useParams<{ id: string }>()
  const id = params.id
  const {
    project, projectType, users, requirements, features, tasks, estimate,
    risks, loading,
  } = useProjectData(id)

  const handlePrint = () => {
    window.print()
  }

  return (
    <AppShell>
      <div className="plan-page no-print" style={{ marginBottom: 16 }}>
        <a href={`/projects/${id}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--muted-foreground)', textDecoration: 'none', marginBottom: 16 }}>
          <ArrowLeft size={15} /> Back to project
        </a>
        <ProjectTabs projectId={id} />
      </div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <SkeletonCard lines={3} />
          <SkeletonCard lines={4} />
          <SkeletonCard lines={2} />
        </div>
      ) : !project ? (
        <EmptyState
          icon={<FileText size={26} />}
          title="Project not found"
          description="This project could not be found."
          action={<button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }} onClick={() => window.location.href = '/dashboard'}>Back to Dashboard</button>}
        />
      ) : (
        <div className="plan-page">
          <div className="print-actions">
            <button className="auth-login-btn no-print" style={{ width: 'auto', display: 'inline-flex' }} onClick={handlePrint}>
              <Printer size={16} /> Print Project Plan
            </button>
            <a href="/dashboard" style={{ textDecoration: 'none' }}>
              <button className="auth-login-btn no-print" style={{ width: 'auto', display: 'inline-flex', background: 'var(--muted)', color: 'var(--foreground)', border: '1px solid var(--border)' }}>
                <ArrowLeft size={16} /> Back to Dashboard
              </button>
            </a>
          </div>

          <div className="plan-header">
            <div className="plan-brand"><Sparkles size={18} /> ProjectScope AI</div>
            <h1>{project.title}</h1>
            <p>AI-generated project plan · {new Date().toLocaleDateString()}</p>
          </div>

          <div className="plan-section">
            <h2><Boxes size={18} /> Project Overview</h2>
            <p style={{ color: 'var(--muted-foreground)', fontSize: 13.5, lineHeight: 1.6, margin: '0 0 16px' }}>{project.description}</p>
            <div className="plan-kv">
              {projectType && (
                <div className="plan-kv-item"><small>PROJECT TYPE</small><strong>{projectType}</strong></div>
              )}
              {project.platform && (
                <div className="plan-kv-item"><small>PLATFORM</small><strong>{project.platform}</strong></div>
              )}
              {project.budget && (
                <div className="plan-kv-item"><small>BUDGET</small><strong>{project.budget}</strong></div>
              )}
              <div className="plan-kv-item"><small>STATUS</small><strong>{project.status}</strong></div>
            </div>
            {users.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <small className="uppercase" style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: '.06em', color: 'var(--muted-foreground)' }}>TARGET USERS</small>
                <p style={{ margin: '4px 0 0', fontSize: 13.5, color: 'var(--muted-foreground)' }}>{users.join(', ')}</p>
              </div>
            )}
          </div>

          <div className="plan-section">
            <h2><FileText size={18} /> Requirements</h2>
            {requirements.length === 0 ? (
              <p className="text-muted">No requirements extracted.</p>
            ) : (
              <div className="plan-list">
                {requirements.map((r, i) => (
                  <div className="plan-list-item" key={r.id || i}>
                    <Check size={15} />
                    <span><b>{r.category.replace('_', ' ')}:</b> {r.description || r.text}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="plan-section">
            <h2><ListChecks size={18} /> Features</h2>
            {features.length === 0 ? (
              <p className="text-muted">No features extracted.</p>
            ) : (
              <div className="plan-list">
                {features.map((f, i) => (
                  <div className="plan-list-item" key={f.id || i}>
                    <Check size={15} />
                    <span><b style={{ textTransform: 'capitalize' }}>{f.canonical_name.replace(/_/g, ' ')}</b> — {f.description} <PriorityBadge priority={f.priority} /> <ComplexityBadge complexity={f.complexity} /></span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="plan-section">
            <h2><ClipboardCheck size={18} /> Tasks</h2>
            {tasks.length === 0 ? (
              <p className="text-muted">No tasks generated yet. Run "Generate Tasks" first.</p>
            ) : (
              <div className="plan-list">
                {tasks.map((t) => (
                  <div className="plan-list-item" key={t.id}>
                    <Check size={15} />
                    <span><b>{t.title}</b>{t.base_hours > 0 && ` (${t.base_hours}h)`} {t.role && <small className="text-muted">· {t.role}</small>}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="plan-section">
            <h2><Users size={18} /> Team / Roles</h2>
            <p className="text-muted" style={{ margin: 0 }}>Roles are assigned during task generation based on each task's requirements. View the Tasks page for role assignments per task.</p>
          </div>

          <div className="plan-section">
            <h2><Calendar size={18} /> Timeline</h2>
            {estimate ? (
              <div className="plan-kv">
                <div className="plan-kv-item"><small>MIN</small><strong>{estimate.timeline_weeks_min} weeks</strong></div>
                <div className="plan-kv-item"><small>EXPECTED</small><strong>{estimate.timeline_weeks_expected} weeks</strong></div>
                <div className="plan-kv-item"><small>MAX</small><strong>{estimate.timeline_weeks_max} weeks</strong></div>
              </div>
            ) : <p className="text-muted" style={{ margin: 0 }}>Not estimated yet.</p>}
          </div>

          <div className="plan-section">
            <h2><Clock size={18} /> Estimated Effort</h2>
            {estimate ? (
              <div className="plan-kv">
                <div className="plan-kv-item"><small>MIN HOURS</small><strong>{Math.round(estimate.min_hours)}</strong></div>
                <div className="plan-kv-item"><small>EXPECTED HOURS</small><strong>{Math.round(estimate.expected_hours)}</strong></div>
                <div className="plan-kv-item"><small>MAX HOURS</small><strong>{Math.round(estimate.max_hours)}</strong></div>
              </div>
            ) : <p className="text-muted" style={{ margin: 0 }}>Not estimated yet.</p>}
          </div>

          <div className="plan-section">
            <h2><DollarSign size={18} /> Estimated Cost</h2>
            {estimate ? (
              <div className="plan-kv">
                <div className="plan-kv-item"><small>MIN COST</small><strong>${Math.round(estimate.min_cost).toLocaleString()}</strong></div>
                <div className="plan-kv-item"><small>EXPECTED COST</small><strong>${Math.round(estimate.expected_cost).toLocaleString()}</strong></div>
                <div className="plan-kv-item"><small>MAX COST</small><strong>${Math.round(estimate.max_cost).toLocaleString()}</strong></div>
              </div>
            ) : <p className="text-muted" style={{ margin: 0 }}>Not estimated yet.</p>}
          </div>

          <div className="plan-section">
            <h2><ShieldAlert size={18} /> Risks</h2>
            {risks.length === 0 ? (
              <p className="text-muted" style={{ margin: 0 }}>No risks identified yet.</p>
            ) : (
              <div className="plan-list">
                {risks.map((r) => (
                  <div className="plan-list-item" key={r.id}>
                    <ShieldAlert size={15} style={{ color: r.severity === 'high' ? 'var(--danger)' : r.severity === 'medium' ? 'var(--warning)' : 'var(--success)', flexShrink: 0, marginTop: 2 }} />
                    <span>
                      <b>{r.description}</b>
                      {' '}· {r.probability} probability · {r.impact} impact
                      {r.mitigation && <div style={{ marginTop: 4, fontSize: 12.5, color: 'var(--muted-foreground)' }}>Mitigation: {r.mitigation}</div>}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="plan-section">
            <h2><Sparkles size={18} /> Recommendations</h2>
            <div className="plan-list">
              {estimate && (
                <div className="plan-list-item">
                  <Check size={15} />
                  <span>Proceed with a <b>{estimate.timeline_weeks_expected}-week</b> to <b>{estimate.timeline_weeks_max}-week</b> delivery timeline, budgeting <b>${Math.round(estimate.expected_cost).toLocaleString()}</b> as the expected cost.</span>
                </div>
              )}
              {features.length > 0 && (
                <div className="plan-list-item">
                  <Check size={15} />
                  <span>Prioritize <b>{features.filter((f) => f.priority === 'high').length || 1} high-priority features</b> in the first build phase to deliver core value quickly.</span>
                </div>
              )}
              {risks.length > 0 && (
                <div className="plan-list-item">
                  <Check size={15} />
                  <span>Address the <b>{risks.filter((r) => r.severity === 'high').length || 1} high-severity risks</b> early to reduce project uncertainty.</span>
                </div>
              )}
              <div className="plan-list-item">
                <Check size={15} />
                <span>Add specific dates, team capacity, and regular stakeholder reviews before committing to the final timeline.</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}
