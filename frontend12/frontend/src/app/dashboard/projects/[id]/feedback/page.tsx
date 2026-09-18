"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  Input,
  PageLoading,
  Textarea,
} from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import {
  deleteFeedback,
  getFeedbackSummary,
  listFeedback,
  submitFeedback,
} from "@/lib/endpoints";
import type { FeedbackItem, FeedbackSummary } from "@/lib/types";
import { ApiError } from "@/lib/api";

export default function FeedbackPage() {
  const { id } = useParams<{ id: string }>();
  const { project, pipeline, loading: projectLoading, error: projectError, reload } =
    useProject(id);

  const [items, setItems] = useState<FeedbackItem[]>([]);
  const [summary, setSummary] = useState<FeedbackSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [taskId, setTaskId] = useState("");
  const [estimatedHours, setEstimatedHours] = useState("");
  const [actualHours, setActualHours] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [feedbackList, feedbackSummary] = await Promise.all([
        listFeedback(id),
        getFeedbackSummary(id).catch(() => null),
      ]);
      setItems(feedbackList);
      setSummary(feedbackSummary);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not load feedback.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    const actual = parseFloat(actualHours);
    if (!actual || actual <= 0) {
      setFormError("Actual hours must be a number greater than 0.");
      return;
    }

    setSubmitting(true);
    try {
      await submitFeedback(id, {
        task_id: taskId || undefined,
        estimated_hours: estimatedHours ? parseFloat(estimatedHours) : undefined,
        actual_hours: actual,
        notes: notes || undefined,
      });
      setTaskId("");
      setEstimatedHours("");
      setActualHours("");
      setNotes("");
      await load();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not submit feedback.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function remove(feedbackId: string) {
    try {
      await deleteFeedback(id, feedbackId);
      await load();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not delete feedback.",
      );
    }
  }

  const tasks = pipeline.tasks ?? [];

  if (projectLoading) return <PageLoading label="Loading..." />;
  if (projectError || !project)
    return (
      <ErrorBanner message={projectError ?? "Project not found."} onRetry={reload} />
    );

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{project.title}</h1>
      <ProjectTabs projectId={project.id} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-4 font-semibold">Submit actual-project feedback</h3>
          {formError && (
            <div className="mb-4">
              <ErrorBanner message={formError} />
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            {tasks.length > 0 && (
              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-muted">
                  Task (optional)
                </span>
                <select
                  value={taskId}
                  onChange={(e) => setTaskId(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface2 px-3.5 py-2.5 text-sm text-text outline-none focus:border-accent"
                >
                  <option value="">— Whole project —</option>
                  {tasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.title}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <Input
              label="Estimated hours (optional)"
              type="number"
              step="0.1"
              value={estimatedHours}
              onChange={(e) => setEstimatedHours(e.target.value)}
            />
            <Input
              label="Actual hours"
              type="number"
              step="0.1"
              required
              value={actualHours}
              onChange={(e) => setActualHours(e.target.value)}
            />
            <Textarea
              label="Notes (optional)"
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            <Button
              type="submit"
              variant="primary"
              loading={submitting}
              className="w-full"
            >
              Submit feedback
            </Button>
          </form>
        </Card>

        <div className="space-y-6">
          {summary && summary.total_feedback_count > 0 && (
            <Card>
              <h3 className="mb-3 font-semibold">Summary</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs uppercase text-muted">Entries</p>
                  <p className="mt-1 font-semibold">
                    {summary.total_feedback_count}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase text-muted">Total actual hours</p>
                  <p className="mt-1 font-semibold">
                    {summary.total_actual_hours}h
                  </p>
                </div>
                {summary.average_deviation_percent !== null &&
                  summary.average_deviation_percent !== undefined && (
                    <div>
                      <p className="text-xs uppercase text-muted">
                        Avg. deviation
                      </p>
                      <p className="mt-1 font-semibold">
                        {summary.average_deviation_percent.toFixed(1)}%
                      </p>
                    </div>
                  )}
              </div>
            </Card>
          )}

          {loading && <PageLoading label="Loading feedback..." />}
          {!loading && error && <ErrorBanner message={error} onRetry={load} />}

          {!loading && !error && items.length === 0 && (
            <EmptyState title="No feedback submitted yet" />
          )}

          {!loading &&
            !error &&
            items.map((item) => (
              <Card key={item.id}>
                <div className="mb-1 flex items-center justify-between">
                  <p className="text-sm font-medium">
                    {item.actual_hours}h actual
                    {item.estimated_hours !== null &&
                      item.estimated_hours !== undefined &&
                      ` (est. ${item.estimated_hours}h)`}
                  </p>
                  <button
                    onClick={() => remove(item.id)}
                    className="text-xs text-danger underline underline-offset-2"
                  >
                    Delete
                  </button>
                </div>
                {item.notes && (
                  <p className="text-sm text-muted">{item.notes}</p>
                )}
                <p className="mt-1 text-xs text-muted">
                  {new Date(item.created_at).toLocaleString()}
                </p>
              </Card>
            ))}
        </div>
      </div>
    </div>
  );
}
