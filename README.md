# Lucas

Lucas is an asynchronous domain management pipeline written in Python. It demonstrates how to coordinate scheduled tasks, store results in a SQLite database and expose a minimal dashboard.

## Features

- **Task orchestration** using APScheduler
- **WebSocket broadcasting** for real‑time updates
- **Rate limiting, retries and circuit breakers** implemented as decorators
- **JSON‑based cache** for long‑running operations
- **React dashboard** served via Vite

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Alternatively run `make dev` to create the virtual environment and install dependencies.

## Configuration

Application settings are provided via environment variables prefixed with `LUCAS_`.
The most important ones are:

| Variable | Description |
| --- | --- |
| `LUCAS_DATABASE_URL` | Path to the SQLite database file. |
| `LUCAS_GITHUB_TOKEN` | Optional GitHub token used when fetching trending repositories. |
| `LUCAS_WHOIS_API_KEY` | API key for WHOIS lookups. |
| `LUCAS_ESTIBOT_API_KEY` | API key for EstiBot valuations. |
| `LUCAS_HUMBLEWORTH_API_KEY` | API key for HumbleWorth valuations. |

Create a `.env` file based on `.env.example` and fill in your credentials.

## Usage

Initialise the database then run the orchestrator:

```bash
alembic upgrade head
python main.py
```

The dashboard UI can be started with:

```bash
make dash
```

This launches the Vite development server serving the React interface under `lucas_project/dashboard/ui`.

## Pipeline modules

The `lucas_project.modules` package contains the scheduled pipeline. Each module exposes a `run` function decorated with `register_job`:

1. **1_trend_discovery** – fetches popular GitHub repositories and stores the names.
2. **2_domain_generator** – generates candidate domain names from stored trends.
3. **3_availability_checker** – checks domain availability (simulated WHOIS calls).
4. **4_valuation** – values available domains using EstiBot, HumbleWorth and GoDaddy.
5. **5_monitoring** – adds domains to uptime monitoring services within free tiers.
6. **6_backordering** – places backorders for monitored domains.
7. **7_portfolio_manager** – exports owned domains as a CSV portfolio each week.
8. **8_monetization** – lists backordered domains on Sedo.

The pipeline relies on helper decorators found in `lucas_project.core.utils`:

- `rate_limiter` – throttle calls to an async function.
- `token_bucket` – asynchronous token bucket implementation.
- `retry` – retry logic with exponential backoff.
- `circuit_breaker` – open/close logic to stop calling failing services.

The `lucas_project.core` package also provides:

- `get_db` – async context manager returning an `aiosqlite` connection.
- `scheduler` and `register_job` – wrappers around APScheduler.
- `LLMCache` and `cache` – JSON cache for long‑running operations.
- `WebSocketBroadcaster` – manage WebSocket clients and broadcast messages.

## External services

For full functionality you will need accounts and API keys for:

- **GitHub** – to retrieve trending repositories via the Search API.
- **WHOIS provider** – to check domain availability.
- **EstiBot** and **HumbleWorth** – domain valuation services.
- **UptimeRobot** and **FreeDomainAlerts** – uptime monitoring services.
- **NoWinNoFee** – backordering provider.
- **Sedo** – domain marketplace for monetization.

Without these accounts the pipeline still runs but will use mock data.

## Testing

Run the test suite with:

```bash
pytest -q
```

---
