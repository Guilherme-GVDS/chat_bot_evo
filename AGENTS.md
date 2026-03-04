# Repository Guidelines

## Project Structure & Module Organization
- `src/chat_bot_evo/app.py`: FastAPI entrypoint exposing `POST /webhook`.
- `src/bot/`: bot orchestration (`chains.py`, `message_buffer.py`, `evolution_api.py`, prompts, memory).
- `src/rag/`: RAG vector store setup and retrieval integration.
- `src/core/config.py`: environment-based configuration loading (`.env`).
- `data/`: runtime data for vector store and RAG source files (mounted in Docker).
- Root infra files: `Dockerfile`, `docker-compose.yml`, `requirements.txt`.

## Build, Test, and Development Commands
- `python -m venv .venv && .\\.venv\\Scripts\\Activate.ps1`: create and activate local env (Windows PowerShell).
- `pip install -r requirements.txt`: install dependencies.
- `uvicorn chat_bot_evo.app:app --host 0.0.0.0 --port 8000 --app-dir src`: run API locally.
- `docker compose up --build`: start bot + Evolution API + Redis + Postgres stack.
- `pytest`: run tests (add tests first; see Testing Guidelines).

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and clear, small functions.
- Use `snake_case` for functions/variables/modules, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Keep async boundaries explicit (`async def`, awaited I/O) in bot and API integrations.
- Prefer type hints on public functions and API client methods.

## Testing Guidelines
- Current repository has no tracked test suite; new features should include tests.
- Place tests under `tests/` mirroring `src/` paths (example: `tests/bot/test_message_buffer.py`).
- Name files `test_*.py`; focus on webhook handling, debounce behavior, and API client error paths.
- Mock external services (`Redis`, `httpx`, LLM/retriever calls) to keep tests deterministic.

## Commit & Pull Request Guidelines
- Use Conventional Commit style seen in history: `feat: ...`, `refactor: ...`.
- Keep commits scoped to one concern and write messages in imperative mood.
- PRs should include: purpose, behavior changes, setup/env changes, and manual verification steps.
- Link related issues and include request/response examples when webhook behavior changes.

## Security & Configuration Tips
- Never commit secrets; `.env` is ignored and should stay local.
- Required runtime values are loaded from `src/core/config.py`; document any new keys in PR descriptions.
