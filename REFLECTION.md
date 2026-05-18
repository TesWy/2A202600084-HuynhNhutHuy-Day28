# Reflection - Day 28 Full Platform Integration Sprint

## Thông tin sinh viên

- Họ tên: Huynh Nhut Huy
- Mã học viên: 2A202600084
- Lab: Day 28 - Full Platform Integration Sprint
- Repository: `TesWy/2A202600084-HuynhNhutHuy-Day28`

## Tóm tắt triển khai

Trong lab này, em đã triển khai một AI infrastructure platform theo kiến trúc hybrid Local + Kaggle GPU. Phần local chạy các service nền tảng như Kafka, Prefect, Delta Lake, Redis/Feast-like feature store, Qdrant, API Gateway, Prometheus và Grafana. Phần Kaggle GPU chạy vLLM để serve model `Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4` và embedding service dùng `BAAI/bge-small-en-v1.5`.

Luồng end-to-end đã được kiểm tra gồm:

1. Ingest dữ liệu vào Kafka topic `data.raw`.
2. Prefect flow consume Kafka và ghi dữ liệu xuống Delta Lake.
3. Script load dữ liệu từ Delta Lake vào Redis feature store.
4. Embedding service trên Kaggle tạo vector embedding.
5. Qdrant lưu vector và payload document.
6. API Gateway nhận request chat, search context từ Qdrant và gọi vLLM qua Cloudflare tunnel.
7. Prometheus scrape metrics từ API Gateway.
8. Grafana hiển thị dashboard hệ thống.
9. LangSmith ghi nhận tracing/observability.
10. Smoke tests và production readiness check xác nhận hệ thống hoạt động.

## Evidence đã chuẩn bị

Các evidence chính nằm trong thư mục `screenshots/`:

- `prefect_ui.png`: Prefect UI với flow run đã chạy.
- `api_gateway.png`: API Gateway health endpoint.
- `grafana_dashboard.png`: Grafana dashboard.
- `prometheus_targets.png`: Prometheus targets.
- `qdrant_dashboard.png`: Qdrant dashboard.
- `smoke_test_evidence.png`: ảnh terminal thật khi chạy `pytest smoke-tests -v`.
- `smoke_tests_results.png`: bản copy dùng đúng tên file nộp bài.
- `production_readiness_evidence.png`: ảnh terminal thật khi chạy production readiness check.
- `production_readiness.png`: bản copy dùng đúng tên file nộp bài.
- `api_gateway_chat_response.json`: response thật từ API Gateway, trong đó `mode` là `vllm` và model là `Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4`.
- `observability_check.txt`: output xác nhận Prometheus metrics và LangSmith traces.

Evidence Kaggle nằm ở:

- `kaggle/2a20260084-huynhnhuthuy.ipynb`: notebook đã lưu output, thể hiện vLLM chạy model Qwen, Cloudflare public URLs, chat completion sample và embedding service health.

Kết quả kiểm tra:

- Smoke tests: 8/8 passed.
- Production readiness: 11/11, score 100%, status READY.
- Embedding mode: `sentence-transformers:BAAI/bge-small-en-v1.5`.
- Chat mode: `vllm`.

## Các phần nâng cao so với yêu cầu cơ bản

Một số phần được triển khai vượt mức yêu cầu tối thiểu:

- API Gateway có graceful fallback: nếu Kaggle/vLLM URL thiếu hoặc request tới vLLM lỗi, service không crash mà trả fallback response có mode rõ ràng.
- Kaggle notebook có fallback server OpenAI-compatible để lab vẫn test được nếu vLLM không load được.
- Notebook xử lý lỗi thực tế của Kaggle T4 với FlashInfer bằng cách ép vLLM dùng Triton attention backend và tắt FlashInfer sampler.
- Embedding service ưu tiên `BAAI/bge-small-en-v1.5`, nhưng có deterministic fallback nếu package/model lỗi.
- Docker Compose hỗ trợ cấu hình `API_PORT` và `REDIS_PORT` qua `.env`, tránh conflict với service local khác.
- Grafana dashboard được provision tự động bằng file config trong repo.
- Smoke tests được chỉnh phù hợp kiến trúc hybrid: khi gọi vLLM qua tunnel, latency threshold thực tế hơn so với local fallback.
- Production readiness check kiểm tra nhiều thành phần hơn yêu cầu tối thiểu: API, metrics, Grafana, Qdrant, Redis, Kafka.
- Có evidence manifest trong `screenshots/README.md` để phân biệt screenshot thật và raw log.
- LangSmith observability được verify bằng script riêng.

## Khó khăn và cách xử lý

Khó khăn chính nằm ở môi trường Kaggle. Một số hướng dẫn lab ban đầu không ổn với Kaggle Python 3.12 và package stack mới. Lỗi đầu tiên là venv thiếu `pip`, nên notebook được chuyển sang cài package bằng `pip --target=/kaggle/working/day28_site` thay vì tạo virtualenv. Lỗi tiếp theo là FlashInfer JIT không link được `libcuda.so` trên Kaggle T4, dù vLLM đã load model thành công. Cách xử lý là bỏ cài FlashInfer, xoá cache cũ, dùng `--attention-backend TRITON_ATTN`, `--enforce-eager`, và `VLLM_USE_FLASHINFER_SAMPLER=0`.

Sau khi xử lý, vLLM đã serve được model `Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4`, endpoint `/v1/models` trả đúng model, chat completion hoạt động, và embedding service trả vector 384 chiều từ `BAAI/bge-small-en-v1.5`.

## Kết luận

Lab đã hoàn thành end-to-end từ data ingestion, orchestration, vector store, feature store, model serving, API Gateway đến observability. Các evidence bắt buộc và bổ sung đã được lưu trong repository. Hệ thống đạt smoke tests 8/8 và production readiness 100%, đồng thời có fallback để giảm rủi ro khi Kaggle tunnel hoặc GPU service bị gián đoạn.
