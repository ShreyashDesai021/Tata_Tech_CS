# Implementation explanation and viva preparation

**Problem:** HLD architecture knowledge is spread across revisions and text. The assistant retrieves cited evidence and extracts simple component/signal/interface/dependency records for review.

**Why RAG instead of training?** The project uses pretrained models and current project documents as context. No fine-tuning or foundation-model training was performed. Changing documents rebuilds the retrieval index rather than retraining Qwen.

**What is the actual pipeline?** Validate approved/synthetic input → chunk by section (PDF page for uploads) → embed with BGE in local mode → normalize vectors → FAISS IndexFlatIP retrieval → project/version filtering → prompt Qwen with top three evidence records → schema-constrained JSON → citation-ID validation → display pending human review → SQLite audit.

**What is the baseline?** TF-IDF unigrams and bigrams stored in FAISS, followed by exact source extraction. It does not use a pretrained embedding model or a generative LLM. It is evaluated separately.

**What is IndexFlatIP?** An exact inner-product search index. Since vectors are L2-normalized, the inner product equals cosine similarity. For this small corpus exact search is simple; approximate indexing would add unnecessary complexity.

**Why filter revisions?** The old powertrain document says 100 ms and 300 Nm, while the current synthetic revision says 50 ms and 250 Nm. Default retrieval excludes old versions; historical questions require explicit selection.

**How are components extracted?** Deterministic parsing of explicit synthetic record lines. This is not a general AUTOSAR ontology parser or validated extraction from arbitrary HLD diagrams. JSON export preserves the section citation.

**What does comparison do?** It aligns two versions by document ID and section ID, then reports added, removed and changed text. It does not infer formal semantic compatibility.

**How are findings generated?** Rule checks compare declared component names, dependency endpoints and sender/receiver units. Two thermal anomalies are deliberately seeded: percent versus rpm, and MissingSensor. These are test fixtures, not discovered field defects.

**What does citation accuracy mean here?** The script checks that cited IDs exist among retrieved evidence. It does not prove the answer follows from the evidence. A real reviewer must inspect the text.

**What are the evaluation limitations?** Twenty answerable and four unsupported/blocked questions on a small synthetic corpus. Required-term matching is a narrow automated check and may fail a correct paraphrase or pass an incomplete answer. No independent expert validation, real OEM dataset, productivity baseline or safety certification exists.

**Are confidence scores calibrated?** No. Cosine similarity indicates retrieval closeness, not correctness probability. The UI states this.

**What are the security limits?** Loopback-only single-user demo, file-type/size/schema checks, safe generated upload filenames and separated system instructions. Project filtering is not enterprise RBAC. Prompt-injection defenses are limited and cannot guarantee immunity. Review identity is self-reported; no digital signature or immutable enterprise audit exists.

**Why human review?** An assistant can omit or invent technical facts. No result automatically approves a design, modifies original HLDs or authorizes a production release.

**What is the internet dependency?** Initial package/model download. Tested inference uses local weights and synthetic data. Optional Ollama is a local service and needs a separate model download/evaluation.

**What did AI help with?** ChatGPT/Codex generated code, synthetic examples, evaluation scripts and draft documents. Explain your actual subsequent review, execution and modifications honestly. Do not state that you independently wrote or validated all code if you did not.

**What is future work?** Better answerability calibration, hybrid retrieval/reranking, broader ground truth, expert-labelled entailment metrics, authorized real HLDs, OCR/table/diagram extraction, controlled enterprise identity, and real deployment checks.
