"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Button, Card, ErrorBanner, PageLoading } from "@/components/ui";
import { ProjectTabs } from "@/components/shell";
import { useProject } from "@/lib/use-project";
import {
  chooseTheme,
  getSavedTheme,
  getThemeSuggestion,
  listThemes,
} from "@/lib/endpoints";
import type { Theme } from "@/lib/types";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

export default function ThemePage() {
  const { id } = useParams<{ id: string }>();
  const { project, loading: projectLoading, error: projectError, reload } =
    useProject(id);

  const [themes, setThemes] = useState<Theme[]>([]);
  const [saved, setSaved] = useState<Theme | null>(null);
  const [suggested, setSuggested] = useState<Theme | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const all = await listThemes();
      setThemes(all);
      try {
        const savedTheme = await getSavedTheme(id);
        setSaved(savedTheme);
        updatePipelineData(id, { theme: savedTheme });
      } catch (err) {
        // 404 just means no theme has been chosen for this project yet
        if (!(err instanceof ApiError && err.status === 404)) {
          throw err;
        }
        setSaved(null);
      }
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not load themes.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function getSuggestion() {
    setBusy("suggest");
    setError(null);
    try {
      const theme = await getThemeSuggestion(id);
      setSuggested(theme);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not get a suggestion.",
      );
    } finally {
      setBusy(null);
    }
  }

  async function select(themeId?: string) {
    setBusy(themeId ?? "ai");
    setError(null);
    try {
      const theme = await chooseTheme(id, themeId);
      setSaved(theme);
      updatePipelineData(id, { theme });
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not save the theme.",
      );
    } finally {
      setBusy(null);
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

      {loading && <PageLoading label="Loading themes..." />}

      {!loading && (
        <div className="space-y-6">
          {saved && (
            <Card>
              <div className="mb-2 flex items-center justify-between">
                <h3 className="font-semibold">Selected theme</h3>
                <Badge tone="accent">{saved.name}</Badge>
              </div>
              <div className="flex items-center gap-3">
                <span
                  className="h-8 w-8 rounded-full border border-border"
                  style={{ backgroundColor: saved.primary_color }}
                />
                <span
                  className="h-8 w-8 rounded-full border border-border"
                  style={{ backgroundColor: saved.secondary_color }}
                />
                <span className="text-sm text-muted">
                  Font: {saved.font}
                </span>
              </div>
              <p className="mt-3 text-sm text-muted">{saved.description}</p>
            </Card>
          )}

          <Card>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-semibold">AI suggestion</h3>
              <Button
                variant="secondary"
                loading={busy === "suggest"}
                onClick={getSuggestion}
              >
                Get AI suggestion
              </Button>
            </div>
            {suggested && (
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="flex items-center gap-3">
                  <span
                    className="h-6 w-6 rounded-full border border-border"
                    style={{ backgroundColor: suggested.primary_color }}
                  />
                  <div>
                    <p className="text-sm font-medium">{suggested.name}</p>
                    <p className="text-xs text-muted">{suggested.description}</p>
                  </div>
                </div>
                <Button
                  variant="primary"
                  loading={busy === "ai"}
                  onClick={() => select(undefined)}
                >
                  Use this
                </Button>
              </div>
            )}
          </Card>

          <div>
            <h3 className="mb-3 font-semibold">All themes</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {themes.map((theme) => (
                <Card key={theme.id}>
                  <div className="mb-3 flex items-center gap-2">
                    <span
                      className="h-6 w-6 rounded-full border border-border"
                      style={{ backgroundColor: theme.primary_color }}
                    />
                    <span
                      className="h-6 w-6 rounded-full border border-border"
                      style={{ backgroundColor: theme.secondary_color }}
                    />
                  </div>
                  <h4 className="mb-1 font-medium">{theme.name}</h4>
                  <p className="mb-3 text-xs text-muted">{theme.description}</p>
                  <Button
                    variant={saved?.id === theme.id ? "secondary" : "primary"}
                    loading={busy === theme.id}
                    onClick={() => select(theme.id)}
                    className="w-full"
                  >
                    {saved?.id === theme.id ? "Selected" : "Select"}
                  </Button>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
