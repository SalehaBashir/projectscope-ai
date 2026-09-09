'use client'

import { useState, useEffect, type ReactNode } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  Sparkles, LayoutDashboard, FolderOpen, FilePlus, Settings2, LogOut,
  ChevronDown, ChevronRight, X, Menu, CircleHelp, ClipboardList, FileText, ListChecks,
  ClipboardCheck, BarChart3, ShieldAlert, FileCheck2, Loader2,
} from 'lucide-react'
import { useAuth } from '@/lib/auth-context'

const mainNav = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/projects', label: 'Projects', icon: FolderOpen },
  { href: '/projects/new', label: 'Create Project', icon: FilePlus },
  { href: '/settings', label: 'Settings', icon: Settings2 },
]

const projectTabs = [
  { path: '', label: 'Overview', icon: ClipboardList },
  { path: '/requirements', label: 'Requirements', icon: FileText },
  { path: '/features', label: 'Features', icon: ListChecks },
  { path: '/tasks', label: 'Tasks', icon: ClipboardCheck },
  { path: '/estimate', label: 'Estimate', icon: BarChart3 },
  { path: '/risks', label: 'Risks', icon: ShieldAlert },
  { path: '/plan', label: 'Project Plan', icon: FileCheck2 },
]

export function AppShell({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { user, logout, loading } = useAuth()
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [loading, user, router])

  if (loading) {
    return (
      <div className="auth-page">
        <Loader2 size={28} className="spin" style={{ color: 'var(--primary)' }} />
      </div>
    )
  }

  if (!user) return null

  const displayName = user.full_name || user.email?.split('@')[0] || 'User'
  const initial = (user.full_name || user.email || 'U').charAt(0).toUpperCase()

  const projectId = extractProjectId(pathname)
  const isProjectPage = !!projectId && pathname.includes('/projects/')

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <Link href="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: 9, textDecoration: 'none', color: 'inherit' }}>
            <span className="brand-mark"><Sparkles size={16} /></span>
            <span>ProjectScope <b>AI</b></span>
          </Link>
          <button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><X size={18} /></button>
        </div>

        <div className="workspace">
          <span className="workspace-dot" /> My Workspace <ChevronDown size={14} />
        </div>

        <nav className="step-nav" aria-label="Main navigation">
          <div className="nav-label">WORKSPACE</div>
          {mainNav.map((item) => {
            const Icon = item.icon
            const active =
              item.href === '/dashboard' ? pathname === '/dashboard'
              : item.href === '/projects' ? (pathname === '/projects' || pathname === '/')
              : item.href === '/projects/new' ? pathname === '/projects/new'
              : item.href === '/settings' ? pathname === '/settings'
              : false
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`step-link ${active ? 'active' : ''}`}
                onClick={() => setMobileOpen(false)}
              >
                <span className="step-icon"><Icon size={15} /></span>
                <span>{item.label}</span>
              </Link>
            )
          })}

          {isProjectPage && (
            <>
              <div className="nav-label" style={{ marginTop: 18 }}>PROJECT</div>
              {projectTabs.map((tab) => {
                const Icon = tab.icon
                const target = tab.path === '' ? `/projects/${projectId}` : `/projects/${projectId}${tab.path}`
                const active = tab.path === '' ? pathname === target : pathname === target
                return (
                  <Link
                    key={tab.label}
                    href={target}
                    className={`step-link ${active ? 'active' : ''}`}
                    onClick={() => setMobileOpen(false)}
                  >
                    <span className="step-icon"><Icon size={15} /></span>
                    <span>{tab.label}</span>
                  </Link>
                )
              })}
            </>
          )}
        </nav>

        <div className="sidebar-bottom">
          <button className="side-action"><CircleHelp size={16} /> Help center</button>
          <button className="side-action" onClick={logout}><LogOut size={16} /> Logout</button>
          <div className="profile">
            <div className="avatar">{initial}</div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 12, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{displayName}</div>
              <div style={{ fontSize: 11, color: 'var(--muted-foreground)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.email}</div>
            </div>
          </div>
        </div>
      </aside>

      {mobileOpen && <button className="mobile-overlay" onClick={() => setMobileOpen(false)} aria-label="Close navigation overlay" />}

      <main className="main-area">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Menu size={20} /></button>
          <div className="crumb">
            <span>ProjectScope AI</span>
            <ChevronRight size={14} />
            <strong>
              {pathname === '/dashboard' ? 'Dashboard'
                : pathname === '/projects' ? 'Projects'
                : pathname === '/projects/new' ? 'Create Project'
                : pathname === '/settings' ? 'Settings'
                : isProjectPage && !pathname.endsWith('/requirements') && !pathname.endsWith('/features')
                  && !pathname.endsWith('/tasks') && !pathname.endsWith('/estimate')
                  && !pathname.endsWith('/risks') && !pathname.endsWith('/plan') ? 'Project Overview'
                : isProjectPage ? 'Project' : 'Workspace'}
            </strong>
          </div>
          <div className="top-actions">
            <div className="online"><span /> Connected</div>
          </div>
        </header>
        <div className="content">{children}</div>
      </main>
    </div>
  )
}

function extractProjectId(pathname: string): string | null {
  const parts = pathname.split('/').filter(Boolean)
  const idx = parts.indexOf('projects')
  if (idx >= 0 && parts[idx + 1] && parts[idx + 1] !== 'new' && parts[idx + 1] !== '') {
    return parts[idx + 1]
  }
  return null
}
