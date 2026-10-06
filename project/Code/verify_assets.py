"""Offline verification against saved input and pretrained-model manifests."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def verify(path,expected):
 if not path.is_file(): raise FileNotFoundError(path)
 actual=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
 if actual!=expected: raise RuntimeError(f'SHA-256 mismatch: {path.name}')
 print('VERIFIED',path.name)
inputs=json.loads((ROOT/'Model_Prompts_Config/input_manifest.json').read_text())
for entry in inputs['documents']:verify(ROOT/'Input_Data'/entry['file'],entry['sha256'])
model=json.loads((ROOT/'Model_Prompts_Config/model_manifest.json').read_text())
verify(ROOT.parent/'model_cache'/model['filename'],model['sha256'])
embedding=json.loads((ROOT/'Model_Prompts_Config/embedding_manifest.json').read_text())
snapshot=ROOT.parent/'model_cache/embeddings/models--BAAI--bge-small-en-v1.5/snapshots'/embedding['revision']
for entry in embedding['files']:verify(snapshot/entry['name'],entry['sha256'])
print('All saved input and model hashes match. This verifies file identity, not model accuracy.')
