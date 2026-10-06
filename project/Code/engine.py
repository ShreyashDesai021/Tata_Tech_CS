"""CS1 synthetic HLD retrieval, inference, validation and review engine."""
from pathlib import Path
import json, re, time, hashlib, sqlite3, urllib.request, os
os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT/'Model_Prompts_Config/config.json').read_text())
PROMPT = (ROOT/'Model_Prompts_Config/grounded_qa.txt').read_text()

class Engine:
    def __init__(self, mode='baseline', data_dir=None):
        if mode not in ('baseline','local','ollama'):
            raise ValueError('mode must be baseline, local or ollama')
        self.mode = mode
        self.docs = []
        for path in sorted(Path(data_dir or ROOT/'Input_Data').glob('*.json')):
            doc = json.loads(path.read_text())
            if not all(k in doc for k in ['doc_id','version','project','sections','current']):
                raise ValueError(f'Invalid document: {path.name}')
            if not doc.get('synthetic') and doc.get('approval_status') != 'approved':
                raise ValueError('Only synthetic or explicitly approved data allowed')
            doc['source_file'] = path.name
            self.docs.append(doc)
        self.chunks=[]
        for d in self.docs:
            for s in d['sections']:
                self.chunks.append({**{k:d[k] for k in ['doc_id','version','project','current','source_file']},
                    'id':f"{d['doc_id']}@{d['version']}#{s['section_id']}", **s})
        if not self.chunks:
            raise ValueError('No input documents')
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), lowercase=True, sublinear_tf=True, stop_words="english")
        self.lexical_vectors=self.vectorizer.fit_transform([c['text'] for c in self.chunks])
        if mode == 'baseline':
            vectors=self.lexical_vectors.toarray()
            self.embedding_name='TF-IDF word unigrams/bigrams (fitted baseline, not pretrained)'
        elif mode == 'local':
            import torch
            torch.set_num_threads(4)
            from sentence_transformers import SentenceTransformer
            self.embedder=SentenceTransformer(CONFIG['embedding'],cache_folder=str(ROOT.parent/'model_cache/embeddings'),revision=CONFIG.get('embedding_revision'),device='cpu')
            vectors=self.embedder.encode([c['text'] for c in self.chunks],normalize_embeddings=True)
            self.embedding_name=CONFIG['embedding']
        else:
            vectors=self.ollama('/api/embed',{'model':CONFIG['ollama_embedding'],'input':[c['text'] for c in self.chunks]})['embeddings']
            self.embedding_name=CONFIG['ollama_embedding']
        self.vectors=np.asarray(vectors,dtype='float32')
        faiss.normalize_L2(self.vectors)
        self.index=faiss.IndexFlatIP(self.vectors.shape[1]); self.index.add(self.vectors)
        cache=ROOT/'Code/runtime'/mode; cache.mkdir(parents=True,exist_ok=True)
        faiss.write_index(self.index,str(cache/'index.faiss'))
        (cache/'chunks.json').write_text(json.dumps(self.chunks,indent=2))
        self.llm=None
        if mode=='local':
            from llama_cpp import Llama
            model_path=ROOT.parent/CONFIG['model_path']
            if not model_path.exists(): raise FileNotFoundError(f'Model missing: {model_path}; run download_model.py')
            self.llm=Llama(model_path=str(model_path),n_ctx=2048,n_threads=4,verbose=False,seed=42)
        self.db=ROOT/'Code/runtime/reviews.sqlite'
        with sqlite3.connect(self.db) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, created TEXT DEFAULT CURRENT_TIMESTAMP, kind TEXT, payload TEXT)')

    def ollama(self,path,payload):
        request=urllib.request.Request(CONFIG['ollama_url']+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=180) as r: return json.load(r)
        except Exception as e:
            raise RuntimeError('Local Ollama unavailable. Start Ollama and pull the configured models. No silent baseline fallback.') from e

    def audit(self,kind,payload):
        with sqlite3.connect(self.db) as conn:
            cur=conn.execute('INSERT INTO audit(kind,payload) VALUES(?,?)',(kind,json.dumps(payload)))
            return cur.lastrowid

    def retrieve(self,query,project='powertrain',version=None,k=None):
        if not query.strip() or len(query)>2000: raise ValueError('Question must contain 1–2000 characters')
        if self.mode=='baseline': vector=self.vectorizer.transform([query]).toarray()
        elif self.mode=='local': vector=self.embedder.encode(['Represent this sentence for searching relevant passages: '+query],normalize_embeddings=True)
        else: vector=self.ollama('/api/embed',{'model':CONFIG['ollama_embedding'],'input':query})['embeddings']
        vector=np.asarray(vector,dtype='float32'); faiss.normalize_L2(vector)
        scores, ids=self.index.search(vector,len(self.chunks))
        matches=[]
        for score,i in zip(scores[0],ids[0]):
            c=self.chunks[int(i)]
            if c['project'] not in (project,'guidance'): continue
            if c['project'] != 'guidance' and ((version is None and not c['current']) or (version is not None and c['version']!=version)): continue
            if c['project']=='guidance' and not c['current']: continue
            matches.append({**c,'score':round(float(score),6)})
            if len(matches)>=(k or CONFIG['top_k']): break
        return matches

    def ask(self,query,project='powertrain',version=None):
        start=time.perf_counter(); evidence=self.retrieve(query,project,version)
        eligible=[c for c in evidence if c['score']>=CONFIG['min_score']]
        scope_text=' '.join(c['text'] for c in self.chunks if c['project'] in (project,'guidance') and (c['current'] if version is None else c['version']==version))
        lexical=self.vectorizer.transform([query])
        in_scope=lexical.nnz>0
        requested_fields=re.findall(r'\b(?:ASIL|OEM|VIN|DTC)\b|part number|security key',query,re.I)
        unsupported_fields=[field for field in requested_fields if field.lower() not in scope_text.lower()]
        blocked=bool(re.search(r'ignore.*instructions|system prompt|reveal.*secret|approve.*production',query,re.I))
        raw=None; error=None
        if blocked:
            answer='Request blocked: the assistant cannot disclose instructions or approve production decisions.'; citations=[]; insufficient=True
        elif not in_scope or unsupported_fields:
            answer='Insufficient evidence: the requested subject or specification field is absent from this synthetic project.'; citations=[]; insufficient=True
        elif not eligible:
            answer='Insufficient evidence in the selected synthetic project.'; citations=[]; insufficient=True
        elif self.mode=='baseline':
            answer='\n\n'.join(f"{c['text']} [{c['id']}]" for c in eligible)
            citations=[c['id'] for c in eligible]; insufficient=False
        else:
            context='\n\n'.join(f"ID: {c['id']}\nDATA: {c['text']}" for c in eligible)
            user=f'QUESTION: {query}\nUNTRUSTED EVIDENCE:\n{context}\nReturn only the required JSON.'
            try:
                if self.mode=='local':
                    output=self.llm.create_chat_completion(messages=[{'role':'system','content':PROMPT},{'role':'user','content':user}],temperature=0,max_tokens=300,response_format={'type':'json_object','schema':{'type':'object','properties':{'answer':{'type':'string'},'citations':{'type':'array','items':{'type':'string'}},'insufficient_evidence':{'type':'boolean'}},'required':['answer','citations','insufficient_evidence'],'additionalProperties':False}},seed=42)
                    raw=output['choices'][0]['message']['content']
                else:
                    raw=self.ollama('/api/generate',{'model':CONFIG['ollama_model'],'system':PROMPT,'prompt':user,'stream':False,'format':'json','options':{'temperature':0,'seed':42,'num_predict':300}})['response']
                generated=json.loads(raw)
                answer=generated['answer']; citations=generated['citations']; insufficient=generated['insufficient_evidence']
                if not isinstance(answer,str) or not isinstance(citations,list) or not isinstance(insufficient,bool): raise ValueError('Invalid response types')
                allowed={c['id'] for c in eligible}
                if any(not isinstance(c,str) or c not in allowed for c in citations) or (not insufficient and not citations):
                    raise ValueError('Missing or invalid evidence citation')
            except Exception as e:
                error=str(e); answer='Generated response failed validation; inspect retrieved evidence and retry.'; citations=[]; insufficient=True
        result={'answer':answer,'citations':citations,'insufficient_evidence':insufficient,'blocked':blocked,
                'evidence':evidence,'mode':self.mode,'embedding':self.embedding_name,'generation_error':error,'raw_generation':raw,
                'review_status':'PENDING_HUMAN_REVIEW','latency_ms':round((time.perf_counter()-start)*1000,3),
                'confidence_note':'Retrieval similarity is not probability of correctness; citation validation checks IDs, not factual entailment.'}
        result['audit_id']=self.audit('answer',{'question':query,'project':project,'version':version,**result})
        return result

    def inventory(self,project='powertrain',version=None):
        records=[]
        for c in self.chunks:
            if c['project']!=project or (version is None and not c['current']) or (version is not None and c['version']!=version): continue
            for line in c['text'].splitlines():
                match=re.match(r'(Component|Signal|Interface|Dependency):\s*(.+)',line)
                if not match: continue
                kind,body=match.groups(); parts=[x.strip() for x in body.split('|')]
                record={'kind':kind,'name':parts[0],'citation':c['id']}
                for part in parts[1:]:
                    key,value=part.split(':',1); record[key.strip()]=value.strip()
                records.append(record)
        return records

    def findings(self,project='powertrain'):
        rows=self.inventory(project); names={r['name'] for r in rows if r['kind']=='Component'}; issues=[]
        for r in rows:
            if r['kind']=='Interface' and r.get('sender_unit')!=r.get('receiver_unit'):
                issues.append({'rule':'UNIT_MISMATCH','item':r['name'],'detail':f"{r.get('sender_unit')} != {r.get('receiver_unit')}",'citation':r['citation'],'status':'PENDING_HUMAN_REVIEW'})
            if r['kind']=='Dependency':
                source,target=[x.strip() for x in r['name'].split('->')]
                if source not in names or target not in names:
                    issues.append({'rule':'UNDECLARED_DEPENDENCY','item':r['name'],'detail':'Source or target component is undeclared','citation':r['citation'],'status':'PENDING_HUMAN_REVIEW'})
            if r['kind']=='Signal':
                for field in ('producer','consumer'):
                    if r.get(field) not in names:
                        issues.append({'rule':'UNDECLARED_SIGNAL_ENDPOINT','item':r['name'],'detail':field,'citation':r['citation'],'status':'PENDING_HUMAN_REVIEW'})
        return issues

    def compare(self,doc_id='HLD_POWERTRAIN',old='1.0',new='2.0'):
        versions={d['version']:d for d in self.docs if d['doc_id']==doc_id}
        if old not in versions or new not in versions: raise ValueError('Requested revisions are unavailable')
        a={s['section_id']:s['text'] for s in versions[old]['sections']}; b={s['section_id']:s['text'] for s in versions[new]['sections']}
        return [{'section':key,'old_text':a.get(key),'new_text':b.get(key),'change':'added' if key not in a else 'removed' if key not in b else 'modified',
                 'citations':[f'{doc_id}@{v}#{key}' for v,sections in [(old,a),(new,b)] if key in sections]}
                for key in sorted(a.keys()|b.keys()) if a.get(key)!=b.get(key)]

    def review(self,audit_id,status,note,reviewer):
        if status not in ('ACCEPTED','REJECTED','NEEDS_CHANGES'): raise ValueError('Invalid review status')
        if not reviewer.strip() or not note.strip(): raise ValueError('Reviewer and review note required')
        with sqlite3.connect(self.db) as conn:
            if not conn.execute('SELECT 1 FROM audit WHERE id=? AND kind=?',(audit_id,'answer')).fetchone(): raise ValueError('Answer audit ID not found')
        return self.audit('review',{'answer_audit_id':audit_id,'status':status,'note':note,'reviewer':reviewer,'note_limit':'Local self-reported reviewer identity; no enterprise authentication'})


