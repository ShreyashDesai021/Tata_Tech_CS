"""One-time public model download; no corpus or questions are transmitted."""
from pathlib import Path
import urllib.request,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
repo='Qwen/Qwen2.5-0.5B-Instruct-GGUF'
filename='qwen2.5-0.5b-instruct-q4_k_m.gguf'
configuration=json.loads((Path(__file__).resolve().parents[1]/'Model_Prompts_Config/config.json').read_text())
pinned=configuration.get('qwen_revision')
api='https://huggingface.co/api/models/'+repo+('/revision/'+pinned if pinned else '')+'?blobs=true'
metadata=json.load(urllib.request.urlopen(api,timeout=60))
revision=metadata['sha']; sibling=next(s for s in metadata['siblings'] if s['rfilename']==filename)
expected=sibling.get('lfs',{}).get('sha256')
destination=ROOT/'model_cache'/filename;destination.parent.mkdir(parents=True,exist_ok=True)
if not destination.exists():
 temporary=destination.with_suffix('.partial')
 urllib.request.urlretrieve(f'https://huggingface.co/{repo}/resolve/{revision}/{filename}',temporary)
 temporary.replace(destination)
hash=hashlib.file_digest(destination.open('rb'),'sha256').hexdigest()
if expected and hash!=expected:
 raise RuntimeError('Downloaded model SHA-256 differs from published LFS object; remove it and retry')
manifest={'repo':repo,'revision':revision,'filename':filename,'sha256':hash,'expected_lfs_sha256':expected,'size_bytes':destination.stat().st_size,'download_only_internet_dependency':True}
output=Path(__file__).resolve().parents[1]/'Model_Prompts_Config/model_manifest.json';output.write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
