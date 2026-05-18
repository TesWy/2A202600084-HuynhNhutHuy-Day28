# Kaggle GPU and Tunnel Setup

Use this with a Kaggle notebook that has GPU enabled. The local Day28 stack reads
the public URLs from `.env`.

## Local side

Copy `.env.example` to `.env` if `scripts/setup_local.ps1` has not already done it:

```powershell
Copy-Item .env.example .env
```

After the Kaggle cells print public URLs, paste them into:

```text
VLLM_NGROK_URL=https://...
EMBED_NGROK_URL=https://...
```

`VLLM_NGROK_URL` may be either an ngrok URL or a trycloudflare URL. The variable
name is kept because the starter code uses that name.

## Kaggle side

Upload `kaggle/day28_gpu_services.ipynb` to Kaggle and run the cells in order.
The notebook installs dependencies into `/kaggle/working/day28_site` with
`pip --target` and adds that folder to `PYTHONPATH` only for the Day28 service
processes. It also removes the older `/kaggle/working/day28_venv` folder if a
previous notebook run created a broken venv, and resets
`/kaggle/working/day28_site` on each install run to avoid stale partial
packages.

The notebook uses `Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4` by default to match the
Day28 lab guide. It installs vLLM into the target package directory and uses the
CUDA 12.4 PyTorch wheel index as an extra package source. If Kaggle cannot
install vLLM or load the 7B model, the notebook starts an OpenAI-compatible
fallback server so the local integration can still be tested.

The notebook supports:

- `cloudflared`: no account required, prints `trycloudflare.com` URLs.
- vLLM mode when vLLM installs and the model loads successfully.
- Kaggle T4-safe vLLM startup: the notebook skips FlashInfer, sets
  `VLLM_ATTENTION_BACKEND=TRITON_ATTN`, and sets
  `VLLM_USE_FLASHINFER_SAMPLER=0` because FlashInfer JIT commonly fails on
  Kaggle with `cannot find -lcuda`.
- Embedding mode with `BAAI/bge-small-en-v1.5` when `sentence-transformers`
  loads successfully, with deterministic fallback otherwise.
- OpenAI-compatible fallback mode when vLLM is unavailable, so the local
  integration can still be tested end-to-end.

Recommended flow:

1. Run the install cell.
2. Start the chat API on port `8001`.
3. Start the embedding API on port `8002`.
4. Expose both ports with cloudflared.
5. Paste the printed `MODEL_ID`, `VLLM_NGROK_URL`, and `EMBED_NGROK_URL` into local `.env`.
6. Restart local Docker Compose if it was already running:

```powershell
docker compose down
docker compose up -d --build
```
