import Link from 'next/link'
import { Sparkles, ArrowLeft } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="auth-page">
      <div style={{ textAlign: 'center' }}>
        <div className="auth-brand" style={{ marginBottom: 20 }}>
          <span className="auth-brand-mark"><Sparkles /></span>
          ProjectScope <b>AI</b>
        </div>
        <h1 style={{ fontSize: 40, fontWeight: 800, margin: '0 0 8px' }}>404</h1>
        <p style={{ color: 'var(--muted-foreground)', fontSize: 14, margin: '0 0 24px' }}>
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
        <Link href="/dashboard" style={{ textDecoration: 'none' }}>
          <button className="auth-login-btn" style={{ width: 'auto', display: 'inline-flex' }}>
            <ArrowLeft size={16} /> Back to Dashboard
          </button>
        </Link>
      </div>
    </div>
  )
}
