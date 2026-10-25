#!/usr/bin/env python3
"""Recheck saved evidence offline. Does not call models or execute generated code."""
import argparse,base64,collections,hashlib,importlib.util,json,math,shutil,statistics,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STUDIES={'v6':'runs/live-v6-heldout-2026-10-22T21-19-27.251Z','v7':'runs/live-v7-heldout-2026-10-22T21-44-23.043Z'}
EXPECTED={'v6':{'runs':48,'passed':{'langchain_native':23,'langchain_code':23},'models':{'langchain_native':66,'langchain_code':93},'public':{'langchain_native':42,'langchain_code':57},'cost':3.400222},'v7':{'runs':24,'passed':{'langchain_native':12,'langchain_code':11},'models':{'langchain_native':35,'langchain_code':38},'public':{'langchain_native':23,'langchain_code':30},'cost':1.598256}}
class Store:
 def __init__(self):
  self.p=subprocess.Popen(['node',str(ROOT/'tools/store.mjs'),'serve'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
 def call(self,**q):
  self.p.stdin.write(json.dumps(q)+'\n');self.p.stdin.flush();line=self.p.stdout.readline()
  if not line:raise RuntimeError('Evidence process exited')
  r=json.loads(line)
  if not r['ok']:raise RuntimeError(r['error'])
  return r['result']
 def get(self,path):return base64.b64decode(self.call(op='get',path=path))
 def json(self,path):return json.loads(self.get(path))
 def extract(self,prefix,out):self.call(op='extract',prefix=prefix,out=str(out))
 def close(self):self.p.stdin.close();self.p.wait(timeout=10)
def load(p):return json.loads(p.read_text())
def norm(v):
 if isinstance(v,list):return [norm(x) for x in v]
 if isinstance(v,dict):return {k:'OPAQUE_TOKEN' if k=='access_token' else norm(x) for k,x in v.items()}
 return v
def describe(xs):
 xs=sorted(xs);return {'medianMs':statistics.median(xs),'p90Ms':xs[math.ceil(.9*len(xs))-1]}
def price(u):return (u.get('input_tokens',0)*2+u.get('output_tokens',0)*10+u.get('cache_creation_input_tokens',0)*2.5+u.get('cache_read_input_tokens',0)*.2)/1e6
def close(a,b):assert abs(a-b)<1e-8,(a,b)
def verify_study(store,manifest,v,temp):
 prefix=STUDIES[v];summary=store.json(prefix+'/summary.json');expected=EXPECTED[v];source='experiments/live-'+v
 spec=importlib.util.spec_from_file_location('frozen_checker_'+v,temp/'checker.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
 reservation=store.json(source+'/heldout.json');freeze=store.json(source+'/freeze.json')
 for original,h in freeze['files'].items():
  path=str(Path(original).relative_to(manifest['originalRoot']));assert manifest['files'][path]['sha256']==h,'Frozen source differs: '+path
 assert store.json(source+'/reservation.json')['reservedAt']<freeze['frozenAt'],'Reservation after freeze'
 contexts=collections.defaultdict(list);group=collections.defaultdict(list);paired=collections.defaultdict(dict);seen=set();format_errors=0;blocks=0;envelopes=collections.Counter()
 for r in summary['results']:
  case=r['case'];arm=r['arm'];assert (case,arm) not in seen;seen.add((case,arm))
  casepath=prefix+'/'+case+'/'+arm;folder=temp/'case';store.extract(casepath,folder)
  try:
   c=load(folder/'case.json');assert c==next(x for x in reservation if x['id']==case),'Unreserved case'
   fresh=checker.check(folder);saved=load(folder/'verdict.json');assert fresh==saved,'Verdict changed: '+case+'/'+arm
   for k,value in fresh.items():assert r[k]==value,'Summary/verdict mismatch: '+k
   runtime=load(folder/'runner.json');usage=load(folder/'model-usage.json');responses=sorted(folder.glob('model-*-response.json'));requests=sorted(folder.glob('model-*-request.json'))
   assert len(usage)==len(responses)==len(requests)==fresh['modelCalls']
   response_usage=[load(x)['usage'] for x in responses]
   # requests are stored with numeric indices; sum is order independent.
   close(sum(price(x) for x in response_usage),fresh['costUsd']);close(sum(x['costUsd'] for x in usage),fresh['costUsd'])
   assert all(x['model']=='claude-sonnet-5' for x in usage)
   history=load(folder/'history.json');calls={x['callSeq']:x for x in history if x['kind']=='public_call' and x['actor']=='agent'}
   native=sum(x['atMs']-calls[x['callSeq']]['atMs'] for x in history if x['kind'] in ['public_result','public_error'] and x.get('actor')=='agent' and x.get('callSeq') in calls)
   model=sum(x['latencyMs'] for x in usage);agent=runtime['agentTimeToSubmissionMs']
   item={**fresh,'agentMs':agent,'totalMs':runtime['latencyMs'],'modelMs':model,'publicMs':native,'otherMs':agent-model-native}
   group[arm].append(item);paired[case][arm]=item;contexts[case].append(norm(load(folder/'initial-context.json')))
   if arm=='langchain_code':
    outputs=load(folder/'outputs.json');format_errors+=sum(bool(x.get('error')) for x in outputs);blocks+=len(list(folder.glob('program-*.js')))
    for e in folder.glob('envelope-*.json'):envelopes.update([load(e)['form']])
  finally:shutil.rmtree(folder)
 assert len(seen)==expected['runs'];assert len(paired)==len(reservation)
 assert all(len(x)==2 and x[0]==x[1] for x in contexts.values()),'Paired initial context differs'
 report={'runs':len(seen),'sourceFreezeFiles':len(freeze['files']),'pairedContextsMatched':len(contexts),'arms':{},'formatErrors':format_errors,'codeBlocks':blocks,'envelopes':dict(envelopes)}
 for arm,rs in group.items():
  assert sum(x['passed'] for x in rs)==expected['passed'][arm]
  assert sum(x['modelCalls'] for x in rs)==expected['models'][arm]
  assert sum(x['publicCalls'] for x in rs)==expected['public'][arm]
  assert sum(x['invalidEffects'] for x in rs)==0
  report['arms'][arm]={key:sum(x[key] for x in rs) for key in ['passed','publicCalls','modelCalls','invalidEffects','lostHumanEdit','duplicateEffects','blockedMutationAttempts','unnecessaryIntervention','repeatedReadsWithoutInterveningWrite']}
  report['arms'][arm].update(runs=len(rs),costUsd=sum(x['costUsd'] for x in rs),exactExposures=sum(x['exactScheduleExposed'] for x in rs),fallbacks=sum(x['timingFallback'] for x in rs),failures=[{'family':x['family'],'issues':x['issues']} for x in rs if not x['passed']])
  report['arms'][arm]['timing']={key:describe([x[key] for x in rs]) for key in ['agentMs','totalMs','modelMs','publicMs','otherMs']}
 ds=[x['langchain_native']['agentMs']-x['langchain_code']['agentMs'] for x in paired.values() if all(r['passed'] for r in x.values())]
 report['jointlySuccessfulPairs']={'n':len(ds),'medianNativeMinusCodeMs':statistics.median(ds),'nativeFaster':sum(x<0 for x in ds)}
 before=store.json(prefix+'/budget-before.json');after=store.json(prefix+'/budget-after.json');cost=sum(x['costUsd'] for rs in group.values() for x in rs)
 close(cost,expected['cost']);close(after['spentUsd']-before['spentUsd'],cost);assert not after['reservations']
 report['matrixCostUsd']=cost
 if v=='v7':
  assert format_errors==0 and blocks==26
  assert store.get('experiments/live-v7/checker.py')==store.get('experiments/live-v6/checker.py')
  assert report['jointlySuccessfulPairs']=={'n':11,'medianNativeMinusCodeMs':-2734,'nativeFaster':8}
 return report

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--study',choices=['all','v6','v7'],default='all');parser.add_argument('--output',type=Path,help='Optional local JSON report');args=parser.parse_args()
 if sys.version_info<(3,12):raise RuntimeError('Python 3.12+ required')
 store=Store()
 try:
  integrity=store.call(op='verify');manifest=store.call(op='manifest');reports={}
  with tempfile.TemporaryDirectory(prefix='agent-recovery-verify-') as td:
   temp=Path(td)
   (temp/'checker.py').write_bytes(store.get('experiments/live-v7/checker.py'))
   for v in STUDIES if args.study=='all' else [args.study]:
    reports[v]=verify_study(store,manifest,v,temp)
  budget=store.json('runs/pilot-budget/budget.json');assert budget['spentUsd']<=30 and not budget['reservations']
  result={'verification':'matched saved evidence, including expected agent failures','integrity':integrity,'studies':reports,'sharedSpendUsd':budget['spentUsd'],'independentHumanReview':'pending','freshLiveReexecution':'not performed'}
  text=json.dumps(result,indent=2);print(text)
  if args.output:args.output.write_text(text+'\n')
 finally:store.close()
if __name__=='__main__':main()
