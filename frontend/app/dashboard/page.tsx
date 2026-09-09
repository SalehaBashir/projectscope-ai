'use client'

import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import {
  FolderOpen, Clock, CheckCircle2, Plus, ArrowRight, FilePlus2,
  Briefcase, Loader2, Activity, Sparkles,
} from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { api, ApiError } from '@/lib/api'
import type { Project } from '@/lib/types'
import { useAuth } from '@/lib/auth-context'

type ProjectWithMeta = Project & {
  estimated_hours?: number
  estimated_cost?: number
}

export default function DashboardPage() {
  const [projects, setProjects] = useState<ProjectWithMeta[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuth()

  const loadProjects = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.listProjects()
      setProjects(data as ProjectWithMeta[])
    } catch (err) {
      if (err instanceof ApiError && err.status !== 401) {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  const totalProjects = projects.length
  const analyzedCount = projects.filter((p) => p.status && p.status !== 'draft').length
  const activeCount = projects.filter((p) => p.status === 'draft').length

  const firstName = (user?.full_name || user?.email?.split('@')[0] || 'there').split(' ')[0]

  return (
    <AppShell>
      <div className="dashboard-hero">
        <div>
          <h1>Welcome back, {firstName}</h1>
          <p>Turn your ideas into clear, buildable project plans.</p>
        </div>
        <Link href="/projects/new" style={{ textDecoration: 'none' }}>
          <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }}>
            <Plus size={16} /> Create New Project
          </button>
        </Link>
      </div>

      {error && <div className="auth-error mb-16">{error}</div>}

      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-icon purple"><Briefcase size={19} /></div>
          <div className="stat-info">
            <small>TOTAL PROJECTS</small>
            <strong>{totalProjects}</strong>
            <span>in your workspace</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon blue"><Activity size={19} /></div>
          <div className="stat-info">
            <small>ACTIVE PROJECTS</small>
            <strong>{activeCount}</strong>
            <span>in planning</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green"><CheckCircle2 size={19} /></div>
          <div className="stat-info">
            <small>COMPLETED ANALYSES</small>
            <strong>{analyzedCount}</strong>
            <span>analyzed by AI</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon amber"><Clock size={19} /></div>
          <div className="stat-info">
            <small>ESTIMATED HOURS</small>
            <strong>{projects.reduce((sum, p) => sum + (p.estimated_hours || 0), 0) || '—'}</strong>
            <span>across analyzed projects</span>
          </div>
        </div>
      </div>

      <div className="deck-title">
        <h2>Recent projects</h2>
        <Link href="/projects">View all</Link>
      </div>

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
          <p>Create your first project and let the AI analyze it.</p>
          <Link href="/projects/new" style={{ textDecoration: 'none' }}>
            <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }}>
              <FilePlus2 size={16} /> Create your first project
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
