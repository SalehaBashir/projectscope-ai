def get_readme_template(
    project_name: str,
    tech_stack: dict,
    theme: dict,
    features: list | None = None,
) -> str:
    features = features or []

    feature_lines = "\n".join(
        "- " + str(feature)
        for feature in features
    )

    if not feature_lines:
        feature_lines = "- Project-specific features will be added here."

    return (
        "# " + project_name + "\n\n"
        "Auto-generated starter project by ProjectScope AI.\n\n"
        "## Overview\n\n"
        "This project was automatically scaffolded from a project idea "
        "using ProjectScope AI.\n\n"
        "## Tech Stack\n\n"
        "- Frontend: " + tech_stack.get(
            "frontend", "Next.js + TypeScript"
        ) + "\n"
        "- Backend: " + tech_stack.get(
            "backend", "FastAPI + Python"
        ) + "\n"
        "- Database: " + tech_stack.get(
            "database", "PostgreSQL"
        ) + "\n"
        "- Hosting: " + tech_stack.get(
            "hosting", "Docker / Cloud"
        ) + "\n\n"
        "## Theme\n\n"
        "- Name: " + theme.get(
            "name", "Modern Minimal"
        ) + "\n"
        "- Primary color: " + theme.get(
            "primary_color", "#2E7D32"
        ) + "\n"
        "- Secondary color: " + theme.get(
            "secondary_color", "#F5F5F5"
        ) + "\n"
        "- Font: " + theme.get(
            "font", "Inter"
        ) + "\n\n"
        "## Generated Features\n\n"
        + feature_lines
        + "\n\n"
        "## Project Structure\n\n"
        "- backend/ - FastAPI backend\n"
        "- frontend/ - Next.js web application\n"
        "- mobile/ - Mobile application\n"
        "- shared/ - Shared types\n\n"
        "## Getting Started\n\n"
        "See the README files inside backend/, frontend/, and mobile/.\n"
    )


def get_fastapi_main_template(project_name: str) -> str:
    return (
        "from fastapi import FastAPI\n"
        "from fastapi.middleware.cors import CORSMiddleware\n\n"
        f'app = FastAPI(title="{project_name}", version="0.1.0")\n\n'
        "app.add_middleware(\n"
        "    CORSMiddleware,\n"
        '    allow_origins=["*"],\n'
        "    allow_credentials=True,\n"
        '    allow_methods=["*"],\n'
        '    allow_headers=["*"],\n'
        ")\n\n\n"
        "@app.get('/')\n"
        "def root():\n"
        f'    return {{"message": "{project_name} backend is running"}}\n\n\n'
        "@app.get('/health')\n"
        "def health():\n"
        '    return {"status": "ok"}\n'
    )


def get_fastapi_requirements() -> str:
    return (
        "fastapi\n"
        "uvicorn[standard]\n"
        "sqlalchemy\n"
        "psycopg2-binary\n"
        "python-dotenv\n"
        "pydantic\n"
        "pydantic-settings\n"
    )


def get_fastapi_readme() -> str:
    return (
        "# Backend\n\n"
        "## Setup\n\n"
        "python -m venv venv\n\n"
        "### Windows\n\n"
        "venv\\Scripts\\activate\n\n"
        "### Install\n\n"
        "pip install -r requirements.txt\n\n"
        "## Run\n\n"
        "uvicorn app.main:app --reload\n\n"
        "## API Documentation\n\n"
        "http://127.0.0.1:8000/docs\n\n"
        "## Health Check\n\n"
        "http://127.0.0.1:8000/health\n"
    )


