# AI Support Copilot

Hi Everyone,
This is my personal project for AI Support Copilot. Currently, this project will focus on Document RAG System, but in the near future, I am planning to elevate this project into Agentic RAG with MCP.

The project demonstrates how to build an AI application with:

- **Python + FastAPI** — backend/API
- **LangGraph** — agent/workflow orchestration
- **RAG (Retrieval-Augmented Generation)** — knowledge retrieval
- **PostgreSQL + pgvector** — database and vector search
- **Pydantic** — request/response validation and structured data
- **Docker Compose** — local infrastructure
- **Prometheus** — application metrics
- **Next.js** — frontend (added/connected in later stages)

For now, this README note focuses on getting the **backend API running locally**. Frontend, deployment, CI/CD, and production hosting are outside the scope of this setup guide. Hence, some developer toolkits installations are required.

---

## 1. Prerequisites

You'll need:
<table>
  <thead>
    <tr>
      <th align="left">Software</th>
      <th align="left">Recommended version</th>
      <th align="left">Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Git</td>
      <td>Latest stable</td>
      <td>Source control</td>
    </tr>
    <tr>
      <td>Python</td>
      <td>3.12+</td>
      <td>Backend runtime</td>
    </tr>
    <tr>
      <td>Docker Desktop</td>
      <td>Latest stable</td>
      <td>PostgreSQL and local services</td>
    </tr>
    <tr>
      <td>Docker Compose</td>
      <td>Included with Docker Desktop</td>
      <td>Run local services</td>
    </tr>
    <tr>
      <td>VS Code</td>
      <td>Latest stable</td>
      <td>Recommended editor</td>
    </tr>
  </tbody>
</table>

> **Important:** Never commit API keys, passwords, `.env`, or other secrets to GitHub.

---

# 2. Install Git

## Windows

Download and install Git from:

https://git-scm.com/downloads

After installation, open PowerShell and verify:

```powershell
git --version
```

You should see something similar to:

```text
git version 2.x.x
```

---

# 3. Install Python

## Windows

Download Python from:

https://www.python.org/downloads/

I recommend to use Python **3.12 or newer**.

During installation:

1. Start the installer.
2. **Enable "Add python.exe to PATH".**
3. Choose **Install Now**.

Verify the installation:

```powershell
python --version
```

You should see:

```text
Python 3.12.x
```

If `python` is not recognized, try:

```powershell
py --version
```

---

# 4. Install Docker Desktop

Download Docker Desktop from:

https://www.docker.com/products/docker-desktop/

Install Docker Desktop and start it.

Verify Docker:

```powershell
docker --version
```

Verify Docker Compose:

```powershell
docker compose version
```

You should see a Docker version and a Docker Compose version.

### Windows note

Docker Desktop may ask you to enable/install **WSL 2**. Follow Docker Desktop's installation instructions if prompted.

After installation, make sure Docker Desktop is running before starting the database.

---

# 5. Clone the Project

If you are cloning the GitHub repository:

```powershell
https://github.com/rickysusanto18/ai-support-copilot
cd ai-support-copilot
```

If you already have the project locally:

```powershell
cd <path-to-your-project>
```

---

# 6. Create a Python Virtual Environment

Move into the backend directory:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see something similar to:

```text
(.venv) PS C:\...\ai-support-copilot\backend>
```

### If PowerShell blocks activation

Run PowerShell as your normal user and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 7. Upgrade pip

With the virtual environment activated:

```powershell
python -m pip install --upgrade pip
```

Verify:

```powershell
pip --version
```

---

# 8. Install Python Dependencies

The project's Python dependencies are defined in:

```text
backend/requirements.txt
```

Install them with:

```powershell
pip install -r requirements.txt
```

Verify that FastAPI is installed:

```powershell
pip show fastapi
```

---

# 9. Configure Environment Variables

Go back to the project root:

```powershell
cd ..
```

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

If `.env.example` does not exist yet, create `.env` manually.

A typical configuration will look similar to:

```env
APP_ENV=development

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_support

OPENAI_API_KEY=your_api_key_here
```

The exact variables should match the application's `core/config.py` configuration.

### Security

Never commit the real `.env` file.

The repository should contain:

```text
.env.example    # safe template — commit this
.env            # real secrets — DO NOT commit
```

The `.gitignore` file already excludes `.env`.

---

# 10. Start PostgreSQL with Docker

From the project root:

```powershell
docker compose up -d
```

Check the running containers:

```powershell
docker compose ps
```

You should see the PostgreSQL service running.

To view logs:

```powershell
docker compose logs -f
```

Press:

```text
Ctrl + C
```

to stop following the logs.

---

# 11. Verify PostgreSQL

Check the database container:

```powershell
docker compose ps
```

If PostgreSQL is running correctly, its status should indicate that the container is running.

You can also inspect PostgreSQL logs:

```powershell
docker compose logs postgres
```

If your service has a different name, use:

```powershell
docker compose config --services
```

to list the services defined in `docker-compose.yml`.

