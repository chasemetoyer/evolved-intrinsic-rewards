"""Read-only interruption audit: no call get, cancellation, submission, or volume writes."""
import json,hashlib,collections,concurrent.futures,datetime
from pathlib import Path
import modal
BASE=Path('/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform')
OUT=Path('/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/stage2-interruption')
v=modal.Volume.from_name('evolved-intrinsic-rewards-stage2',create_if_missing=False,version=2)
l=json.loads(b''.join(v.read_file('/budget-ledger.json')))
(OUT/'ledger-snapshot.json').write_text(json.dumps(l,indent=2))
entries={e.path.lstrip('/') for e in v.listdir('/runs',recursive=True)}
def audit(item):
 key,c=item
 row={'id':key,'ledger_status':c['status'],'function_call_id':c.get('function_call_id')}
 try:
  graph=modal.FunctionCall.from_id(c['function_call_id']).get_call_graph()
  row['provider_inputs']=[{'input_id':g.input_id,'status':g.status.name,'task_id':g.task_id} for g in graph]
 except Exception as e: row['provider_error']=str(e)
 marker=f'runs/{key}/complete.json'
 row['durable_completion']=marker in entries
 if row['durable_completion']:
  m=json.loads(b''.join(v.read_file('/'+marker)));row['marker']=m
  row['identity_matches']=m['id']==key and m['spec_sha256']==c['spec_sha256']
  checks={}
  for p,h in m['files'].items():
   if p.endswith(('metrics.jsonl','summary.json','spec.json','usage.json','outcome.json')):
    raw=b''.join(v.read_file('/'+p));checks[p]=hashlib.sha256(raw).hexdigest()==h
  row['output_hash_checks']=checks
 row['attempt_files']=[p for p in entries if p.startswith('runs/'+key+'/') and p.endswith(('attempt.json','usage.json','infrastructure_failure.json'))]
 return row
unresolved=[(k,c) for k,c in l['calls'].items() if c['status']!='complete']
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: rows=list(ex.map(audit,unresolved))
science={k:c for k,c in l['calls'].items() if k.startswith(('search_cma-','search_random-','finalist_'))}
summary={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tracked_run_id':'55d43a42-6cbd-493c-b74d-202f5714f064','cause':'ClientConnectorDNSError downloading saved result from clobber.modal-storage.com; scheduler cleanup canceled outstanding calls','search_ledger_status_counts':dict(collections.Counter(c['status'] for c in science.values())),'guard_usd':l['guard_total_usd'],'cap_usd':l['limit_usd'],'billed_complete_intervals_usd':l.get('provider_reported_complete_intervals_cost_usd'),'measured_compute_usd':sum(float(c.get('measured',{}).get('compute_cost_estimate_usd',0)) for c in l['calls'].values() if c.get('measured')),'unresolved_with_durable_completion':sum(r['durable_completion'] for r in rows),'provider_status_counts':dict(collections.Counter(g['status'] for r in rows for g in r.get('provider_inputs',[]))),'unresolved':rows,'changes_to_controller_or_volume':False}
(OUT/'interruption-audit.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='unresolved'},indent=2))
