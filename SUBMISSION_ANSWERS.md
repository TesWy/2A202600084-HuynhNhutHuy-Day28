# Lab28 Submission Answers

## 1. Architecture Trade-offs

This platform separates local infrastructure from GPU serving. Kafka, Prefect, Redis, Qdrant, Prometheus, Grafana, and the API Gateway run locally because they need stable networking and are cheaper to operate without GPU. vLLM and embedding serving run on Kaggle because GPU is the expensive bottleneck. The trade-off is extra network complexity through a tunnel, but the design keeps GPU usage flexible while preserving local control over data flow, observability, and API routing.

Performance is handled by keeping vector search local and sending only the final prompt to vLLM. Reliability is handled through health checks, readiness checks, and an API Gateway fallback when vLLM is unavailable. Maintainability is handled through Docker Compose, environment variables, and separated services/scripts.

## 2. Hybrid Local + Kaggle Disconnect Handling

The API Gateway treats Kaggle vLLM as an external dependency. If the tunnel URL is missing or the vLLM request fails, the gateway returns a local fallback response instead of crashing. This is graceful degradation: the platform remains healthy and observable, while the response mode clearly indicates fallback behavior. In production, the same pattern could be extended with cached responses, retry policies, and circuit breakers.

## 3. Kafka Event-driven Decoupling

Kafka decouples data producers from downstream processing. The ingestion script only writes events to `data.raw`; it does not need to know whether Prefect, Delta Lake, Redis, or Qdrant are available at that exact moment. Consumers can process events independently, replay old events, and recover after failures without changing the producer contract. This makes the platform easier to evolve because new consumers can be added without modifying ingestion.

## 4. Observability Implementation

The API Gateway exposes Prometheus metrics through `/metrics` using `prometheus-fastapi-instrumentator`. Prometheus scrapes the API Gateway, and Grafana is provisioned with a Lab28 dashboard for request rate, p95 latency, and error ratio. The readiness script also verifies Prometheus, Grafana, API health, Qdrant, Redis, and Kafka topic availability. LangSmith tracing is prepared through `LANGCHAIN_API_KEY`, but it requires the user's LangSmith key to verify real traces.

## 5. Service Crash Handling

If Qdrant is unavailable, the API Gateway catches the vector-search failure and continues with an empty context. If Kaggle/vLLM is unavailable, the gateway returns a fallback response and reports the fallback mode. If Kafka fails, ingestion/readiness checks fail clearly while the API can still serve degraded requests. For a stronger production setup, this should be extended with Docker health checks, restart policies, retry queues, and alerts.
