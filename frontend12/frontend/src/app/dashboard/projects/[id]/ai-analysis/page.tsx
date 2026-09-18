"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import {
  Card,
  Button,
  Badge,
  PageLoading,
  ErrorBanner,
} from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { analyzeProject, getJobStatus } from "@/lib/endpoints";

export default function AIAnalysisPage() {
  const { id } = useParams<{ id: string }>();
  const { project, pipeline, loading, error, reload } = useProject(id);

  const [description, setDescription] = useState("");
  const [budget, setBudget] = useState("");
  const [platform, setPlatform] = useState("Web");

  const [analyzing, setAnalyzing] = useState(false);
  const [status, setStatus] = useState("");
  const [analysisError, setAnalysisError] = useState("");

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

  const analysis = pipeline.analysis;

  async function handleAnalyze() {
    if (!description.trim()) {
      setAnalysisError("Please describe your project first.");
      return;
    }

    try {
      setAnalyzing(true);
      setAnalysisError("");
      setStatus("Starting AI analysis...");

      const response: any = await analyzeProject(project.id, {
        description: description.trim(),
        budget: budget || undefined,
        platform: platform || undefined,
      });

      const payload = response?.data ?? response;

      if (payload?.status === "completed" && payload?.result) {
        setStatus("Analysis completed successfully.");
        await reload();
        return;
      }

      const jobId = payload?.job_id;

      if (!jobId) {
        throw new Error("Analysis job was not created.");
      }

      setStatus("AI is analyzing your project...");

      let finished = false;

      for (let i = 0; i < 30; i++) {
        await new Promise((resolve) => setTimeout(resolve, 2000));

        const jobResponse: any = await getJobStatus(jobId);
        const job = jobResponse?.data ?? jobResponse;

        if (job?.status === "finished") {
          finished = true;
          setStatus("Analysis completed successfully.");
          await reload();
          break;
        }

        if (job?.status === "failed") {
          throw new Error(
            job?.error || "AI analysis failed."
          );
        }

        if (job?.status === "started") {
          setStatus("AI is analyzing your project...");
        } else {
          setStatus("Waiting for AI analysis...");
        }
      }

      if (!finished) {
        throw new Error(
          "Analysis is taking longer than expected. Please check again shortly."
        );
      }
    } catch (err: any) {
      console.error("AI Analysis Error:", err);

      setAnalysisError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to analyze the project."
      );
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">
          {project.title}
        </h1>

        <p className="mt-1 text-sm text-muted">
          AI-powered project analysis and requirements generation
        </p>
      </div>

      {/* Navigation */}
      <ProjectTabs projectId={project.id} />

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">

        {/* LEFT: AI ANALYSIS FORM */}
        <Card>
          <div className="mb-6">
            <h2 className="text-lg font-semibold">
              AI Analysis
            </h2>

            <p className="mt-1 text-sm text-muted">
              Describe your project and let ProjectScope AI
              generate structured requirements and features.
            </p>
          </div>

          <div className="space-y-5">

            {/* Project Description */}
            <div>
              <label className="mb-2 block text-sm font-medium text-text">
                Project Description
              </label>

              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your project..."
                rows={7}
                className="w-full resize-none rounded-lg border border-border bg-white px-4 py-3 text-sm text-black placeholder:text-gray-500 outline-none transition focus:border-accent"
              />
            </div>

            {/* Budget */}
            <div>
              <label className="mb-2 block text-sm font-medium text-text">
                Budget
              </label>

              <input
                type="text"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="Example: $10,000"
                className="w-full rounded-lg border border-border bg-white px-4 py-3 text-sm text-black placeholder:text-gray-500 outline-none transition focus:border-accent"
              />
            </div>

            {/* Target Platform */}
            <div>
              <label className="mb-2 block text-sm font-medium text-text">
                Target Platform
              </label>

              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full rounded-lg border border-border bg-white px-4 py-3 text-sm text-black outline-none transition focus:border-accent"
              >
                <option value="Web">Web</option>
                <option value="Mobile">Mobile</option>
                <option value="Web & Mobile">
                  Web & Mobile
                </option>
                <option value="Desktop">Desktop</option>
              </select>
            </div>

            {/* Error */}
            {analysisError && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {analysisError}
              </div>
            )}

            {/* Status */}
            {status && !analysisError && (
              <div className="rounded-lg border border-border bg-surface2 px-4 py-3 text-sm text-muted">
                {status}
              </div>
            )}

            {/* Analyze Button */}
            <Button
              variant="primary"
              onClick={handleAnalyze}
              disabled={analyzing}
            >
              {analyzing ? "Analyzing..." : "Analyze with AI"}
            </Button>
          </div>
        </Card>

        {/* RIGHT: ANALYSIS RESULTS */}
        <Card>
          <div className="mb-6">
            <h2 className="text-lg font-semibold">
              Analysis Results
            </h2>

            <p className="mt-1 text-sm text-muted">
              AI-generated project understanding
            </p>
          </div>

          {!analysis ? (
            <div className="rounded-lg border border-dashed border-border p-8 text-center">
              <div className="mb-3 text-3xl">
                ✦
              </div>

              <p className="text-sm font-medium">
                No analysis available yet
              </p>

              <p className="mt-2 text-sm text-muted">
                Enter your project description and run AI
                analysis to generate structured project
                information.
              </p>
            </div>
          ) : (
            <div className="space-y-5">

              {/* Project Type */}
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                  Project Type
                </p>

                <Badge tone="accent">
                  {analysis.project_type || "Not specified"}
                </Badge>
              </div>

              {/* Target Users */}
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                  Target Users
                </p>

                <div className="flex flex-wrap gap-2">
                  {(Array.isArray(analysis.users)
                    ? analysis.users
                    : String(analysis.users || "")
                        .split(/[,|]/)
                        .map((x) => x.trim())
                        .filter(Boolean)
                  ).map((user: string, index: number) => (
                    <Badge
                      key={index}
                      tone="neutral"
                    >
                      {user.replace("_", " ")}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Requirements */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted">
                    Requirements
                  </p>

                  <span className="text-xs font-semibold text-text">
                    {analysis.requirements?.length ?? 0}
                  </span>
                </div>

                <div className="rounded-lg border border-border bg-surface2 p-3">
                  <p className="text-sm text-muted">
                    {analysis.requirements?.length
                      ? "Requirements have been generated successfully."
                      : "No requirements generated."}
                  </p>
                </div>
              </div>

              {/* Features */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted">
                    Features
                  </p>

                  <span className="text-xs font-semibold text-text">
                    {analysis.features?.length ?? 0}
                  </span>
                </div>

                <div className="rounded-lg border border-border bg-surface2 p-3">
                  <p className="text-sm text-muted">
                    {analysis.features?.length
                      ? "Features have been generated successfully."
                      : "No features generated."}
                  </p>
                </div>
              </div>

              {/* Missing Information */}
              {analysis.missing_information?.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                    Missing Information
                  </p>

                  <div className="space-y-2">
                    {analysis.missing_information.map(
                      (item: string, index: number) => (
                        <div
                          key={index}
                          className="rounded-lg border border-border bg-surface2 px-3 py-2 text-sm text-text"
                        >
                          {item}
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

              {/* View Pages */}
              <div className="flex flex-wrap gap-2 pt-2">
                <Link
                  href={`/dashboard/projects/${project.id}/requirements`}
                >
                  <Button variant="secondary">
                    View Requirements
                  </Button>
                </Link>

                <Link
                  href={`/dashboard/projects/${project.id}/features`}
                >
                  <Button variant="secondary">
                    View Features
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}