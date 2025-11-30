# Service Dashboard

A transaction monitoring dashboard built with FastAPI and SQLite.

## Setup

1.  **Install `uv`**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Setup Environment**:
    Create a `.env` file in the root directory:
    ```bash
    echo "DATABASE_URL=sqlite:///./sql_app.db" > .env
    ```

4.  **Run the application**:
    ```bash
    uv run uvicorn app.main:app --reload
    ```

## Features

- Real-time transaction monitoring
- Time series visualization
- Card scheme filtering
- Automated data ingestion
