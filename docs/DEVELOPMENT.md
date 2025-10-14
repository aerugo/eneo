# Development Setup Guide

This guide explains how to set up and run the Eneo project locally using `uv` for Python, `pnpm` for Node.js, and `podman` for containerized services.

## Prerequisites

Before starting, make sure you have the following installed:

- **Task**: Task runner for build automation
  ```bash
  brew install go-task/tap/go-task
  ```

- **UV**: Fast Python package installer and resolver
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **pnpm**: Fast, disk space efficient package manager for Node.js
  ```bash
  npm install -g pnpm
  ```

- **Podman & podman-compose**: Container management and orchestration
  ```bash
  brew install podman podman-compose
  ```

## Quick Start

1. **Initial Setup**: Install all dependencies for both backend and frontend
   ```bash
   task setup
   ```

2. **Start Database and Redis**: Start containerized services
   ```bash
   task podman:up
   ```

3. **Run Database Migrations**: Set up the database schema
   ```bash
   task migrate
   ```

4. **Initialize Database**: Set up initial data and configuration
   ```bash
   task init-db
   ```

5. **Start Backend**: Launch the FastAPI backend server
   ```bash
   task run
   ```

6. **Start Worker**: Launch the background worker (in a new terminal)
   ```bash
   task worker
   ```

7. **Start Frontend**: Launch the SvelteKit frontend (in a new terminal)
   ```bash
   task frontend
   ```

## Available Task Commands

### Setup Commands

- **`task setup`**: Install dependencies for both backend and frontend
- **`task setup:backend`**: Install only backend dependencies using `uv`
- **`task setup:frontend`**: Install only frontend dependencies using `pnpm`

### Backend Commands

- **`task run`**: Start the FastAPI backend server on port 8123
  - Uses `uvicorn` with auto-reload for development
  - Backend will be available at `http://127.0.0.1:8123`

- **`task worker`**: Start the background worker process
  - Runs ARQ worker for async task processing
  - Set `LOGLEVEL=DEBUG` for verbose logging

- **`task migrate`**: Run database migrations using Alembic
  - Upgrades the database to the latest schema
  - Must be run after starting the database services

- **`task init-db`**: Initialize database with default data
  - Sets up initial configuration, users, and default content
  - Must be run after `task migrate` on first setup

### Frontend Commands

- **`task frontend`**: Start the SvelteKit development server
  - Runs both the web app and UI package in watch mode
  - Frontend will be available at `http://localhost:3000`

### Database & Redis Commands

- **`task podman:up`**: Start PostgreSQL and Redis containers
- **`task podman:down`**: Stop and remove PostgreSQL and Redis containers
- **`task reset-db`**: Nuke the database and start over. This command will stop the services, delete all data volumes, restart the services, and then run migrations and initial data setup.

## Common Workflows

### Starting Fresh

To completely reset your local environment, including the database:

1.  Stop all running processes (backend, frontend, worker).
2.  Run the reset command:
    ```bash
    task reset-db
    ```
3.  Follow the quick start guide from step 5 onwards to restart the application.

  - PostgreSQL: `localhost:5441` → container port 5432
  - Redis: `localhost:6379` → container port 6379
  - Runs containers in detached mode (`-d`)

- **`task podman:down`**: Stop and remove PostgreSQL and Redis containers
  - Gracefully shuts down all services
  - Container data persists in named volumes

## Development Workflow

### Starting Development

1. Start the infrastructure services:
   ```bash
   task podman:up
   ```

2. Initialize the database (first time only):
   ```bash
   task migrate
   task init-db
   ```

3. Start the backend in one terminal:
   ```bash
   task run
   ```

4. Start the worker in another terminal:
   ```bash
   task worker
   ```

5. Start the frontend in a third terminal:
   ```bash
   task frontend
   ```

### Daily Development

For subsequent development sessions, you typically only need:

```bash
# Start services (if not already running)
task podman:up

# Start backend (terminal 1)
task run

# Start worker (terminal 2)
task worker

# Start frontend (terminal 3)
task frontend
```

### Stopping Development

1. Stop frontend, backend, and worker processes with `Ctrl+C` in each terminal
2. Stop database services:
   ```bash
   task podman:down
   ```

## Configuration

### Backend Configuration

The backend uses environment variables loaded from `backend/.env`. Key settings:

- **Database**: Uses `POSTGRES_*` variables for connection
- **Redis**: Uses `REDIS_*` variables for connection
- **For local development**: Create `backend/.env.local` to override settings:
  ```env
  POSTGRES_HOST=localhost
  REDIS_HOST=localhost
  ```

### Frontend Configuration

The frontend configuration is in:
- `frontend/.env`: Main environment variables
- `frontend/apps/web/.env`: Web app specific settings

Key setting: `INTRIC_BACKEND_URL` should point to `http://localhost:8123`

### Database & Redis Ports

Services are exposed on these ports:
- **PostgreSQL**: `localhost:5441` (mapped from container port 5432)
- **Redis**: `localhost:6379` (direct mapping)

## Troubleshooting

### Backend Issues

**Import Errors**: If you see module import errors, ensure:
- Virtual environment was created: `task setup:backend`
- Python path is correctly set (handled automatically by tasks)

**Database Connection**: If migrations or app startup fails:
- Ensure database is running: `task podman:up`
- Check `.env.local` has correct host settings

### Frontend Issues

**API Connection Errors**: If frontend can't reach backend:
- Ensure backend is running on port 8123: `task run`
- Check `INTRIC_BACKEND_URL` in frontend env files

**Package Issues**: If dependencies are missing:
- Reinstall: `task setup:frontend`
- Clear cache: `pnpm store prune`

### Container Issues

**Port Conflicts**: If ports are already in use:
- Check what's using the port: `lsof -i :5441` or `lsof -i :6379`
- Stop conflicting services or change ports in `compose.yml`

**Permission Issues**: If podman fails:
- Initialize podman machine: `podman machine init && podman machine start`

## Architecture

The development setup uses:

- **Backend**: FastAPI with `uv` for dependency management
- **Frontend**: SvelteKit with `pnpm` workspaces
- **Database**: PostgreSQL with pgvector extension
- **Cache**: Redis for session and application caching
- **Task Runner**: Go Task for build automation
- **Containers**: Podman for infrastructure services

This setup provides fast dependency management, reliable container orchestration, and efficient development workflows.