---

# 12. Initialize the Database

The backend contains database initialization code under:

```text
backend/app/db/
```

If the project exposes a database initialization module, run:

```powershell
python -m app.db.init_db
```

If database initialization is handled automatically by the application, this step can be skipped.

The purpose of this step is to make sure the PostgreSQL database and required tables are ready before using the API.

---

# 13. Start the FastAPI Server

Make sure you are inside the `backend` directory and that the virtual environment is activated:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

The API should start on:

```text
http://127.0.0.1:8000
```

You should see output similar to:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

# 14. Verify the API

Open your browser and visit:

```text
http://127.0.0.1:8000
```

If the project defines a root endpoint, you should receive its response.

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You should see the **Swagger UI**.

You can also open:

```text
http://127.0.0.1:8000/redoc
```

for the ReDoc documentation.

---

# 15. Test the API from PowerShell

You can test the server without opening a browser.

For example:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/docs
```

Or, if a health endpoint exists:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

A successful response means the API server is reachable.

---

# 16. Running the Project Every Time

After the initial setup, the normal development workflow is:

### Terminal 1 — Start infrastructure

From the project root:

```powershell
docker compose up -d
```

### Terminal 2 — Start the API

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# 17. Stopping the Project

Stop the FastAPI server with:

```text
Ctrl + C
```

Stop the Docker services:

```powershell
docker compose down
```

> `docker compose down` stops and removes the containers. Depending on the Docker Compose configuration, database data may be preserved in a Docker volume.

---

# 18. Useful Docker Commands

### Start services

```powershell
docker compose up -d
```

### Stop services

```powershell
docker compose down
```

### See running services

```powershell
docker compose ps
```

### View logs

```powershell
docker compose logs -f
```

### View PostgreSQL logs

```powershell
docker compose logs -f postgres
```

### Rebuild services

```powershell
docker compose up -d --build
```

---

# 19. Useful Python Commands

### Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Deactivate virtual environment

```powershell
deactivate
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Update dependencies file

```powershell
pip freeze > requirements.txt
```

> Only update `requirements.txt` intentionally. Avoid accidentally adding unrelated global packages.

---

# 20. Git Safety Checklist

Before pushing the project to GitHub, check that these are **not** committed:

```text
.env
.venv/
__pycache__/
*.pyc
*.db
*.sqlite3
models/
chroma/
chroma_db/
uploads/
outputs/
data/raw/
data/processed/
*.log
```

Check Git:

```powershell
git status
```

If a secret was accidentally staged:

```powershell
git restore --staged .env
```

If a secret has already been pushed to GitHub, **do not simply delete the file and assume the secret is safe**. Rotate/revoke the exposed credential immediately.

---

# 21. Troubleshooting

## `python` is not recognized

Try:

```powershell
py --version
```

If that works, create the environment with:

```powershell
py -3.12 -m venv .venv
```

If neither works, reinstall Python and make sure Python is added to PATH.

---

## `pip` is not recognized

Use:

```powershell
python -m pip --version
```

Instead of:

```powershell
pip --version
```

You can also install dependencies with:

```powershell
python -m pip install -r requirements.txt
```

---

## Docker is not running

Start Docker Desktop and verify:

```powershell
docker info
```

If Docker returns a daemon/connection error, Docker Desktop is probably not running yet.

---

## PostgreSQL connection error

Check:

```powershell
docker compose ps
```

Then:

```powershell
docker compose logs postgres
```

Also verify that `DATABASE_URL` in `.env` matches the PostgreSQL configuration in `docker-compose.yml`.

---

## Port 8000 is already in use

Start FastAPI on another port:

```powershell
uvicorn app.main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001/docs
```

---

## Import error when starting FastAPI

Make sure:

1. You are inside `backend/`.
2. The virtual environment is activated.
3. Dependencies are installed.

Run:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then:

```powershell
uvicorn app.main:app --reload
```

---

# 22. Definition of Done

The local backend setup is complete when all of the following work:

- [ ] Git is installed
- [ ] Python is installed
- [ ] Docker Desktop is installed and running
- [ ] Docker Compose works
- [ ] Python virtual environment is created
- [ ] Python dependencies are installed
- [ ] `.env` is configured
- [ ] PostgreSQL is running through Docker
- [ ] Database initialization succeeds
- [ ] FastAPI starts successfully
- [ ] `http://127.0.0.1:8000/docs` opens successfully
- [ ] API endpoints can be tested from Swagger UI

At this point, the **AI Support Copilot backend is running locally** and is ready for the next development stage.

---

## Project Roadmap

The project will be developed incrementally:

1. **Backend foundation** ← current setup
2. Database and document ingestion
3. RAG pipeline
4. Embeddings and vector search
5. LangGraph agent workflow
6. Ticket lookup tool
7. Structured AI responses
8. API integration
9. Next.js frontend
10. Observability and Prometheus metrics
11. Automated tests
12. GitHub Actions CI
13. Dockerized full application
14. Production deployment

