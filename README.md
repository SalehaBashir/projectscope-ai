# projectscope-ai
Turning a rough idea into a real project plan usually means hours of back-and-forth between a client and a dev team — figuring out what needs to be built, who should build it, how long it'll take, and what it'll cost.

ProjectScope AI shortens that process. A user describes their idea in plain English, and the system breaks it down into concrete requirements, 
features, and tasks — then estimates effort, cost, timeline, and risk using a combination of rule-based logic, machine learning, and LLM reasoning. The goal isn't to replace a project manager's judgment, 
but to give founders, clients, and teams a fast, explainable starting point.

## Status
🚧 Actively in development — MVP build in progress.

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | Next.js / React |
| Database | PostgreSQL |
| Machine Learning | scikit-learn, XGBoost |
| AI Layer | LLM provider with structured output |

## Why This Project
Most "idea → estimate" tools either lean entirely on an LLM to guess numbers, or use rigid spreadsheets that can't adapt to unique projects. 
This one keeps the LLM in charge of understanding language and generating explanations, while deterministic code and a trained ML model handle the actual calculations — so estimates stay consistent, explainable, and improve over time as real project data comes in.
