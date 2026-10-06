# Windows setup and reproducibility

Open PowerShell in the cloned `Tata_Tech_CS` repository. Python 3.11 or 3.12 is recommended. Model downloads need internet initially. The app processes the corpus locally and does not call a cloud LLM.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
cd project
python -m pip install -r Code/requirements_baseline.txt
python Code/check_system.py
python Code/evaluate.py --mode baseline
python -m streamlit run Code/app.py --browser.gatherUsageStats=false
```

Open the displayed localhost URL. The baseline is an extractive retrieval demonstrator, not a pretrained LLM. Do not describe a baseline demo as LLM inference.

## Local Qwen + BGE model mode

In the same activated environment:

```powershell
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install sentence-transformers
python -m pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
python Code/download_model.py
python Code/evaluate.py --mode local
$env:HLD_MODE="local"
python -m streamlit run Code/app.py --browser.gatherUsageStats=false
```

The Qwen GGUF file is approximately 491 MB. BGE is downloaded by Sentence Transformers at first initialization. Allow several GB of free disk space for Python packages and caches. If memory is limited, close other apps. The GGUF SHA-256 is checked against Hugging Face LFS metadata. BGE model identity and any retrieved revision/hash are recorded separately. Model weights are not committed to Git.

If a compatible llama-cpp wheel is unavailable, compilation requires a C++ toolchain; use the optional Ollama mode rather than assuming installation succeeded. Ollama is an alternative configuration and requires a separate evaluation. It is not interchangeable evidence for the tested local GGUF mode.

```powershell
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
$env:HLD_MODE="ollama"
python -m streamlit run Code/app.py --browser.gatherUsageStats=false
python Code/evaluate.py --mode ollama
```

## API (optional)

```powershell
python -m uvicorn api:app --app-dir Code --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`. API execution mode comes from HLD_MODE. Run app and API in separate terminals. Leave services bound to loopback; there is no enterprise login or RBAC.

## Docker baseline (provided, execution must be checked locally)

From the submission folder:

```powershell
docker build -f Code/Dockerfile -t pccoe-cs1-hld .
docker run --rm -p 127.0.0.1:8501:8501 pccoe-cs1-hld
```

Docker is optional. Do not claim a Docker build or deployment was tested unless you run it. The image includes baseline dependencies only.

## Before recording

Run the checks and evaluation on your laptop, save their real outputs, select local mode, and ask a current-revision question. Check citations manually. Replacing synthetic data changes the evaluation assumptions; use a new test set and do not reuse the old scores as new-data results.

## Optional supplied model-cache archives

Extract `Institution_CS1_Qwen_Model.zip` and `Institution_CS1_BGE_Embeddings.zip` into the repository root, so `model_cache/` sits alongside the submission folder. They restore the verified pretrained weights without downloading them again. Install Python packages separately. Run the verified downloader to check the Qwen hash if internet is available, or compare with model_manifest.json offline. BGE file hashes are listed in embedding_manifest.json. Use `$env:HF_HUB_OFFLINE="1"` once the embedding cache is restored and the packages are installed.

For completely offline file-integrity verification after restoring the model archives, run `python Code/verify_assets.py`. It compares every input and active model file with the saved SHA-256 manifests.

Large uploaded pages may exceed the configured 2,048-token model context; the app reports a generation validation failure instead of silently changing models. Split large synthetic sources into smaller sections/pages before the demo. General OCR, diagram semantics and formal AUTOSAR validation are outside this prototype.

If PowerShell blocks activation, you can skip activation and use the virtual-environment executable directly: from the repository root, `.\.venv\Scripts\python.exe -m pip install -r project/Code/requirements_baseline.txt`. Use that same executable for the app and evaluation commands. No execution-policy change is required.
