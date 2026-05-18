"""
Day28 Kaggle GPU services.

Use the notebook version for Kaggle:

    kaggle/day28_gpu_services.ipynb

The notebook is safer than a raw script because it:
- installs dependencies into /kaggle/working/day28_site with pip --target
- avoids relying on a Kaggle venv, which may be missing pip on Python 3.12
- avoids modifying Kaggle's base Python environment
- starts vLLM when available
- avoids FlashInfer on Kaggle T4 because its JIT can fail to link libcuda.so
- falls back to an OpenAI-compatible server if vLLM cannot install or load
- starts an embedding service with BAAI/bge-small-en-v1.5 when available
  and deterministic 384-dim fallback otherwise
- exposes both services through cloudflared

Upload day28_gpu_services.ipynb to Kaggle and run its cells in order.
"""
