"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  PageLoading,
} from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { calculateEstimate } from "@/lib/endpoints";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

function Stat({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <p className="text-xs uppercase text-muted">
        {label}
      </p>
      <p className="mt-1 text-lg font-semibold">
        {value}
      </p>
    </div>
  );
}

function formatConfidence(confidence: unknown): string {
  if (typeof confidence === "number") {
    return `${Math.round(confidence * 100)}%`;
  }

  if (
    confidence &&
    typeof confidence === "object" &&
    "score" in confidence
  ) {
    const score = Number(
      (confidence as { score?: unknown }).score,
    );

    if (!Number.isNaN(score)) {
      return `${Math.round(score * 100)}%`;
    }
  }

  return "—";
}

function getConfidenceExplanation(confidence: unknown) {
  if (
    confidence &&
    typeof confidence === "object"
  ) {
    const data = confidence as {
      why?: unknown;
      factors?: unknown;
      confidence_why?: unknown;
    };

    return {
      why:
        typeof data.why === "string"
          ? data.why
          : null,

      factors:
        Array.isArray(data.factors)
          ? data.factors.map(String)
          : typeof data.factors === "string"
            ? [data.factors]
            : [],

      confidenceWhy:
        typeof data.confidence_why === "string"
          ? data.confidence_why
          : null,
    };
  }

  return {
    why: null,
    factors: [],
    confidenceWhy: null,
  };
}

