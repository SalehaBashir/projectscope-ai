'use client'

import { useEffect, useState, useCallback } from 'react'
import { api, ApiError } from '@/lib/api'
import type {
  Project, Requirement, Feature, TaskItem, Estimate, Risk, Question,
} from '@/lib/types'

export interface ProjectData {
  project: Project | null
  projectType: string
  users: string[]
  requirements: Requirement[]
  features: Feature[]
  questions: Question[]
  tasks: TaskItem[]
  estimate: Estimate | null
  risks: Risk[]
  loading: boolean
  analyzing: boolean
  generatingTasks: boolean
  estimating: boolean
  generatingRisks: boolean
  error: string
  analyze: () => Promise<boolean>
  generateTasks: () => Promise<void>
  generateEstimate: () => Promise<void>
  generateRisks: () => Promise<void>
  refreshAll: () => Promise<void>
}

export function useProjectData(id: string): ProjectData {
  const [project, setProject] = useState<Project | null>(null)
  const [projectType, setProjectType] = useState('')
  const [users, setUsers] = useState<string[]>([])
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [features, setFeatures] = useState<Feature[]>([])
  const [questions, setQuestions] = useState<Question[]>([])
  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [estimate, setEstimate] = useState<Estimate | null>(null)
  const [risks, setRisks] = useState<Risk[]>([])
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [generatingTasks, setGeneratingTasks] = useState(false)
  const [estimating, setEstimating] = useState(false)
  const [generatingRisks, setGeneratingRisks] = useState(false)
  const [error, setError] = useState('')

  const loadProject = useCallback(async () => {
    try {
      const p = await api.getProject(id)
      setProject(p)
      return p
    } catch (err) {
      if (err instanceof ApiError && err.status !== 401) {
        setError(err.message)
      }
      return null
    }
  }, [id])

  const refreshAll = useCallback(async () => {
    setError('')

    const [pResult, qResult] = await Promise.allSettled([
      api.getProject(id),
      api.getQuestions(id).catch(() => [] as Question[]),
    ])

    if (pResult.status === 'fulfilled') {
      const p = pResult.value
      setProject(p)
      if (qResult.status === 'fulfilled') {
        setQuestions(qResult.value)
      }
    } else if (qResult.status === 'fulfilled') {
      setQuestions(qResult.value)
    }

    setLoading(false)
  }, [id])

  useEffect(() => {
    setLoading(true)
    refreshAll()
  }, [refreshAll])

  const analyze = useCallback(async (): Promise<boolean> => {
    if (!project) {
      const p = await loadProject()
      if (!p) return false
    }
    setAnalyzing(true)
    setError('')
    try {
      const current = project
      if (!current) return false
      const analysis = await api.analyzeProject(id, {
        description: current.description,
        budget: current.budget || undefined,
        platform: current.platform || undefined,
      })
      setProjectType(analysis.project_type || '')
      setUsers(analysis.users || [])
      setRequirements(analysis.requirements || [])
      setFeatures(analysis.features || [])
      return true
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Analysis failed. Please try again.')
      }
      return false
    } finally {
      setAnalyzing(false)
    }
  }, [id, project, loadProject])

  const generateTasks = useCallback(async () => {
    setGeneratingTasks(true)
    setError('')
    try {
      const t = await api.generateTasks(id)
      setTasks(t)
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('Failed to generate tasks.')
    } finally {
      setGeneratingTasks(false)
    }
  }, [id])

  const generateEstimate = useCallback(async () => {
    setEstimating(true)
    setError('')
    try {
      const e = await api.generateEstimate(id)
      setEstimate(e)
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('Failed to calculate estimate.')
    } finally {
      setEstimating(false)
    }
  }, [id])

  const generateRisks = useCallback(async () => {
    setGeneratingRisks(true)
    setError('')
    try {
      const r = await api.generateRisks(id)
      setRisks(r)
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('Failed to generate risks.')
    } finally {
      setGeneratingRisks(false)
    }
  }, [id])

  return {
    project,
    projectType,
    users,
    requirements,
    features,
    questions,
    tasks,
    estimate,
    risks,
    loading,
    analyzing,
    generatingTasks,
    estimating,
    generatingRisks,
    error,
    analyze,
    generateTasks,
    generateEstimate,
    generateRisks,
    refreshAll,
  }
}
