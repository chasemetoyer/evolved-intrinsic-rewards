"""Independent volume reader and tracking publisher. Never imports training code."""
import argparse,json,time,math,os,hashlib
from pathlib import Path
import modal
from stage3.common import ROOT,VOLUME_NAME,canonical_sha,cpu_class
from stage3.tracking import TrackioSink,snapshot_payload,quiet_tracking_output
from stage2.transport import retry_io

def collect(volume,profile,cache=None):
 cache={} if cache is None else cache
 def raw(p):return retry_io(lambda:b''.join(volume.read_file(p)))
 ledger=json.loads(raw('/budget-ledger.json'));records=[];errors=[]
 for key,row in list(ledger['calls'].items()):
  if not key.startswith('stage3_'+profile+'-') or row['status']!='complete':continue
  if key in cache:
   records.append(cache[key]);continue
  try:
   marker=json.loads(raw('/runs/'+key+'/complete.json'));prefix=f'/runs/{key}/attempts/{marker["attempt"]}/'
   def checked(name):
    data=raw(prefix+name);expected=marker['files'].get((prefix+name).lstrip('/'))
    if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Result hash mismatch')
    return data
   spec=json.loads(checked('spec.json'))
   if canonical_sha(spec)!=row['spec_sha256'] or marker['id']!=key:raise ValueError('Recorded input mismatch')
   metrics=[json.loads(s) for s in checked('metrics.jsonl').decode().splitlines() if s.strip()]
   windows={w['global_step']:w for w in [json.loads(s) for s in checked('descriptive-windows.jsonl').decode().splitlines() if s.strip()]}
   for metric in metrics:
    w=windows.get(metric['global_step'],{})
    for a,b in [('presses_per_step','tamper/presses_per_step'),('presses_per_episode','tamper/presses_per_episode'),('episode_intrinsic_return_mean','intrinsic/episode_return')]:
     if w.get(a) is not None:metric[b]=w[a]
   env=json.loads(checked('environment.json'));success=[m.get('train/success',0.) for m in metrics]
   import numpy as np
   area=float(np.mean(success));solved=float(np.mean(success[-max(1,len(success)//10):]))>=.9
   record={'method':spec['method'],'task':spec['task'],'seed':spec['seed'],'metrics':metrics,'area':area,'solved':solved,'cpu_class':cpu_class(env['cpu'])};records.append(record);cache[key]=record
  except Exception as e:errors.append({'id':key,'error_type':type(e).__name__})
 from collections import Counter
 physical={}
 for entry in volume.listdir('/runs',recursive=True):
  parts=Path(entry.path.lstrip('/')).parts
  if parts and parts[0]!='runs':parts=('runs',)+parts
  if len(parts)==5 and parts[1].startswith('stage3_'+profile+'-') and parts[2]=='attempts':
   physical.setdefault('/'.join(parts[:4]),set()).add(parts[4])
 mix=Counter()
 for directory,names in physical.items():
  cachekey=('cpu',directory)
  try:
   if cachekey not in cache and 'environment.json' in names:
    cache[cachekey]=cpu_class(json.loads(raw('/'+directory+'/environment.json'))['cpu'])
   mix[cache.get(cachekey,'unknown')]+=1
  except Exception:mix['unknown']+=1
 ledger['physical_cpu_mix']=dict(mix)
 ledger['candidate_failures']=sum(r['status']=='numerical_failure' for r in ledger['calls'].values())
 ledger['observed_restarts']=sum(max(0,r.get('attempt_count',1)-1) for r in ledger['calls'].values())
 return records,ledger,errors

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected',type=int,default=20);args=p.parse_args()
 profile=json.loads((ROOT/'stage3/mode.json').read_text())['profile']
 volume=modal.Volume.from_name(VOLUME_NAME,create_if_missing=False,version=2);sink=TrackioSink();iteration=0;cache={}
 while True:
  try:
   with quiet_tracking_output():
    records,ledger,errors=collect(volume,profile,cache);result=sink.publish(snapshot_payload(records,ledger,args.expected),iteration)
   print(json.dumps({'event':'tracking_observer','iteration':iteration,'completed':len(records),'read_errors':errors,'tracking':result}),flush=True)
  except Exception as error:print(json.dumps({'event':'tracking_observer_error','error_type':type(error).__name__}),flush=True)
  iteration+=1;time.sleep(60)
if __name__=='__main__':
 with quiet_tracking_output():main()
