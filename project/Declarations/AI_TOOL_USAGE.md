# AI-tool and pre-trained-model disclosure

| AI tool / model | Purpose | Artifact affected | Verified By Student (Y/N) |
|---|---|---|---|
| ChatGPT / Codex (service model not independently recorded) | Implementation assistance, debugging, synthetic examples, evaluation automation and document drafting | Code, Input_Data, Evaluation_Results, Synopsis, Documentation, demo materials | Y — reviewed by student |
| Qwen/Qwen2.5-0.5B-Instruct-GGUF, Q4_K_M | Local grounded answer generation; not trained or fine-tuned by the student | Runtime answers and evaluation outputs | Y — reviewed by student |
| BAAI/bge-small-en-v1.5 | Local pretrained text embeddings through Sentence Transformers / PyTorch | FAISS retrieval index and retrieval evidence | Y — reviewed by student |
| Optional Ollama qwen2.5:1.5b + nomic-embed-text | Alternative local execution configuration, only if installed and separately evaluated | Optional runtime configuration; not evidence for tested GGUF mode | Y — configuration reviewed; optional runtime not tested |

Automated execution evidence is recorded separately from student review. Student review was confirmed on 07/10/2026. Student review confirmed on 07/10/2026. No claim of unaided authorship, model training, real vehicle testing, formal standards compliance or student-performed evaluation is made by this package.
