# Six-minute demonstration guide

The supplied video records automated interactions with the actual local Streamlit application. Captions disclose that it is automated and AI-assisted. It is automated system footage rather than footage of the student presenting. Student review of the submission was confirmed on 07/10/2026. Watch it fully, verify that it matches the submitted build, and optionally record your own voice or a fresh screen recording using the guide below.

## 0:00–0:30 — Introduction

“My project is the AUTOSAR HLD Intelligence Assistant, case study CS1. It addresses the difficulty of locating architecture information across design-document revisions. The intended users are architects, developers, integration engineers and reviewers. This is a synthetic teaching prototype, not an AUTOSAR compliance-certification tool. I used AI assistance to prepare the implementation and have disclosed it. I will explain the actual pipeline, evidence, results and limitations.”

## 0:30–1:00 — Knowledge base

Open Knowledge base. Expand current powertrain revision. “We use five original synthetic JSON documents containing 25 sections. They describe powertrain, body and thermal-controller examples, plus review guidance. Powertrain has revisions 1.0 and 2.0. The documents include components, signals, interfaces, dependencies and behaviour. No proprietary customer data or licensed AUTOSAR standards text is included. Evaluation labels are kept outside the indexed folder.”

## 1:00–1:30 — Model and pipeline

Show local execution mode and the configuration file if recording your own screen. “The local model is Qwen2.5-0.5B-Instruct in Q4_K_M GGUF format. BGE-small-en-v1.5 produces embeddings through Sentence Transformers and PyTorch. Normalized vectors are indexed in FAISS. Retrieval uses the selected project and revision. The top three sections are passed to Qwen in a controlled prompt. A JSON schema requires an answer, citations and an insufficient-evidence flag. We check citation IDs and show all outputs as pending human review. There is no model training or fine-tuning.”

## 1:30–2:00 — Current-revision question

Ask the current PedalPosition timeout. “The current synthetic revision states 50 milliseconds. The answer should cite the document, revision and section. I can expand the retrieved evidence and verify the value directly. The citation is useful for traceability, but a valid citation ID does not prove that every generated claim is correct.”

## 2:00–2:30 — Evidence inspection

Expand a retrieval panel. “Similarity is a ranking score, not a calibrated correctness probability. The index contains source sections, not the expected-answer labels. The separate offline baseline uses TF-IDF and exact evidence extraction; it is not a pretrained generative model and its scores are reported separately.”

## 2:30–3:00 — Architecture inventory

Open Architecture inventory. “A deterministic parser extracts explicit record lines into component, signal, interface and dependency inventories. Each row keeps its citation. We can export JSON for review. This parser is designed for the synthetic schema and is not a general extractor for arbitrary AUTOSAR diagrams or complex tables.”

## 3:00–3:30 — Revision comparison

Open TIMEOUT in Revision comparison. “Revision 1.0 has a 100-millisecond timeout, and revision 2.0 has 50 milliseconds. Comparison aligns stable section IDs and reports text changes with citations to both versions. It does not automatically modify the source document or approve the design change.”

## 3:30–4:00 — Historical question

Select revision 1.0 and ask its timeout. “Historical selection lets us deliberately retrieve older facts. The default current filter helps avoid accidental mixing of stale and current information.”

## 4:00–4:30 — Candidate findings

Switch to thermal and inspect candidate findings. “The test fixture deliberately contains a percent/rpm interface mismatch and a MissingSensor dependency. The rule engine flags them with source citations. These are seeded examples for verification, not discovered real-vehicle defects. A qualified engineer must review each finding.”

## 4:30–5:00 — Unsupported question and review

Return to powertrain; ask a weather question. Open Review queue. “Unsupported subjects and missing specification fields are refused by limited scope guards. The review workflow records a disposition and note in SQLite. Reviewer identity is self-reported. The automated demo reviewer is not my signature, faculty approval or a production approval.”

## 5:00–5:30 — Evaluation

Open Evaluation and actual results. “The fixed development set has 24 questions, including 20 answerable cases and four unsupported or blocked cases. Read the final saved scores directly: retrieval hit at three, required-term checks, citation-ID validity, abstention and latency. All failed outputs are retained. The tests were run automatically by the assistant; I must separately verify them on my laptop. Required-term matching is a narrow proxy, not a semantic or expert quality score.”

## 5:30–6:00 — Limitations and contribution

“Limitations include synthetic data, a small model, relationship-extraction errors, no OCR or enterprise authentication, and no formal compliance validation. Docker is provided but was not executed in the preparation environment. My final contribution statement must describe what I actually reviewed, ran, changed and understood, along with the AI assistance. Future work would use qualified reviewer labels, a genuinely held-out dataset, stronger retrieval and answerability checks, and approved real documents. All generated engineering output remains subject to human review.”

Do not read a first-person claim that you have not actually completed. Replace it with your truthful status. Complete student verification and obtain faculty signatures before agreeing to the form declarations.
