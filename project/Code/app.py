import os,json
from pathlib import Path
import streamlit as st
from engine import Engine,ROOT,validate_upload
st.set_page_config(page_title='AUTOSAR HLD Intelligence',page_icon='⚙',layout='wide')
st.markdown('''<style>.stApp{background:#f4f7fb}h1,h2,h3{color:#16345c}.block-container{padding-top:2rem}.stMetric{background:white;padding:16px;border-radius:12px;border:1px solid #dce5ef}</style>''',unsafe_allow_html=True)
st.caption('TECHPULSE FY-26  /  Institution  /  CASE STUDY 01')
st.title('AUTOSAR HLD Intelligence Assistant')
st.write('Explore architecture evidence, compare revisions and review candidate inconsistencies.')
st.info('Synthetic teaching data • Engineering review required • No compliance certification')
with st.sidebar:
 st.header('Workspace')
 mode=st.selectbox('Execution mode',['baseline','local','ollama'],index=['baseline','local','ollama'].index(os.getenv('HLD_MODE','baseline')))
 st.caption('baseline = extractive TF-IDF; local = Qwen GGUF + BGE; ollama = Qwen + Nomic. Modes never silently substitute each other.')
 project=st.selectbox('Project',['powertrain','body','thermal'])
 version=st.selectbox('Revision',['Current','1.0','2.0'] if project=='powertrain' else ['Current','1.0'])
 st.caption('Local single-user demonstration. Project filtering is implemented; enterprise RBAC is not.')
@st.cache_resource
def load_engine(mode,fingerprint): return Engine(mode)
fingerprint=tuple((p.name,p.stat().st_mtime_ns) for p in (ROOT/'Input_Data').glob('*.json'))
try: engine=load_engine(mode,fingerprint)
except Exception as e:
 st.error(str(e));st.stop()
rev=None if version=='Current' else version
cols=st.columns(4)
for col,label,value in zip(cols,['Documents','Knowledge sections','Components','Candidate findings'],[len(engine.docs),len(engine.chunks),sum(x['kind']=='Component' for x in engine.inventory(project,rev)),len(engine.findings(project))]): col.metric(label,value)
tabs=st.tabs(['Cited Q&A','Architecture inventory','Revision comparison','Review queue','Knowledge base','Evaluation'])
with tabs[0]:
 st.subheader('Ask the selected HLD')
 question=st.text_input('Engineering question',value='What is the PedalPosition timeout in the current revision?')
 if st.button('Retrieve and answer',type='primary'):
  try:
   with st.spinner('Retrieving project evidence…'):
    st.session_state['result']=engine.ask(question,project,rev)
    st.session_state['result_scope']=(mode,project,rev)
  except Exception as e: st.error(str(e))
 result=st.session_state.get('result') if st.session_state.get('result_scope')==(mode,project,rev) else None
 if result:
  st.caption(f"Mode: {result['mode']} | {result['latency_ms']:.1f} ms | {result['review_status']}")
  st.write(result['answer'])
  st.caption('Cited sources: '+(' | '.join(result['citations']) or '(none - abstained or blocked)'))
  st.caption(result['confidence_note'])
  if result['generation_error']: st.warning(result['generation_error'])
  for e in result['evidence']:
   with st.expander(f"{e['id']} · similarity {e['score']:.3f}"):
    st.text(e['text']);st.caption(e['source_file'])
  st.download_button('Export answer + evidence JSON',json.dumps(result,indent=2),'hld_answer_evidence.json','application/json')
with tabs[1]:
 rows=engine.inventory(project,rev)
 st.subheader('Structured architecture entities')
 st.dataframe(rows,width='stretch')
 st.download_button('Export entity inventory',json.dumps(rows,indent=2),'hld_architecture_inventory.json','application/json')
 st.subheader('Candidate inconsistencies')
 st.dataframe(engine.findings(project),width='stretch')
with tabs[2]:
 st.subheader('Powertrain HLD: revision 1.0 → 2.0')
 changes=engine.compare()
 for change in changes:
  with st.expander(change['section']+' · '+change['change']):
   a,b=st.columns(2);a.write('Revision 1.0');a.text(change['old_text'] or '(absent)');b.write('Revision 2.0');b.text(change['new_text'] or '(absent)');st.caption(' | '.join(change['citations']))
 st.download_button('Export revision comparison',json.dumps(changes,indent=2),'hld_revision_comparison.json','application/json')
with tabs[3]:
 st.subheader('Record human review')
 st.caption('Disposition is a local audit record, not a design approval. Review the cited evidence before accepting.')
 with st.form('review'):
  aid=st.number_input('Answer audit ID',min_value=1,value=int(result['audit_id']) if result else 1)
  reviewer=st.text_input('Reviewer name');status=st.selectbox('Disposition',['NEEDS_CHANGES','ACCEPTED','REJECTED']);note=st.text_area('Evidence-based review note')
  submitted=st.form_submit_button('Save review')
  if submitted:
   try: st.success(f'Review audit ID: {engine.review(aid,status,note,reviewer)}')
   except Exception as e: st.error(str(e))
with tabs[4]:
 st.subheader('Synthetic input documents')
 for d in engine.docs:
  with st.expander(f"{d['title']} · {d['version']} · {d['project']}"): st.json(d)
 st.subheader('Controlled synthetic upload')
 approved=st.checkbox('I confirm this upload is synthetic, contains no proprietary data and may be used in this demo.')
 upload=st.file_uploader('JSON HLD or PDF with a text layer',type=['json','pdf'])
 if st.button('Validate and ingest'):
  try:
   if not approved or not upload: raise ValueError('Select a file and confirm synthetic-data status')
   doc=validate_upload(upload.name,upload.getvalue())
   destination=ROOT/'Input_Data'/f"{doc['doc_id']}_v{doc['version']}.json"
   if destination.exists(): raise ValueError('Document revision exists; supply a new revision instead of overwriting')
   if doc['current'] and any(d['doc_id']==doc['doc_id'] and d['current'] for d in engine.docs): raise ValueError('A current revision already exists; mark upload historical or review current-version metadata first')
   destination.write_text(json.dumps(doc,indent=2));engine.audit('ingestion',{'file':destination.name});st.success('Saved. Reloading index.');st.rerun()
  except Exception as e: st.error(str(e))
with tabs[5]:
 st.subheader('Measured evaluation evidence')
 for path in sorted((ROOT/'Evaluation_Results').glob('metrics_*.json')):
  st.write(path.name);st.json(json.loads(path.read_text()))
 st.code('python Code/evaluate.py --mode baseline\npython Code/evaluate.py --mode local')
 st.caption('Metric scores are corpus-specific checks, not proof of standards compliance or real-world accuracy.')
