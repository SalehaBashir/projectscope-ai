"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Button, Card, EmptyState, ErrorBanner, Input, PageLoading } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { answerQuestion, getQuestions } from "@/lib/endpoints";
import type { Question } from "@/lib/types";
import { ApiError } from "@/lib/api";

export default function QuestionsPage() {
  const { id } = useParams<{ id: string }>();
  const { project, loading: projectLoading, error: projectError, reload } =
    useProject(id);

  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getQuestions(id);
      setQuestions(data);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to load follow-up questions.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function submitAnswer(questionId: string) {
    const answer = answers[questionId]?.trim();
    if (!answer) return;
    setSubmitting(questionId);
    try {
      await answerQuestion(id, questionId, answer);
      // Answered questions correctly disappear from the relevant list.
      await load();
      setAnswers((prev) => {
        const next = { ...prev };
        delete next[questionId];
        return next;
      });
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not save your answer.",
      );
    } finally {
      setSubmitting(null);
    }
  }

  if (projectLoading) return <PageLoading label="Loading..." />;
  if (projectError || !project)
    return (
      <ErrorBanner message={projectError ?? "Project not found."} onRetry={reload} />
    );

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{project.title}</h1>
      <ProjectTabs projectId={project.id} />

      {error && (
        <div className="mb-4">
          <ErrorBanner message={error} onRetry={load} />
        </div>
      )}

      {loading && <PageLoading label="Loading questions..." />}

      {!loading && questions && questions.length === 0 && (
        <EmptyState
          title="No open questions"
          description="Either every high-impact question has been answered, or none apply to this project yet."
        />
      )}

      {!loading && questions && questions.length > 0 && (
        <div className="space-y-3">
          {questions.map((q) => (
            <Card key={q.id}>
              <div className="mb-3 flex items-start justify-between gap-2">
                <p className="text-sm font-medium">{q.description}</p>
                {q.category && <Badge tone="accent">{q.category}</Badge>}
              </div>
              <div className="flex gap-2">
                <Input
                  placeholder="Your answer"
                  value={answers[q.id] ?? ""}
                  onChange={(e) =>
                    setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))
                  }
                  className="flex-1"
                />
                <Button
                  variant="primary"
                  loading={submitting === q.id}
                  onClick={() => submitAnswer(q.id)}
                >
                  Save
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
