'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { LogOut, Check, ShieldCheck } from 'lucide-react'
import { AppShell } from '@/components/layout/app-shell'
import { useAuth } from '@/lib/auth-context'

export default function SettingsPage() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [copied, setCopied] = useState(false)

  function handleLogout() {
    logout()
    router.push('/login')
  }

  const displayName = user?.full_name || user?.email?.split('@')[0] || 'User'
  const initial = (user?.full_name || user?.email || 'U').charAt(0).toUpperCase()

  return (
    <AppShell>
      <div className="view">
        <div className="view-heading">
          <div>
            <div className="eyebrow">SETTINGS</div>
            <h1>Settings</h1>
            <p>Manage your account and preferences.</p>
          </div>
        </div>

        <div className="req-card" style={{ maxWidth: 560, marginBottom: 16 }}>
          <div className="req-card-top">
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div className="avatar" style={{ width: 40, height: 40, fontSize: 15 }}>{initial}</div>
              <div>
                <strong style={{ fontSize: 15, fontWeight: 700, display: 'block' }}>{displayName}</strong>
                <span style={{ fontSize: 12.5, color: 'var(--muted-foreground)' }}>{user?.email}</span>
              </div>
            </div>
          </div>
          <div className="req-card-footer" style={{ marginTop: 4 }}>
            <span className="category-tag functional">Member</span>
          </div>
        </div>

        <div className="notice green mb-16" style={{ maxWidth: 560 }}>
          <ShieldCheck size={15} style={{ flexShrink: 0, marginTop: 1 }} />
          <span>Your account data and project plans are private and securely stored.</span>
        </div>

        <div className="button-row">
          <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex', background: 'transparent', color: 'var(--danger)', border: '1px solid var(--danger-bg)' }} onClick={handleLogout}>
            <LogOut size={16} /> Log out
          </button>
        </div>
      </div>
    </AppShell>
  )
}
