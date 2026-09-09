'use client'

import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export function Badge({
  children,
  variant = 'neutral',
  className,
}: {
  children: ReactNode
  variant?: 'neutral' | 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'amber'
  className?: string
}) {
  return (
    <span
      className={cn(
        'badge',
        variant === 'neutral' && 'badge-neutral',
        variant === 'purple' && 'badge-purple',
        variant === 'blue' && 'badge-blue',
        variant === 'green' && 'badge-green',
        variant === 'orange' && 'badge-orange',
        variant === 'red' && 'badge-red',
        variant === 'amber' && 'badge-amber',
        className,
      )}
    >
      {children}
    </span>
  )
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn('bg-card border border-border rounded-xl', className)}>
      {children}
    </div>
  )
}

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="skeleton-card">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton skeleton-row" style={{ width: `${100 - i * 15}%` }} />
      ))}
    </div>
  )
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon: ReactNode
  title: string
  description: string
  action?: ReactNode
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  )
}

export function PriorityBadge({ priority }: { priority: string }) {
  const tone = priority.toLowerCase()
  return <span className={`priority-badge ${tone}`}>{tone === 'high' ? '● ' : tone === 'medium' ? '● ' : '● '}{tone} priority</span>
}

export function ComplexityBadge({ complexity }: { complexity: string }) {
  const tone = complexity.toLowerCase()
  return <span className={`priority-badge ${tone === 'high' ? 'high' : tone === 'medium' ? 'medium' : 'low'}`}>{complexity} complexity</span>
}

export function SeverityBadge({ level }: { level: string }) {
  const tone = level.toLowerCase()
  const cls = tone === 'high' ? 'high' : tone === 'medium' ? 'medium' : 'low'
  return <span className={`risk-sev ${cls}`}>{tone === 'high' ? '▲' : tone === 'medium' ? '■' : '●'} {tone}</span>
}

export function CategoryTag({ category }: { category: string }) {
  const clean = category.toLowerCase()
  return <span className={`category-tag ${clean}`}>{clean.replace('_', ' ')}</span>
}