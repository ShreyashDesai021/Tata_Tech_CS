"""Fixed test-set checks. No LLM-as-judge or fabricated ground truth."""
import argparse,json,time,platform,statistics,importlib.metadata,csv
from pathlib import Path
from engine import Engine,ROOT

def run(mode):
 start=time.perf_counter();engine=Engine(mode);load_ms=round((time.perf_counter()-start)*1000,2)
 tests=json.loads((ROOT/'Evaluation_Results/test_questions.json').read_text());results=[]
 for test in tests:
  response=engine.ask(test['question'],test['project'],test.get('version'))
  if test['expected_behavior']=='abstain':
   hit=None;answer_ok=response['insufficient_evidence']
  else:
   hit=test['expected_citation'] in {c['id'] for c in response['evidence']}
   answer_ok=not response['insufficient_evidence'] and all(k.lower() in response['answer'].lower() for k in test['required_terms'])
  ids={c['id'] for c in response['evidence']};valid=all(c in ids for c in response['citations'])
  cited=bool(response['citations']) if not response['insufficient_evidence'] else None
  passed=bool(answer_ok and valid and (hit is not False))
  results.append({'test':test,'retrieval_hit_at_3':hit,'required_terms_or_abstention_pass':answer_ok,'citation_id_valid':valid,'pass':passed,'response':response})
  print(f"{test['id']} {'PASS' if passed else 'FAIL'} {response['latency_ms']} ms",flush=True)
 positive=[r for r in results if r['retrieval_hit_at_3'] is not None];negative=[r for r in results if r['test']['expected_behavior']=='abstain'];answered=[r for r in results if not r['response']['insufficient_evidence']]
 metrics={'mode':mode,'test_count':len(results),'pass_count':sum(r['pass'] for r in results),'overall_pass_rate':sum(r['pass'] for r in results)/len(results),
 'retrieval_hit_at_3':sum(r['retrieval_hit_at_3'] for r in positive)/len(positive),'required_terms_accuracy':sum(r['required_terms_or_abstention_pass'] for r in positive)/len(positive),
 'abstention_accuracy':sum(r['required_terms_or_abstention_pass'] for r in negative)/len(negative),
 'citation_id_validity_on_answered':sum(r['citation_id_valid'] for r in answered)/len(answered) if answered else None,
 'citation_presence_on_answered':sum(bool(r['response']['citations']) for r in answered)/len(answered) if answered else None,
 'warm_query_latency_mean_ms':statistics.mean(r['response']['latency_ms'] for r in results),'warm_query_latency_p95_ms':float(__import__('numpy').percentile([r['response']['latency_ms'] for r in results],95)),
 'engine_initialization_ms':load_ms,'limitations':'Citation ID validity is not entailment. Required-term matching is a narrow proxy. Same synthetic design corpus; not independent automotive validation. No reviewer confirmation or productivity benchmark.',
 'platform':platform.platform(),'python':platform.python_version(),'packages':{n:importlib.metadata.version(n) for n in ['numpy','scikit-learn','faiss-cpu','streamlit','fastapi','sentence-transformers','llama-cpp-python']}}
 out=ROOT/'Evaluation_Results';(out/f'results_{mode}.json').write_text(json.dumps(results,indent=2));(out/f'metrics_{mode}.json').write_text(json.dumps(metrics,indent=2))
 with (out/f'results_{mode}.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['id','question','expected_behavior','pass','retrieval_hit_at_3','answer_check','citation_id_valid','latency_ms','answer'])
  for r in results:w.writerow([r['test']['id'],r['test']['question'],r['test']['expected_behavior'],r['pass'],r['retrieval_hit_at_3'],r['required_terms_or_abstention_pass'],r['citation_id_valid'],r['response']['latency_ms'],r['response']['answer']])
 print(json.dumps(metrics,indent=2));return metrics
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['baseline','local','ollama'],default='baseline');run(parser.parse_args().mode)
