# Evidence Manifest

Primary evidence for submission:

- `prefect_ui.png`: real browser screenshot from the running Prefect UI at `localhost:4200`.
- `api_gateway.png`: real browser screenshot from the running API Gateway `/health` endpoint.
- `grafana_dashboard.png`: real browser screenshot from the running Grafana dashboard.
- `prometheus_targets.png`: real browser screenshot from the running Prometheus targets page.
- `qdrant_dashboard.png`: real browser screenshot from the running Qdrant dashboard.
- `api_gateway_chat_response.json`: raw API Gateway response showing `mode: vllm` and the Qwen model.
- `api_gateway_chat_response.png`: rendered preview of `api_gateway_chat_response.json`.
- `smoke_tests_results.txt`: raw terminal output from `pytest smoke-tests -v`.
- `smoke_test_evidence.png`: real terminal screenshot of the smoke test run.
- `smoke_tests_results.png`: copy of the real terminal screenshot above, using the submission filename.
- `production_readiness.txt`: raw terminal output from `python scripts/production_readiness_check.py`.
- `production_readiness_evidence.png`: real terminal screenshot of the production readiness run.
- `production_readiness.png`: copy of the real terminal screenshot above, using the submission filename.
- `observability_check.txt`: raw terminal output from `python scripts/09_verify_observability.py`.

Rendered previews:

- `observability_check.png`

`observability_check.png` is generated from the raw `.txt` log for easier viewing. The raw `.txt`
files are still the source of truth for command output.

Kaggle evidence:

- `../kaggle/2a20260084-huynhnhuthuy.ipynb` is the Kaggle notebook saved with outputs.
  It shows vLLM serving `Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4`, public Cloudflare URLs,
  chat completion output, and embedding service health using
  `sentence-transformers:BAAI/bge-small-en-v1.5`.
