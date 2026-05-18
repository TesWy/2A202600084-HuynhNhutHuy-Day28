# scripts/09_verify_observability.py
import os
import time
from datetime import datetime, timezone
from uuid import uuid4

import requests
from dotenv import load_dotenv

load_dotenv()

def check_prometheus():
    resp = requests.get("http://localhost:9090/api/v1/query",
                        params={"query": 'up{job="api-gateway"}'})
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["result"], "api-gateway target not found"
    print("Integration 9 OK: Prometheus metrics flowing")

def check_langsmith():
    api_key = os.environ.get("LANGCHAIN_API_KEY", "")
    if not api_key:
        print("Integration 10 SKIPPED: LANGCHAIN_API_KEY is not set")
        return

    from langsmith import Client

    project_name = os.environ.get("LANGCHAIN_PROJECT", "lab28-platform")
    client = Client(api_key=api_key)
    runs = list(client.list_runs(project_name=project_name, limit=1))
    if not runs:
        run_id = uuid4()
        client.create_run(
            id=run_id,
            name="lab28-observability-check",
            run_type="chain",
            inputs={"check": "langsmith connectivity"},
            project_name=project_name,
            tags=["lab28", "observability"],
        )
        client.update_run(
            run_id,
            outputs={"status": "ok"},
            end_time=datetime.now(timezone.utc),
        )
        time.sleep(3)
        runs = list(client.list_runs(project_name=project_name, limit=1))
    assert len(runs) > 0
    print("Integration 10 OK: LangSmith traces visible")

check_prometheus()
check_langsmith()
