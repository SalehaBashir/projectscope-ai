
import Link from "next/link";
import { Button } from "@/components/ui";

export default function LandingPage() {
  const services = [
    {
      title: "AI Project Analysis",
      body: "Turn a simple project idea into a structured analysis with project type, users, requirements, assumptions, and missing information.",
    },
    {
      title: "Requirements & Features",
      body: "Automatically extract clear requirements and features from your project description.",
    },
    {
      title: "Tasks & Team Planning",
      body: "Break features into actionable development tasks and identify the roles needed to build your project.",
    },
    {
      title: "Cost & Timeline Estimation",
      body: "Get estimated effort, project cost, timeline, and workload using deterministic logic and machine learning.",
    },
    {
      title: "Risk & MVP Analysis",
      body: "Identify potential project risks and define an MVP scope so you can focus on the most important features first.",
    },
    {
      title: "Technology Recommendations",
      body: "Get technology and stack recommendations that match your project's requirements and development needs.",
    },
  ];

  const features = [
    "AI-powered project analysis",
    "Structured requirements and features",
    "Task and team allocation",
    "Cost and timeline estimation",
    "Risk detection",
    "MVP recommendations",
    "Technology recommendations",
    "Project report export",
  ];

  return (
    <div className="min-h-screen bg-bg text-text">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-bg/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
              P
            </span>
            <span className="text-lg font-semibold">ProjectScope AI</span>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-muted md:flex">
            <a href="#about" className="transition hover:text-text">
              About
            </a>
            <a href="#services" className="transition hover:text-text">
              Services
            </a>
            <a href="#how-it-works" className="transition hover:text-text">
              How It Works
            </a>
            <a href="#features" className="transition hover:text-text">
              Features
            </a>
            <a href="#contact" className="transition hover:text-text">
              Contact
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost">Log in</Button>
            </Link>

            <Link href="/register">
              <Button variant="primary">Sign up</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto flex max-w-5xl flex-col items-center px-6 py-28 text-center">
        <span className="mb-5 inline-block rounded-full border border-accent/30 bg-accent/10 px-4 py-2 text-xs font-medium text-accent2">
          Idea → Requirements → Cost → Timeline → Risks
        </span>

        <h1 className="max-w-4xl text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
          Turn your project idea into a{" "}
          <span className="text-accent2">complete project plan.</span>
        </h1>

        <p className="mt-6 max-w-3xl text-lg leading-8 text-muted">
          Describe your idea in plain English. ProjectScope AI transforms it
          into requirements, features, tasks, team roles, estimates, risks,
          technology recommendations, and a complete project plan.
        </p>

        <div className="mt-9 flex flex-wrap justify-center gap-4">
          <Link href="/register">
            <Button variant="primary" className="px-7 py-3 text-base">
              Start a project
            </Button>
          </Link>

          <Link href="/login">
            <Button variant="secondary" className="px-7 py-3 text-base">
              I already have an account
            </Button>
          </Link>
        </div>
      </section>

      {/* About */}
      <section id="about" className="border-y border-border bg-surface/40">
        <div className="mx-auto max-w-6xl px-6 py-24">
          <div className="max-w-3xl">
            <span className="text-sm font-semibold uppercase tracking-wider text-accent2">
              About ProjectScope AI
            </span>

            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              From an idea to a development-ready plan
            </h2>

            <p className="mt-5 leading-8 text-muted">
              ProjectScope AI helps founders, developers, students, and teams
              understand what it takes to build a software project before
              development begins.
            </p>

            <p className="mt-4 leading-8 text-muted">
              Instead of starting with scattered notes and assumptions,
              ProjectScope AI organizes your idea into structured
              requirements, features, tasks, estimates, risks, team roles,
              and technology recommendations.
            </p>
          </div>
        </div>
      </section>

      {/* Services */}
      <section id="services" className="mx-auto max-w-6xl px-6 py-24">
        <div className="text-center">
          <span className="text-sm font-semibold uppercase tracking-wider text-accent2">
            Our Services
          </span>

          <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
            Everything you need to scope your project
          </h2>

          <p className="mx-auto mt-4 max-w-2xl text-muted">
            ProjectScope AI provides the planning tools needed to move from an
            initial idea toward development.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <div
              key={service.title}
              className="rounded-2xl border border-border bg-surface p-6 transition hover:-translate-y-1 hover:border-accent/50"
            >
              <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent2">
                ✓
              </div>

              <h3 className="text-lg font-semibold">{service.title}</h3>

              <p className="mt-3 text-sm leading-7 text-muted">
                {service.body}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-y border-border bg-surface/40">
        <div className="mx-auto max-w-6xl px-6 py-24">
          <div className="text-center">
            <span className="text-sm font-semibold uppercase tracking-wider text-accent2">
              How It Works
            </span>

            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              Four simple steps
            </h2>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-4">
            {[
              {
                number: "01",
                title: "Describe",
                body: "Tell us about your project idea in plain English.",
              },
              {
                number: "02",
                title: "Analyze",
                body: "AI extracts requirements, features, assumptions, and missing information.",
              },
              {
                number: "03",
                title: "Plan",
                body: "Generate tasks, roles, costs, timeline, risks, MVP, and technology recommendations.",
              },
              {
                number: "04",
                title: "Build",
                body: "Use the generated project plan as your development roadmap.",
              },
            ].map((step) => (
              <div
                key={step.number}
                className="rounded-2xl border border-border bg-surface p-6"
              >
                <span className="text-sm font-bold text-accent2">
                  {step.number}
                </span>

                <h3 className="mt-4 text-xl font-semibold">{step.title}</h3>

                <p className="mt-3 text-sm leading-7 text-muted">
                  {step.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-6xl px-6 py-24">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <span className="text-sm font-semibold uppercase tracking-wider text-accent2">
              Features
            </span>

            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              A complete project scoping workspace
            </h2>

            <p className="mt-5 leading-8 text-muted">
              Keep your project planning organized in one place, from the
              initial idea through estimates, risks, technology decisions, and
              reporting.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {features.map((feature) => (
              <div
                key={feature}
                className="flex items-center gap-3 rounded-xl border border-border bg-surface p-4"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent/10 text-sm text-accent2">
                  ✓
                </span>

                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why ProjectScope */}
      <section className="border-y border-border bg-surface/40">
        <div className="mx-auto max-w-6xl px-6 py-24">
          <div className="text-center">
            <span className="text-sm font-semibold uppercase tracking-wider text-accent2">
              Why ProjectScope AI
            </span>

            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              Plan before you build
            </h2>

            <p className="mx-auto mt-5 max-w-2xl leading-8 text-muted">
              ProjectScope AI combines AI analysis with structured project
              planning and estimation logic to help turn an idea into an
              actionable roadmap.
            </p>
          </div>

          <div className="mx-auto mt-12 grid max-w-4xl gap-6 md:grid-cols-3">
            <div className="rounded-2xl border border-border bg-surface p-6 text-center">
              <h3 className="font-semibold">Save Planning Time</h3>
              <p className="mt-3 text-sm leading-7 text-muted">
                Generate structured project information without starting from
                scratch.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-surface p-6 text-center">
              <h3 className="font-semibold">Make Better Estimates</h3>
              <p className="mt-3 text-sm leading-7 text-muted">
                Understand expected effort, cost, timeline, and workload.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-surface p-6 text-center">
              <h3 className="font-semibold">Reduce Uncertainty</h3>
              <p className="mt-3 text-sm leading-7 text-muted">
                Identify missing information, risks, and MVP priorities early.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-5xl px-6 py-24 text-center">
        <div className="rounded-3xl border border-accent/20 bg-accent/10 px-6 py-16">
          <h2 className="text-3xl font-bold sm:text-4xl">
            Ready to scope your next project?
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-muted">
            Start with your idea and let ProjectScope AI turn it into a
            structured project plan.
          </p>

          <div className="mt-8">
            <Link href="/register">
              <Button variant="primary" className="px-8 py-3 text-base">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Contact */}
      <section id="contact" className="border-t border-border">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <div className="grid gap-8 md:grid-cols-2">
            <div>
              <h2 className="text-2xl font-bold">Contact</h2>
              <p className="mt-3 max-w-md text-sm leading-7 text-muted">
                Have questions about ProjectScope AI or want to learn more?
                Get in touch with the ProjectScope team.
              </p>
            </div>

            <div className="md:text-right">
              <p className="text-sm text-muted">ProjectScope AI</p>
              <p className="mt-2 text-sm text-muted">
                AI-powered project planning and estimation
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-8 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-xs font-bold text-white">
              P
            </span>
            <span className="text-sm font-semibold">ProjectScope AI</span>
          </div>

          <div className="flex flex-wrap gap-5 text-sm text-muted">
            <a href="#about" className="hover:text-text">
              About
            </a>
            <a href="#services" className="hover:text-text">
              Services
            </a>
            <a href="#features" className="hover:text-text">
              Features
            </a>
            <a href="#contact" className="hover:text-text">
              Contact
            </a>
            <Link href="/login" className="hover:text-text">
              Login
            </Link>
          </div>

          <p className="text-xs text-muted">
            © {new Date().getFullYear()} ProjectScope AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
