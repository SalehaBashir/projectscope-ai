'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  ClipboardList, FileText, ListChecks, ClipboardCheck, BarChart3,
  ShieldAlert, FileCheck2,
} from 'lucide-react'

const tabs = [
  { path: '', label: 'Overview', icon: ClipboardList },
  { path: '/requirements', label: 'Requirements', icon: FileText },
  { path: '/features', label: 'Features', icon: ListChecks },
  { path: '/tasks', label: 'Tasks', icon: ClipboardCheck },
  { path: '/estimate', label: 'Estimate', icon: BarChart3 },
  { path: '/risks', label: 'Risks', icon: ShieldAlert },
  { path: '/plan', label: 'Project Plan', icon: FileCheck2 },
]

export function ProjectTabs({ projectId }: { projectId: string }) {
  const pathname = usePathname()
  return (
    <div className="proj-tabs">
      {tabs.map((tab) => {
        const Icon = tab.icon
        const target = tab.path === '' ? `/projects/${projectId}` : `/projects/${projectId}${tab.path}`
        const active = pathname === target
        return (
          <Link key={tab.label} href={target} className={`proj-tab ${active ? 'active' : ''}`}>
            <Icon /> {tab.label}
          </Link>
        )
      })}
    </div>
  )
}
