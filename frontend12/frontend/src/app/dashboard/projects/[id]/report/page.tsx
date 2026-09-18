"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Button, Card, ErrorBanner, PageLoading } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { downloadReport } from "@/lib/endpoints";
import { ApiError } from "@/lib/api";

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const { project, loading, error, reload } = useProject(id);

  const [downloading, setDownloading] = useState<"pdf" | "docx" | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  async function download(format: "pdf" | "docx") {
    setDownloading(format);
    setDownloadError(null);
    try {
      const blob = await downloadReport(id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `projectscope-report.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setDownloadError(
        err instanceof ApiError || err instanceof Error
          ? err.message
          : "Could not generate the report.",
      );
    } finally {
      setDownloading(null);
    }
  }

  if (loading) return <PageLoading label="Loading..." />;
  if (error || !project)
    return <ErrorBanner message={error ?? "Project not found."} onRetry={reload} />;

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{project.title}</h1>
      <ProjectTabs projectId={project.id} />

      {downloadError && (
        <div className="mb-4">
          <ErrorBanner message={downloadError} />
        </div>
      )}

      <Card>
        <h3 className="mb-2 font-semibold">Export report</h3>
        <p className="mb-4 text-sm text-muted">
          Generates a full report — executive summary, requirements,
          features, roles, tasks, effort, cost, timeline, risks, MVP, tech
          recommendations, confidence and limitations — pulled live from the
          backend.
        </p>
        <div className="flex gap-3">
          <Button
            variant="primary"
            loading={downloading === "pdf"}
            onClick={() => download("pdf")}
          >
            Download PDF
          </Button>
          <Button
            variant="secondary"
            loading={downloading === "docx"}
            onClick={() => download("docx")}
          >
            Download Word (.docx)
          </Button>
        </div>
      </Card>
    </div>
  );
}
