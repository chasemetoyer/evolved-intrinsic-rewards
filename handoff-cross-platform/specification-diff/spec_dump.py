"""Generate one frozen input specification; no training, controller, volume writes or search."""
from pathlib import Path
import hashlib,importlib.metadata,json,os,platform,sys,resource,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
ROOT=Path(__file__).resolve().parents[1]
KEY='search_cma-g00-c000-DoorKey-8x8-2000000-seed1000'


def main():
    protocol=json.loads((ROOT/'diagnostics/protocol.json').read_text())
    for name,expected in protocol['calculation_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Calculation input changed: '+name)
    from stage2.cloud import ResumeSearchPlan
    from stage2.search import REGISTERED_DRAFT
    from stage2.common import canonical_sha,parse_cpuinfo,cpu_class
    import numpy as np
    plan=ResumeSearchPlan(REGISTERED_DRAFT)
    spec=plan.spec_for_key(KEY)
    cpu=parse_cpuinfo(Path('/proc/cpuinfo').read_text() if Path('/proc/cpuinfo').exists() else None)
    payload={'specification':spec,'canonical_sha256':canonical_sha(spec),'target_key':KEY,
             'platform':platform.platform(),'machine':platform.machine(),'python':platform.python_version(),
             'versions':{name:importlib.metadata.version(name) for name in ['numpy','cma','scipy']},
             'cpu':cpu,'cpu_class':cpu_class(cpu),'source_commit':os.environ.get('ORX_COMMIT'),
             'run_id':os.environ.get('ORX_RUN_ID'),'training_submissions':0,
             'process_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
             'note':'Pure generation of the specified first input. No controller/worker API called; no historical fitness consumed by the first ask.'}
    print('SPEC_DUMP_BEGIN',flush=True)
    print(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False),flush=True)
    print('SPEC_DUMP_END',flush=True)

if __name__=='__main__':main()
