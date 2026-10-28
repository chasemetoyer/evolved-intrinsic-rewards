"""Compare every JSON field, retaining exact float64 representation and differences."""
from pathlib import Path
import csv,difflib,hashlib,json,struct
from decimal import Decimal,localcontext
BASE=Path(__file__).resolve().parent

def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def ordered(x):
 b=struct.unpack('>Q',struct.pack('>d',x))[0]
 return (~b&((1<<64)-1)) if b>>63 else b|(1<<63)

def main():
 a=json.loads((BASE/'mac-specification.json').read_text());b=json.loads((BASE/'linux-specification.json').read_text())
 rows=[];unchanged=[]
 def visit(x,y,path='$'):
  if isinstance(x,dict) and isinstance(y,dict):
   assert set(x)==set(y),'Object keys differ at '+path
   for k in sorted(x):visit(x[k],y[k],path+'.'+k)
  elif isinstance(x,list) and isinstance(y,list):
   assert len(x)==len(y),'Array lengths differ at '+path
   for i,(u,v) in enumerate(zip(x,y)):visit(u,v,f'{path}[{i}]')
  else:
   same=type(x)==type(y) and (struct.pack('>d',x)==struct.pack('>d',y) if isinstance(x,float) else x==y)
   if same:unchanged.append(path);return
   row={'field':path,'mac':repr(x),'linux':repr(y),'mac_type':type(x).__name__,'linux_type':type(y).__name__}
   if isinstance(x,float) and isinstance(y,float):
    with localcontext() as context:
     context.prec=110
     row.update(mac_hex=x.hex(),linux_hex=y.hex(),linux_minus_mac=str(Decimal.from_float(y)-Decimal.from_float(x)),ulp_distance=abs(ordered(x)-ordered(y)))
   rows.append(row)
 visit(a,b)
 assert canonical(a)=='6984a4a2f4eedf4408a645b4986ea825c4a60e6153769374f0cd58b26ef3fa3a'
 assert canonical(b)=='f65304c4d5315a0ac775bb302457e86220ccf47f2b00b6f719a726f41212b639'
 vector=[r for r in rows if r['field'].startswith('$.latent[')]
 summary={'mac_canonical_sha256':canonical(a),'linux_canonical_sha256':canonical(b),
          'original_mac_hash_reproduced':True,'original_failed_linux_hash_reproduced':True,
          'different_leaf_fields':len(rows),'identical_leaf_fields':len(unchanged),
          'candidate_vector_differs_numerically':bool(vector),'different_vector_indices':[int(r['field'].split('[')[1][:-1]) for r in vector],
          'differences':rows,'identical_fields':unchanged,
          'conclusion':'Scientific candidate-vector and decoded reward parameters differ. Non-scientific-field fix is inapplicable. Stop; no fix, replay-check rerun or training restart.'}
 (BASE/'field-differences.json').write_text(json.dumps(summary,indent=2)+'\n')
 with (BASE/'field-differences.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['field','mac','linux','linux_minus_mac','ulp_distance','mac_hex','linux_hex','mac_type','linux_type']);w.writeheader();w.writerows(rows)
 diff=''.join(difflib.unified_diff((BASE/'mac-specification.json').read_text().splitlines(keepends=True),(BASE/'linux-specification.json').read_text().splitlines(keepends=True),fromfile='mac-specification.json',tofile='linux-specification.json'))
 (BASE/'specification.diff').write_text(diff)
 table='| Field | Mac | Linux | Linux − Mac | ULPs |\n|---|---:|---:|---:|---:|\n'
 for r in rows:table+=f"| `{r['field']}` | `{r['mac']}` | `{r['linux']}` | `{r.get('linux_minus_mac','')}` | {r.get('ulp_distance','')} |\n"
 report=f'''# Exact Mac–Linux input specification diagnosis

Target: `search_cma-g00-c000-DoorKey-8x8-2000000-seed1000`.

**The candidate vector itself differs numerically.** Its zero-based coordinates **4, 7, 10 and 11** differ by exactly one float64 ULP each. Decoded relief parameters 0 and 3 and growth parameter 3 differ as well, including their copies in the training configuration. These are scientific input fields. A paths/version/platform-only fix is therefore inapplicable.

## Full specifications and provenance

- [Mac full input](mac-specification.json), [Mac execution metadata](mac-dump-metadata.json).
- [Linux full input](linux-specification.json), [Linux execution metadata](linux-dump-metadata.json).
- [Complete unified diff](specification.diff).
- [Every changed field, exact values, float hex and ULPs](field-differences.csv).
- [Machine-readable comparison, including every unchanged field](field-differences.json).

The Mac specification reproduces the original recorded canonical SHA256 `{canonical(a)}`. The diagnostic Linux specification reproduces the failed replay's canonical SHA256 `{canonical(b)}` **exactly**. This is a faithful regeneration of both compared inputs, not a comparison against a different Linux output. The failed check had saved only hashes; the full Linux input was generated in this new explicitly authorized read-only diagnostic.

These are hashes of compact, key-sorted JSON, matching the registered hash function. Pretty-printed file-byte hashes are different because whitespace differs. Metadata is stored separately and is not part of the input hash.

The isolated diagnostic run is `fc91e753-e0e1-467a-af65-44566804fb09`, source `de75a8e49c6b06ca9e57c63dcfed48545f5079f5`, Linux Intel family 6, model 85, with the same pinned NumPy/CMA/SciPy versions as the Mac. It only constructs the specified first input and prints it. No trainer, controller, historical ask/tell replay or worker/volume mutation is invoked. The reported Mac dump was regenerated after that diagnostic protocol was committed; an earlier local sanity dump gave the same hash.

## All differing fields

{table}

No object keys, array lengths or scalar types differ. **All other {len(unchanged)} leaf fields are identical**, including paths and non-scientific input metadata. The dump execution metadata necessarily describes different platforms, but those platform/version/CPU records are outside the specifications and are not responsible for this hash comparison.

Vector coordinates 4 and 7 map directly to relief for `new_view` and `toggle`, respectively. Coordinate 10 is the drop-growth latent value; both platform values are below 0.5, so both decode to growth 0. Coordinate 11 controls toggle growth, whose decoded values differ by 4 ULPs. The record does not identify the lower-level operation/library responsible for the differing initial samples; no untested numerical-cause claim is made.

## Scope and stop

The registered search runtime, scientific code, lock files, configurations and provider ledger are unchanged by this diagnosis. The Linux job used a separate child experiment with only a diagnostic launcher and script; its calculation-input hashes were recorded before launch. Its isolated launcher is not a change to the registered search launcher. Both full specifications and the field comparison are mirrored into the canonical Mac handoff folder.

Per the user's instruction: **stop and report**. No metadata fix, replay-check rerun or training restart has been performed or proposed as a workaround for this numerical mismatch. The user said they will resume on the Mac after this finding; no Mac restart is inferred from that statement.
'''
 (BASE/'specification-diff-report.md').write_text(report)
 print(json.dumps({k:v for k,v in summary.items() if k not in ['differences','identical_fields']},indent=2))

if __name__=='__main__':main()
