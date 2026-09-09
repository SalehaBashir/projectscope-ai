'use client'

import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import { FolderOpen, Plus, ArrowRight, FilePlus2 } from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { api, ApiError } from '@/lib/api'
import type { Project } from '@/lib/types'

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.listProjects()
      setProjects(data)
    } catch (err) {
      if (err instanceof ApiError && err.status !== 401) {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  return (
    <AppShell>
      <div className="dashboard-hero">
        <div>
          <h1>Projects</h1>
          <p>All of your scoped projects in one place.</p>
        </div>
        <Link href="/projects/new" style={{ textDecoration: 'none' }}>
          <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }}>
            <Plus size={16} /> New Project
          </button>
        </Link>
      </div>

      {error && <div className="auth-error mb-16">{error}</div>}

      {loading ? (
        <div style={{ display: 'grid', gap: 12 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton-card">
              <div className="skeleton skeleton-row" style={{ width: '50%' }} />
              <div className="skeleton skeleton-row" style={{ width: '80%' }} />
            </div>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon"><FolderOpen size={26} /></div>
          <h3>No projects yet</h3>
          <p>Create your first project to get started.</p>
          <Link href="/projects/new" style={{ textDecoration: 'none' }}>
            <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }}>
              <FilePlus2 size={16} /> Create a project
            </button>
          </Link>
        </div>
      ) : (
        <div className="projects-list">
          {projects.map((p) => {
            const status = p.status || 'draft'
            const statusClass = status === 'draft' ? 'draft' : status === 'analyzed' || status === 'analyzing' ? 'analyzed' : status === 'estimating' ? 'estimating' : 'completed'
            return (
              <Link href={`/projects/${p.id}`} key={p.id} className="project-row">
                <div className="project-icon"><FolderOpen size={18} /></div>
                <div className="project-main">
                  <strong>{p.title}</strong>
                  <p>{p.description}</p>
                </div>
                <div className="project-meta">
                  {p.platform && <small>{p.platform}</small>}
                  {p.budget && <small>{p.budget}</small>}
                  <span className={`project-status ${statusClass}`}>{status}</span>
                  <ArrowRight size={16} style={{ color: 'var(--muted-foreground)', flexShrink: 0 }} />
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </AppShell>
  )
}