"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Button, Card, ErrorBanner, PageLoading } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import { downloadScaffoldZip } from "@/lib/endpoints";
import { ApiError } from "@/lib/api";

export default function StartBuildingPage() {
  const { id } = useParams<{ id: string }>();
  const { project, loading, error, reload } = useProject(id);

  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  async function download() {
    setDownloading(true);
    setDownloadError(null);
    try {
      const blob = await downloadScaffoldZip(id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "project_starter.zip";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setDownloadError(
        err instanceof ApiError || err instanceof Error
          ? err.message
          : "Could not generate the starter project.",
      );
    } finally {
      setDownloading(false);
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
          <ErrorBanner message={downloadError} onRetry={download} />
        </div>
      )}

      <Card>
        <h3 className="mb-2 font-semibold">Start building</h3>
        <p className="mb-4 text-sm text-muted">
          Generates a downloadable ZIP with a working FastAPI backend
          skeleton, a Next.js-style frontend skeleton with your selected
          theme applied, a README, folder structure notes and development
          guidelines — based on the tech stack and theme already chosen for
          this project.
        </p>
        <Button variant="primary" loading={downloading} onClick={download}>
          {downloading ? "Generating..." : "Download starter project (.zip)"}
        </Button>
      </Card>
    </div>
  );
}
