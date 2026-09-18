"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, ErrorBanner, Input, Textarea } from "@/components/ui";
import { analyzeAndWait, createProject } from "@/lib/endpoints";
import { updatePipelineData } from "@/lib/project-store";
import { ApiError } from "@/lib/api";

export default function NewProjectPage() {
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [budget, setBudget] = useState("");
  const [platform, setPlatform] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<"idle" | "creating" | "analyzing">("idle");

  const busy = step !== "idle";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (description.trim().length < 10) {
      setError("Please describe your idea in at least a sentence or two.");
      return;
    }

    // Minimum budget validation
    if (budget.trim()) {
      const budgetValue = Number(budget);

      if (Number.isNaN(budgetValue) || budgetValue < 10000) {
        setError("Minimum project budget must be 10,000.");
        return;
      }
    }

    try {
      setStep("creating");

      const project = await createProject({
        title,
        description,
        budget: budget || undefined,
        platform: platform || undefined,
      });

      setStep("analyzing");

      try {
        const analysis = await analyzeAndWait(project.id, {
          description,
          budget: budget || undefined,
          platform: platform || undefined,
        });

        updatePipelineData(project.id, { analysis });
      } catch {
        // The project was created successfully even if analysis is slow
        // or fails — send the user in and let them retry analysis there
        // instead of losing the project.
      }

      router.push(`/dashboard/projects/${project.id}`);
    } catch (err) {
      setStep("idle");
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not create the project. Please try again.",
      );
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-2xl font-semibold">New project</h1>

      <p className="mb-6 text-sm text-muted">
        Describe your idea in plain English — ProjectScope AI will extract
        requirements and features automatically.
      </p>

      <Card>
        {error && (
          <div className="mb-4">
            <ErrorBanner message={error} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Project title"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Online food delivery app"
            disabled={busy}
          />

          <Textarea
            label="Describe your idea"
            required
            rows={6}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="I want an online food delivery app with customer login, restaurant listings, real-time order tracking, and online payments..."
            disabled={busy}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Budget"
              type="number"
              min="10000"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="Minimum 10000"
              disabled={busy}
            />

            <Input
              label="Platform (optional)"
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              placeholder="e.g. Web + Mobile"
              disabled={busy}
            />
          </div>

          <p className="text-xs text-muted">
            Minimum project budget is 10,000.
          </p>

          <Button
            type="submit"
            variant="primary"
            loading={busy}
            className="w-full"
          >
            {step === "creating" && "Creating project..."}
            {step === "analyzing" && "Running AI analysis..."}
            {step === "idle" && "Create & analyze"}
          </Button>
        </form>
      </Card>
    </div>
  );
}