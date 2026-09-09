'use client'

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { api, setToken, clearToken, getToken } from '@/lib/api'
import type { User } from '@/lib/types'

interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; full_name?: string; organization_name?: string }) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setTokenState] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const t = getToken()
    if (t) {
      setTokenState(t)
      try {
        const payload = JSON.parse(atob(t.split('.')[1]))
        const userId = payload.sub
        const email = payload.email
        if (user === null) {
          setUser({ id: userId, email })
        }
      } catch {
        // invalid token payload
      }
    }
    setLoading(false)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.login({ email, password })
    setToken(res.access_token)
    setTokenState(res.access_token)
    try {
      const payload = JSON.parse(atob(res.access_token.split('.')[1]))
      setUser({ id: payload.sub, email: payload.email })
    } catch {
      setUser({ id: '', email })
    }
  }, [])

  const register = useCallback(async (data: { email: string; password: string; full_name?: string; organization_name?: string }) => {
    const res = await api.register(data)
    setToken(res.access_token)
    setTokenState(res.access_token)
    try {
      const payload = JSON.parse(atob(res.access_token.split('.')[1]))
      setUser({ id: payload.sub, email: payload.email, full_name: data.full_name })
    } catch {
      setUser({ id: '', email: data.email, full_name: data.full_name })
    }
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setTokenState(null)
    setUser(null)
    router.push('/login')
  }, [router])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
