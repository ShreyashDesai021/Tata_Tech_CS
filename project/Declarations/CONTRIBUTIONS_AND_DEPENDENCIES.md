# Individual contribution and dependency record

Student: Student, PRN STUDENT_PRN, Information Technology, Institution.

Status: Individual submission confirmed by the student. CS1 approval reported by the student; signed evidence must be attached. Division A and contact details have been provided in the private submission documents. Faculty name and signed faculty record remain to be supplied.

## Accurate contribution statement

The student selected CS1, confirmed the scope and reviewed the project implementation, synthetic data, measured outputs and documentation on 07/10/2026. AI assistance supported implementation, debugging, synthetic examples, evaluation automation and document drafting. The supplied student signature was applied at the student's instruction. Automated runs are documented as automated execution; independent laptop execution is not inferred. The student remains responsible for explaining the submitted implementation.

## Dependencies

Initial setup: internet needed for Python packages, public Hugging Face model files and optional Ollama model pulls. No paid cloud inference key is required. Synthetic corpus and questions are processed locally by the tested configuration. UI usage statistics and Hugging Face client telemetry are disabled in the final configuration. The initial ONNX embedding experiment was halted after unauthorized telemetry egress was detected; the submitted local path uses Sentence Transformers/PyTorch instead and does not import ONNX Runtime.

Optional Ollama: local service at 127.0.0.1:11434; its model tags and results must be recorded separately. Docker build requires package-download connectivity. Demo playback works offline. Model weights are excluded from Git and the primary submission ZIP; use the verified downloader or optional model cache archive.

External assets: provided case-study reference and college templates; Qwen model (Apache-2.0), BGE model (MIT), FAISS, llama-cpp-python, Sentence Transformers, PyTorch, FastAPI, Streamlit, scikit-learn and PyMuPDF. Respect each dependency's license if redistributing it. The reference PDF is marked internal/confidential and is not included in the public repository. Synthetic data are a teaching fixture, not an OEM specification or authorized standards text.