def get_nextjs_page_template(
    project_name: str,
    theme: dict,
    features: list | None = None,
) -> str:
    primary = theme.get("primary_color", "#2E7D32")
    secondary = theme.get("secondary_color", "#F5F5F5")
    font = theme.get("font", "Inter")

    features = features or []

    cards = ""

    for feature in features[:8]:
        cards += (
            '        <div style={{\n'
            '          padding: "20px",\n'
            '          borderRadius: "12px",\n'
            '          backgroundColor: "white",\n'
            '          border: "1px solid #e5e5e5"\n'
            '        }}>\n'
            f"          <h3>{feature}</h3>\n"
            "          <p>Starter implementation for this feature.</p>\n"
            "        </div>\n"
        )

    if not cards:
        cards = (
            '        <div style={{ padding: "20px" }}>\n'
            "          <h3>Project Features</h3>\n"
            "          <p>No features generated yet.</p>\n"
            "        </div>\n"
        )

    return (
        "export default function Home() {\n"
        "  return (\n"
        "    <main\n"
        "      style={{\n"
        '        minHeight: "100vh",\n'
        '        padding: "40px",\n'
        f'        backgroundColor: "{secondary}",\n'
        f'        fontFamily: "{font}, sans-serif"\n'
        "      }}\n"
        "    >\n"
        "      <header>\n"
        f"        <h1 style={{{{ color: \"{primary}\" }}}}>\n"
        f"          {project_name}\n"
        "        </h1>\n"
        "        <p>AI-generated project dashboard</p>\n"
        "        <button\n"
        "          style={{\n"
        '            padding: "12px 20px",\n'
        '            borderRadius: "8px",\n'
        '            border: "none",\n'
        f'            backgroundColor: "{primary}",\n'
        '            color: "white"\n'
        "          }}\n"
        "        >\n"
        "          Get Started\n"
        "        </button>\n"
        "      </header>\n\n"
        "      <section\n"
        "        style={{\n"
        '          display: "grid",\n'
        '          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",\n'
        '          gap: "20px",\n'
        '          marginTop: "40px"\n'
        "        }}\n"
        "      >\n"
        + cards
        + "      </section>\n"
        "    </main>\n"
        "  );\n"
        "}\n"
    )


def get_nextjs_layout_template(
    project_name: str,
    theme: dict,
) -> str:
    font = theme.get("font", "Inter")

    return (
        "export const metadata = {\n"
        f'  title: "{project_name}",\n'
        '  description: "Generated by ProjectScope AI"\n'
        "};\n\n"
        "export default function RootLayout({ children }) {\n"
        "  return (\n"
        '    <html lang="en">\n'
        "      <body\n"
        "        style={{\n"
        '          margin: 0,\n'
        f'          fontFamily: "{font}, sans-serif"\n'
        "        }}\n"
        "      >\n"
        "        {children}\n"
        "      </body>\n"
        "    </html>\n"
        "  );\n"
        "}\n"
    )


def get_package_json_template(project_name: str) -> str:
    safe_name = (
        project_name.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
        .replace("\\", "-")[:40]
    )

    return (
        "{\n"
        f'  "name": "{safe_name}",\n'
        '  "version": "0.1.0",\n'
        '  "private": true,\n'
        '  "scripts": {\n'
        '    "dev": "next dev",\n'
        '    "build": "next build",\n'
        '    "start": "next start"\n'
        "  },\n"
        '  "dependencies": {\n'
        '    "next": "^14.0.0",\n'
        '    "react": "^18.0.0",\n'
        '    "react-dom": "^18.0.0"\n'
        "  },\n"
        '  "devDependencies": {\n'
        '    "typescript": "^5.0.0",\n'
        '    "@types/node": "^20.0.0",\n'
        '    "@types/react": "^18.0.0",\n'
        '    "@types/react-dom": "^18.0.0"\n'
        "  }\n"
        "}\n"
    )


def get_frontend_readme() -> str:
    return (
        "# Web Frontend\n\n"
        "## Install\n\n"
        "npm install\n\n"
        "## Run\n\n"
        "npm run dev\n\n"
        "Open: http://localhost:3000\n\n"
        "## Build\n\n"
        "npm run build\n"
    )


