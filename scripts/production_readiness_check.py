# scripts/production_readiness_check.py
import os
import subprocess
from pathlib import Path

import redis
import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
API_PORT = os.environ.get("API_PORT", "8000")
BASE_URL = f"http://localhost:{API_PORT}"
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
results = {}


def check(name, fn):
    try:
        fn()
        results[name] = "PASS"
        print(f"  [PASS] {name}")
    except Exception as e:
        results[name] = f"FAIL: {e}"
        print(f"  [FAIL] {name}: {e}")


def get(url: str):
    return requests.get(url, timeout=10)


print("\n=== RELIABILITY ===")
check("Health check endpoint", lambda: get(f"{BASE_URL}/health").raise_for_status())
check("API Gateway responds", lambda: get(f"{BASE_URL}/docs").raise_for_status())

print("\n=== OBSERVABILITY ===")
check("Prometheus up", lambda: get("http://localhost:9090/-/healthy").raise_for_status())
check("Grafana up", lambda: get("http://localhost:3000/api/health").raise_for_status())
check("Metrics endpoint exposed", lambda: get(f"{BASE_URL}/metrics").raise_for_status())

print("\n=== SECURITY ===")


def check_unauthorized():
    r = get(f"{BASE_URL}/admin")
    assert r.status_code in [401, 403, 404]


check("Unauthorized request rejected", check_unauthorized)

print("\n=== VECTOR STORE ===")
check("Qdrant healthy", lambda: get("http://localhost:6333/healthz").raise_for_status())


def check_collection_exists():
    r = get("http://localhost:6333/collections/documents")
    r.raise_for_status()
    assert r.json()["result"]["points_count"] > 0


check("Collection exists with vectors", check_collection_exists)

print("\n=== FEATURE STORE ===")
check("Redis reachable", lambda: redis.Redis(host="localhost", port=REDIS_PORT).ping())


def check_features_exist():
    keys = redis.Redis(host="localhost", port=REDIS_PORT, decode_responses=True).keys("feature:*")
    assert keys, "No feature:* keys found"


check("Feature records exist", check_features_exist)

print("\n=== KAFKA ===")


def check_kafka_topics():
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "kafka",
            "kafka-topics",
            "--list",
            "--bootstrap-server",
            "localhost:9092",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "data.raw" in result.stdout


check("Kafka topics exist", check_kafka_topics)

passed = sum(1 for v in results.values() if v == "PASS")
total = len(results)
score = (passed / total) * 100
print(f"\n{'='*40}")
print(f"Production Readiness Score: {passed}/{total} = {score:.0f}%")
print(f"Target: >80% - Status: {'READY' if score >= 80 else 'NOT READY'}")