export default function EstimatePage() {
  const { id } = useParams<{ id: string }>();

  const {
    project,
    pipeline,
    loading,
    error,
    reload,
    refreshPipeline,
  } = useProject(id);

  const [running, setRunning] = useState(false);
  const [runError, setRunError] =
    useState<string | null>(null);

  async function run() {
    setRunning(true);
    setRunError(null);

    try {
      const estimate = await calculateEstimate(id);

      updatePipelineData(id, { estimate });

      refreshPipeline();
    } catch (err) {
      setRunError(
        err instanceof ApiError
          ? err.message
          : "Could not calculate the estimate.",
      );
    } finally {
      setRunning(false);
    }
  }

  if (loading) {
    return <PageLoading label="Loading..." />;
  }

  if (error || !project) {
    return (
      <ErrorBanner
        message={error ?? "Project not found."}
        onRetry={reload}
      />
    );
  }

  const estimate = pipeline.estimate;

  const confidenceInfo =
    getConfidenceExplanation(
      estimate?.confidence,
    );

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">
        {project.title}
      </h1>

      <ProjectTabs projectId={project.id} />

      {runError && (
        <div className="mb-4">
          <ErrorBanner
            message={runError}
            onRetry={run}
          />
        </div>
      )}

      <div className="mb-4 flex justify-end">
        <Button
          variant="secondary"
          loading={running}
          onClick={run}
        >
          {estimate
            ? "Recalculate"
            : "Calculate estimate"}
        </Button>
      </div>

      {!estimate ? (
        <EmptyState
          title="No estimate yet"
          description="Generate tasks first, then calculate cost, timeline and complexity."
          action={
            <Button
              variant="primary"
              loading={running}
              onClick={run}
            >
              Calculate estimate
            </Button>
          }
        />
      ) : (
        <div className="space-y-6">
          {/* Effort & Cost */}
          <Card>
            <h3 className="mb-4 font-semibold">
              Effort & cost
            </h3>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Stat
                label="Min hours"
                value={`${estimate.min_hours}h`}
              />

              <Stat
                label="Expected hours"
                value={`${estimate.expected_hours}h`}
              />

              <Stat
                label="Max hours"
                value={`${estimate.max_hours}h`}
              />

              <Stat
                label="Complexity"
                value={`${estimate.complexity_score}`}
              />

              <Stat
                label="Min cost"
                value={`$${Number(
                  estimate.min_cost,
                ).toLocaleString()}`}
              />

              <Stat
                label="Expected cost"
                value={`$${Number(
                  estimate.expected_cost,
                ).toLocaleString()}`}
              />

              <Stat
                label="Max cost"
                value={`$${Number(
                  estimate.max_cost,
                ).toLocaleString()}`}
              />

              <Stat
                label="Tasks"
                value={`${estimate.task_count}`}
              />
            </div>
          </Card>

          {/* Timeline */}
          <Card>
            <h3 className="mb-4 font-semibold">
              Timeline
            </h3>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              {estimate.timeline_weeks_min !==
                undefined && (
                <Stat
                  label="Min weeks"
                  value={`${estimate.timeline_weeks_min}`}
                />
              )}

              <Stat
                label="Expected weeks"
                value={`${estimate.timeline_weeks_expected}`}
              />

              {estimate.timeline_weeks_max !==
                undefined && (
                <Stat
                  label="Max weeks"
                  value={`${estimate.timeline_weeks_max}`}
                />
              )}
            </div>
          </Card>

          {/* ML & Reconciliation */}
          {(estimate.ml_predicted_hours !==
            undefined ||
            estimate.hybrid_expected_hours !==
              undefined ||
            estimate.llm_estimated_hours !==
              undefined ||
            estimate.confidence !==
              undefined) && (
            <Card>
              <h3 className="mb-4 font-semibold">
                ML & reconciliation
              </h3>

              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {estimate.ml_predicted_hours !==
                  undefined && (
                  <Stat
                    label="ML predicted"
                    value={`${estimate.ml_predicted_hours}h`}
                  />
                )}

                {estimate.hybrid_expected_hours !==
                  undefined && (
                  <Stat
                    label="Hybrid expected"
                    value={`${estimate.hybrid_expected_hours}h`}
                  />
                )}

                {estimate.llm_estimated_hours !==
                  undefined && (
                  <Stat
                    label="LLM estimated"
                    value={`${estimate.llm_estimated_hours}h`}
                  />
                )}

                {estimate.confidence !==
                  undefined && (
                  <Stat
                    label="Confidence"
                    value={formatConfidence(
                      estimate.confidence,
                    )}
                  />
                )}
              </div>
            </Card>
          )}

          {/* Confidence Explanation */}
          {(confidenceInfo.why ||
            confidenceInfo.factors.length > 0 ||
            confidenceInfo.confidenceWhy) && (
            <Card>
              <h3 className="mb-4 font-semibold">
                Confidence explanation
              </h3>

              {confidenceInfo.why && (
                <div className="mb-4">
                  <p className="mb-1 text-xs font-medium uppercase text-muted">
                    Why
                  </p>

                  <p className="text-sm text-muted">
                    {confidenceInfo.why}
                  </p>
                </div>
              )}

              {confidenceInfo.factors.length >
                0 && (
                <div className="mb-4">
                  <p className="mb-2 text-xs font-medium uppercase text-muted">
                    Factors
                  </p>

                  <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
                    {confidenceInfo.factors.map(
                      (factor, index) => (
                        <li key={index}>
                          {factor}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}

              {confidenceInfo.confidenceWhy && (
                <div>
                  <p className="mb-1 text-xs font-medium uppercase text-muted">
                    Confidence reasoning
                  </p>

                  <p className="text-sm text-muted">
                    {confidenceInfo.confidenceWhy}
                  </p>
                </div>
              )}
            </Card>
          )}

          {/* Explanation */}
          {(estimate.complexity_explanation ||
            estimate.estimation_explanation) && (
            <Card>
              <h3 className="mb-2 font-semibold">
                Explanation
              </h3>

              {estimate.complexity_explanation && (
                <p className="mb-2 text-sm text-muted">
                  {typeof estimate.complexity_explanation ===
                  "string"
                    ? estimate.complexity_explanation
                    : JSON.stringify(
                        estimate.complexity_explanation,
                      )}
                </p>
              )}

              {estimate.estimation_explanation && (
                <p className="text-sm text-muted">
                  {typeof estimate.estimation_explanation ===
                  "string"
                    ? estimate.estimation_explanation
                    : JSON.stringify(
                        estimate.estimation_explanation,
                      )}
                </p>
              )}
            </Card>
          )}
        </div>
      )}
    </div>
  );
}