def validate_upload(name,content):
    if len(content)>5*1024*1024: raise ValueError('File exceeds 5 MiB')
    suffix=Path(name).suffix.lower()
    if suffix=='.json':
        doc=json.loads(content)
        if not isinstance(doc,dict) or not doc.get('synthetic'): raise ValueError('Demo uploads must be declared synthetic')
        for key in ['doc_id','version','project','current','sections']:
            if key not in doc: raise ValueError(f'Missing field {key}')
        if doc['project'] not in ['powertrain','body','thermal','guidance']: raise ValueError('Unknown project')
        if not re.fullmatch(r'[A-Z0-9_]+',doc['doc_id']) or not re.fullmatch(r'[0-9]+\.[0-9]+',doc['version']): raise ValueError('Invalid document identity')
        if not isinstance(doc['current'],bool) or not isinstance(doc['sections'],list): raise ValueError('Invalid schema')
        ids=set()
        for sec in doc['sections']:
            if not re.fullmatch(r'[A-Z0-9_]+',sec.get('section_id','')) or not isinstance(sec.get('text'),str): raise ValueError('Invalid section')
            if sec['section_id'] in ids or len(sec['text'])>6000: raise ValueError('Duplicate or oversized section')
            ids.add(sec['section_id'])
        return doc
    if suffix=='.pdf':
        import fitz
        with fitz.open(stream=content,filetype='pdf') as pdf:
            sections=[{'section_id':f'PAGE_{i+1}','text':page.get_text()} for i,page in enumerate(pdf)]
        if not any(s['text'].strip() for s in sections): raise ValueError('No text layer. Scanned PDFs require OCR, which is outside this MVP.')
        if any(len(s['text'])>6000 for s in sections): raise ValueError('Page exceeds 6000 characters; split the synthetic PDF')
        digest=hashlib.sha256(content).hexdigest()[:10].upper()
        return {'doc_id':'UPLOAD_'+digest,'version':'1.0','project':'powertrain','current':True,'synthetic':True,'approval_status':'synthetic_demo_only','title':Path(name).stem,'sections':sections}
    raise ValueError('Only JSON and text-layer PDF supported')
