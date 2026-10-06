# TechPulse FY-26 — CS1 AUTOSAR HLD Intelligence Assistant

Reviewed by student Student on 07/10/2026. Student identifiers are provided privately with the academic submission.

The project retrieves evidence from synthetic automotive HLD sections, answers with section citations, compares revisions and records human review. It includes an extractive baseline and a local pretrained Qwen/BGE RAG mode.

## Run

```bash
cd project/Code
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

See `Documentation/SETUP_WINDOWS.md` for local pretrained-model setup. Model weights are distributed separately; the model and embedding manifests identify exact snapshots and hashes. Initial installation/downloads need internet. Baseline and configured local inference operate offline afterward. Optional Ollama configuration was reviewed but not runtime tested.

## Evidence and disclosure

The automated development-set checks recorded 18/24 baseline and 19/24 local-model checks; all 18 system checks passed. These small synthetic-set results are not a production-quality guarantee. Citation-ID validity does not establish semantic entailment. Failures and sample outputs are retained in `Evaluation_Results/`.

AI assistance supported implementation, debugging, synthetic examples, evaluation automation and document drafting. Pretrained Qwen and BGE models are declared. Student review is confirmed; automated execution evidence is distinguished from independent manual testing. See `Declarations/AI_TOOL_USAGE.md` and `CONTRIBUTIONS_AND_DEPENDENCIES.md`.

Signed academic PDFs, personal contact details and the demonstration video are supplied in the private submission package. Faculty approval must be obtained separately. No signature or private contact information is published in this repository.