def get_mobile_readme(project_name: str) -> str:
    return (
        "# Mobile App\n\n"
        f"## Project\n\n{project_name}\n\n"
        "## Suggested Stack\n\n"
        "- React Native\n"
        "- TypeScript\n"
        "- Expo\n"
        "- REST API integration\n"
        "- Shared API types\n\n"
        "## Run\n\n"
        "npm install\n"
        "npm start\n"
    )


def get_mobile_package_json(project_name: str) -> str:
    safe_name = (
        project_name.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
        .replace("\\", "-")[:40]
    )

    return (
        "{\n"
        f'  "name": "{safe_name}-mobile",\n'
        '  "version": "0.1.0",\n'
        '  "private": true,\n'
        '  "scripts": {\n'
        '    "start": "expo start"\n'
        "  },\n"
        '  "dependencies": {\n'
        '    "expo": "^51.0.0",\n'
        '    "react": "^18.0.0",\n'
        '    "react-native": "^0.74.0"\n'
        "  },\n"
        '  "devDependencies": {\n'
        '    "typescript": "^5.0.0"\n'
        "  }\n"
        "}\n"
    )


def get_mobile_app_template(
    project_name: str,
    theme: dict,
    features: list | None = None,
) -> str:
    primary = theme.get("primary_color", "#2E7D32")
    secondary = theme.get("secondary_color", "#F5F5F5")

    features = features or []

    feature_text = ""

    for feature in features[:6]:
        feature_text += (
            f'        <Text style={{styles.feature}}>{feature}</Text>\n'
        )

    if not feature_text:
        feature_text = (
            '        <Text style={styles.feature}>Project Features</Text>\n'
        )

    return (
        'import React from "react";\n'
        "import {\n"
        "  SafeAreaView,\n"
        "  Text,\n"
        "  StyleSheet,\n"
        "  ScrollView,\n"
        '} from "react-native";\n\n'
        "export default function App() {\n"
        "  return (\n"
        "    <SafeAreaView style={styles.container}>\n"
        "      <ScrollView contentContainerStyle={styles.content}>\n"
        f"        <Text style={{styles.title}}>{project_name}</Text>\n"
        '        <Text style={styles.subtitle}>\n'
        "          AI-generated mobile starter application\n"
        "        </Text>\n"
        '        <Text style={styles.sectionTitle}>Features</Text>\n'
        + feature_text
        + "      </ScrollView>\n"
        "    </SafeAreaView>\n"
        "  );\n"
        "}\n\n"
        "const styles = StyleSheet.create({\n"
        "  container: {\n"
        "    flex: 1,\n"
        f'    backgroundColor: "{secondary}",\n'
        "  },\n"
        "  content: {\n"
        "    padding: 24,\n"
        "  },\n"
        "  title: {\n"
        "    fontSize: 30,\n"
        "    fontWeight: \"700\",\n"
        f'    color: "{primary}",\n'
        "    marginBottom: 10,\n"
        "  },\n"
        "  subtitle: {\n"
        "    fontSize: 16,\n"
        "    marginBottom: 30,\n"
        "  },\n"
        "  sectionTitle: {\n"
        "    fontSize: 22,\n"
        "    fontWeight: \"600\",\n"
        "    marginBottom: 16,\n"
        "  },\n"
        "  feature: {\n"
        '    backgroundColor: "white",\n'
        "    padding: 16,\n"
        "    borderRadius: 10,\n"
        "    marginBottom: 10,\n"
        "  },\n"
        "});\n"
    )


def get_shared_types_template() -> str:
    return (
        "export interface ApiResponse<T> {\n"
        "  data: T;\n"
        "  message?: string;\n"
        "}\n\n"
        "export interface HealthResponse {\n"
        "  status: string;\n"
        "}\n\n"
        "export interface Project {\n"
        "  id?: string;\n"
        "  title: string;\n"
        "  description?: string;\n"
        "  platform?: string;\n"
        "  budget?: string;\n"
        "}\n\n"
        "export interface Feature {\n"
        "  id?: string;\n"
        "  canonical_name: string;\n"
        "  description?: string;\n"
        "  priority?: string;\n"
        "  complexity?: string;\n"
        "}\n"
    )