'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  BrainCircuit, ShieldCheck, Sparkles, Loader2, ArrowRight, Monitor,
  Smartphone, Globe, Wrench,
} from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { api, ApiError } from '@/lib/api'

const platforms = [
  { value: 'Web App', label: 'Web App', icon: Globe, desc: 'Browser-based application' },
  { value: 'Mobile App', label: 'Mobile App', icon: Smartphone, desc: 'iOS / Android native' },
  { value: 'Web + Mobile', label: 'Web + Mobile', icon: Monitor, desc: 'Cross-platform product' },
  { value: 'Internal Tool', label: 'Internal Tool', icon: Wrench, desc: 'Team / ops tools' },
]

export default function NewProjectPage() {
  const router = useRouter()
  const [description, setDescription] = useState('')
  const [budget, setBudget] = useState('')
  const [platform, setPlatform] = useState('Web App')
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState<{ description?: string }>({})
  const [submitting, setSubmitting] = useState(false)

  function validate() {
    const errs: { description?: string } = {}
    if (!description.trim()) errs.description = 'Please describe what you are building.'
    else if (description.trim().length < 10) errs.description = 'Please provide a bit more detail (at least 10 characters).'
    setFieldErrors(errs)
    return Object.keys(errs).length === 0
  }

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault()
    if (submitting) return
    if (!validate()) return
    setError('')
    setSubmitting(true)
    try {
      const title = description.trim().slice(0, 60) + (description.trim().length > 60 ? '...' : '')
      const project = await api.createProject({
        title,
        description,
        budget: budget || undefined,
        platform,
      })
      router.push(`/projects/${project.id}`)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Could not create project. Please try again.')
      }
      setSubmitting(false)
    }
  }

  return (
    <AppShell>
      <div className="view">
        <div className="view-heading">
          <div>
            <div className="eyebrow">NEW PROJECT</div>
            <h1>Start with the big picture</h1>
            <p>Tell us what you&apos;re building. Our AI will turn your idea into a clear, buildable plan.</p>
          </div>
          <span className="ai-chip"><Sparkles size={14} /> AI assisted</span>
        </div>

        <form className="form-card" onSubmit={handleAnalyze}>
          <label>
            Project description
            <span style={{ display: 'block', fontSize: 11.5, color: 'var(--muted-foreground)', marginTop: 2 }}>What are you building?</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
              placeholder="e.g. A mobile app that helps independent coffee shops manage delivery orders, track inventory, and offer loyalty rewards to customers."
            />
            {fieldErrors.description && <span className="text-red" style={{ fontSize: 12 }}>{fieldErrors.description}</span>}
          </label>

          <label>
            Estimated budget <span style={{ fontSize: 11.5, color: 'var(--muted-foreground)' }}>(optional)</span>
            <input
              type="text"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="e.g. $20,000 – $40,000 or 10,000-25,000"
            />
          </label>

          <label>
            Target platform
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 8, marginTop: 4 }}>
              {platforms.map((p) => {
                const Icon = p.icon
                const selected = platform === p.value
                return (
                  <button
                    type="button"
                    key={p.value}
                    onClick={() => setPlatform(p.value)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 10, textAlign: 'left',
                      border: `1.5px solid ${selected ? 'var(--primary)' : 'var(--border)'}`,
                      borderRadius: 10, padding: '12px 14px', background: selected ? 'var(--muted)' : 'var(--card)',
                      cursor: 'pointer', transition: 'border-color .15s, background .15s',
                    }}
                  >
                    <span style={{ color: selected ? 'var(--primary)' : 'var(--muted-foreground)' }}>
                      <Icon size={18} />
                    </span>
                    <span>
                      <strong style={{ display: 'block', fontSize: 13, fontWeight: 700, color: 'var(--foreground)' }}>{p.label}</strong>
                      <small style={{ fontSize: 11, color: 'var(--muted-foreground)' }}>{p.desc}</small>
                    </span>
                  </button>
                )
              })}
            </div>
          </label>

          {error && <div className="auth-error">{error}</div>}

          <div className="form-footer">
            <span><ShieldCheck size={15} /> Your project data stays private</span>
            <button
              type="submit"
              className="auth-login-btn"
              style={{ width: 'auto', display: 'inline-flex' }}
              disabled={submitting}
            >
              {submitting ? <Loader2 size={16} className="spin" /> : <BrainCircuit size={16} />}
              {submitting ? 'Analyzing project...' : 'Analyze Project'}
              {!submitting && <ArrowRight size={16} />}
            </button>
          </div>
        </form>

        <div className="tip-row">
          <Sparkles size={18} />
          <div>
            <strong>Pro tip</strong>
            <p>The more context you share, the more accurate your estimates will be. Include your users, core workflows, and any hard deadlines.</p>
          </div>
        </div>
      </div>
    </AppShell>
  )
}