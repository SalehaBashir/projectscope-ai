def get_readme_template(project_name: str, tech_stack: dict, theme: dict) -> str:
    return (
        "# " + project_name + "\n\n"
        "Auto-generated starter project by ProjectScope AI.\n\n"
        "## Tech Stack\n"
        "- Frontend: " + tech_stack.get("frontend", "N/A") + "\n"
        "- Backend: " + tech_stack.get("backend", "N/A") + "\n"
        "- Database: " + tech_stack.get("database", "N/A") + "\n"
        "- Hosting: " + tech_stack.get("hosting", "N/A") + "\n\n"
        "## Theme\n"
        "- Name: " + theme.get("name", "Default") + "\n"
        "- Primary color: " + theme.get("primary_color", "#000000") + "\n"
        "- Font: " + theme.get("font", "Inter") + "\n\n"
        "## Getting Started\n\n"
        "This is a starter scaffold. Business logic, authentication, and features\n"
        "described in your project brief still need to be implemented - this gives\n"
        "you a clean, working foundation to build on.\n\n"
        "See backend/ and frontend/ for setup instructions specific to each.\n"
    )


def get_fastapi_main_template(project_name: str) -> str:
    return (
        "from fastapi import FastAPI\n"
        "from fastapi.middleware.cors import CORSMiddleware\n\n"
        "app = FastAPI(title=\"" + project_name + "\")\n\n"
        "app.add_middleware(\n"
        "    CORSMiddleware,\n"
        "    allow_origins=[\"*\"],\n"
        "    allow_credentials=True,\n"
        "    allow_methods=[\"*\"],\n"
        "    allow_headers=[\"*\"],\n"
        ")\n\n\n"
        "@app.get(\"/\")\n"
        "def root():\n"
        "    return {\"message\": \"" + project_name + " backend is running\"}\n\n\n"
        "@app.get(\"/health\")\n"
        "def health():\n"
        "    return {\"status\": \"ok\"}\n"
    )


def get_fastapi_requirements() -> str:
    return "fastapi\nuvicorn\nsqlalchemy\npsycopg2-binary\npython-dotenv\npydantic\n"


def get_fastapi_readme() -> str:
    return (
        "# Backend Setup\n\n"
        "```\n"
        "python -m venv venv\n"
        "venv\\Scripts\\activate   (Windows)  OR  source venv/bin/activate (Mac/Linux)\n"
        "pip install -r requirements.txt\n"
        "uvicorn app.main:app --reload\n"
        "```\n\n"
        "Visit http://127.0.0.1:8000/docs to see the interactive API docs.\n"
    )


def get_nextjs_page_template(project_name: str, theme: dict) -> str:
    primary = theme.get("primary_color", "#2E7D32")
    font = theme.get("font", "Inter")
    return (
        "export default function Home() {\n"
        "  return (\n"
        "    <main style={{ fontFamily: \"" + font + ", sans-serif\", padding: \"40px\" }}>\n"
        "      <h1 style={{ color: \"" + primary + "\" }}>" + project_name + "</h1>\n"
        "      <p>Your starter frontend is ready. Start building your features here.</p>\n"
        "    </main>\n"
        "  );\n"
        "}\n"
    )


def get_package_json_template(project_name: str) -> str:
    safe_name = project_name.lower().replace(" ", "-")[:40]
    return (
        "{\n"
        "  \"name\": \"" + safe_name + "\",\n"
        "  \"version\": \"0.1.0\",\n"
        "  \"private\": true,\n"
        "  \"scripts\": {\n"
        "    \"dev\": \"next dev\",\n"
        "    \"build\": \"next build\",\n"
        "    \"start\": \"next start\"\n"
        "  },\n"
        "  \"dependencies\": {\n"
        "    \"next\": \"^14.0.0\",\n"
        "    \"react\": \"^18.0.0\",\n"
        "    \"react-dom\": \"^18.0.0\"\n"
        "  }\n"
        "}\n"
    )


def get_frontend_readme() -> str:
    return (
        "# Frontend Setup\n\n"
        "```\n"
        "npm install\n"
        "npm run dev\n"
        "```\n\n"
        "Visit http://localhost:3000\n"
    )