'use client'

import { useParams } from 'next/navigation'
import {
  BrainCircuit,
  Loader2,
  Wand2,
  ListChecks,
  ArrowRight,
  Globe,
  Wallet,
  FolderOpen,
  CheckCircle2,
} from 'lucide-react'

import { AppShell } from '@/components/layout/app-shell'
import { ProjectTabs } from '@/components/projects/project-tabs'
import { useProjectData } from '@/hooks/use-project-data'
import { Badge, EmptyState, SkeletonCard } from '@/components/ui/badges'

function priorityTone(
  priority: string
): 'purple' | 'blue' | 'neutral' {
  if (priority === 'high') return 'purple'
  if (priority === 'medium') return 'blue'
  return 'neutral'
}

function complexityTone(
  complexity: string
): 'orange' | 'blue' | 'green' {
  if (complexity === 'high') return 'orange'
  if (complexity === 'medium') return 'blue'
  return 'green'
}

export default function ProjectOverviewPage() {
  const params = useParams<{ id: string }>()
  const id = params.id

  const {
    project,
    projectType,
    users,
    requirements,
    features,
    loading,
    analyzing,
    error,
    analyze,
  } = useProjectData(id)

  const groupedRequirements = requirements.reduce<Record<string, string[]>>(
    (acc, requirement) => {
      const key = requirement.category.replace('_', ' ')

      if (!acc[key]) {
        acc[key] = []
      }

      acc[key].push(
        requirement.description || requirement.text || ''
      )

      return acc
    },
    {}
  )

  return (
    <AppShell>
      {loading ? (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 16,
          }}
        >
          <div
            className="skeleton skeleton-row"
            style={{ width: '40%', height: 26 }}
          />

          <div
            className="skeleton skeleton-row"
            style={{ width: '70%' }}
          />

          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : !project ? (
        <EmptyState
          icon={<FolderOpen size={26} />}
          title="Project not found"
          description="This project could not be found or you may not have access."
          action={
            <button
              className="auth-login-btn"
              style={{
                width: 'auto',
                display: 'inline-flex',
              }}
              onClick={() => {
                window.location.href = '/dashboard'
              }}
            >
              Back to Dashboard
            </button>
          }
        />
      ) : (
        <>
          <div className="proj-header">
            <div className="proj-header-top">
              <div
                style={{
                  minWidth: 0,
                  flex: 1,
                }}
              >
                <h1>{project.title}</h1>

                <p>{project.description}</p>

                <div className="proj-meta-row">
                  {project.platform && (
                    <span className="proj-meta-chip">
                      <Globe size={13} />
                      {project.platform}
                    </span>
                  )}

                  {project.budget && (
                    <span className="proj-meta-chip">
                      <Wallet size={13} />
                      {project.budget}
                    </span>
                  )}

                  {projectType && (
                    <span className="proj-meta-chip">
                      <ArrowRight size={13} />
                      {projectType}
                    </span>
                  )}
                </div>
              </div>

              <Badge
                variant={
                  project.status === 'draft'
                    ? 'orange'
                    : 'green'
                }
              >
                {project.status}
              </Badge>
            </div>
          </div>

          <ProjectTabs projectId={id} />

          {error && (
            <div className="auth-error mb-16">
              {error}
            </div>
          )}

          {requirements.length === 0 &&
          features.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <BrainCircuit size={26} />
              </div>

              <h3>Not analyzed yet</h3>

              <p>
                Run the AI analysis to extract requirements,
                features, and more.
              </p>

              <button
                className="auth-login-btn"
                style={{
                  width: 'auto',
                  display: 'inline-flex',
                }}
                onClick={() => analyze()}
                disabled={analyzing}
              >
                {analyzing ? (
                  <Loader2
                    size={16}
                    className="spin"
                  />
                ) : (
                  <Wand2 size={16} />
                )}

                {analyzing
                  ? 'Analyzing project...'
                  : 'Analyze Project'}
              </button>
            </div>
          ) : (
            <>
              <div
                className="summary-strip"
                style={{ marginBottom: 24 }}
              >
                {projectType && (
                  <div>
                    <small>PROJECT TYPE</small>
                    <strong>{projectType}</strong>
                  </div>
                )}

                {users.length > 0 && (
                  <div>
                    <small>TARGET USERS</small>
                    <strong>
                      {users.join(', ')}
                    </strong>
                  </div>
                )}

                <div>
                  <small>FEATURES FOUND</small>
                  <strong className="confidence">
                    <span />
                    {features.length}
                  </strong>
                </div>

                <div>
                  <small>REQUIREMENTS</small>
                  <strong className="confidence">
                    <span />
                    {requirements.length}
                  </strong>
                </div>
              </div>

              <div className="section-title">
                <h2>Requirements</h2>
                <span>
                  {requirements.length} extracted
                </span>
              </div>

              <div
                className="requirements-grid"
                style={{ marginBottom: 24 }}
              >
                {Object.entries(
                  groupedRequirements
                ).map(([category, items]) => (
                  <div
                    className="requirement-card"
                    key={category}
                  >
                    <div className="card-kicker">
                      {category}
                    </div>

                    {items.map((item, index) => (
                      <div
                        className="requirement"
                        key={index}
                      >
                        <CheckCircle2 size={14} />
                        {item}
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              <div className="section-title">
                <h2>Key features</h2>
                <span>Prioritized by AI</span>
              </div>

              <div className="feature-list">
                {features.map((feature) => (
                  <div
                    className="feature-row"
                    key={feature.canonical_name}
                  >
                    <div className="feature-icon">
                      <ListChecks size={16} />
                    </div>

                    <div className="feature-copy">
                      <strong>
                        {feature.canonical_name.replace(
                          /_/g,
                          ' '
                        )}
                      </strong>

                      <p>{feature.description}</p>
                    </div>

                    <Badge
                      variant={priorityTone(
                        feature.priority
                      )}
                    >
                      {feature.priority} priority
                    </Badge>

                    <Badge
                      variant={complexityTone(
                        feature.complexity
                      )}
                    >
                      {feature.complexity} complexity
                    </Badge>
                  </div>
                ))}
              </div>

              <div className="button-row">
                <button
                  className="auth-login-btn"
                  style={{
                    width: 'auto',
                    display: 'inline-flex',
                  }}
                  onClick={() => analyze()}
                  disabled={analyzing}
                >
                  {analyzing ? (
                    <Loader2
                      size={16}
                      className="spin"
                    />
                  ) : (
                    <Wand2 size={16} />
                  )}

                  {analyzing
                    ? 'Re-analyzing...'
                    : 'Re-run Analysis'}
                </button>

                <a
                  href={`/projects/${id}/requirements`}
                  style={{
                    textDecoration: 'none',
                    marginLeft: 10,
                  }}
                >
                  <button
                    className="auth-login-btn"
                    style={{
                      width: 'auto',
                      display: 'inline-flex',
                      background: 'var(--primary)',
                    }}
                  >
                    View Requirements
                    <ArrowRight size={16} />
                  </button>
                </a>
              </div>
            </>
          )}
        </>
      )}
    </AppShell>
  )
}