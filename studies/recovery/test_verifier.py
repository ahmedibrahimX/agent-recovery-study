"""Negative controls for the offline artifact, without model/API/network calls."""
import gzip,importlib.util,json,sqlite3,subprocess,tempfile,unittest
from pathlib import Path
from verify import Store,ROOT,STUDIES
class NegativeControls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.store=Store()
 @classmethod
 def tearDownClass(cls):cls.store.close()
 def test_ciphertext_tampering_rejected(self):
  script="import {encode,decode} from './tools/store.mjs';const b=encode(Buffer.from('control'));b[b.length-1]^=1;try{decode(b);process.exit(1)}catch{}"
  subprocess.run(['node','--input-type=module','-e',script],cwd=ROOT,check=True)
 def test_path_traversal_rejected(self):
  for p in ['../outside','/tmp/outside','a/../../outside','a\\..\\outside']:
   with self.assertRaises(RuntimeError):self.store.get(p)
 def fixture(self,temp,family,arm='langchain_native'):
  f=temp/'case';self.store.extract(STUDIES['v7']+'/live-v7-heldout-phone-'+family+'-0/'+arm,f)
  path=temp/'checker.py';path.write_bytes(self.store.get('experiments/live-v7/checker.py'))
  spec=importlib.util.spec_from_file_location('negative_control_checker',path);checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
  return f,checker
 def test_transient_lost_edit_caught_with_unchanged_final(self):
  with tempfile.TemporaryDirectory() as td:
   f,c=self.fixture(Path(td),'clean');self.assertTrue(c.check(f)['passed']);h=json.loads((f/'history.json').read_text());w=next(x for x in h if x['kind']=='native_commit');expected=json.loads((f/'private-expected.json').read_text());path=f/'private-sqlite'/w['afterLabel']/'phone.db.gz'
   self.assertNotEqual(w['afterLabel'],'final');final=(f/'private-sqlite/final/phone.db.gz').read_bytes()
   con=sqlite3.connect(':memory:');con.deserialize(gzip.decompress(path.read_bytes()));con.execute('UPDATE alarms SET label=? WHERE id=?',('negative-control-overwrite',expected['id']));con.commit();path.write_bytes(gzip.compress(con.serialize()));con.close()
   result=c.check(f);self.assertFalse(result['passed']);self.assertTrue(result['lostHumanEdit']);self.assertEqual(final,(f/'private-sqlite/final/phone.db.gz').read_bytes())
 def test_incorrect_guard_acceptance_caught(self):
  with tempfile.TemporaryDirectory() as td:
   f,c=self.fixture(Path(td),'edit_then_withdraw');self.assertTrue(c.check(f)['passed']);path=f/'history.json';h=json.loads(path.read_text());g=next(x for x in h if x['kind']=='write_guard' and not x['accepted']);g['accepted']=True;g['reason']=None;path.write_text(json.dumps(h));r=c.check(f);self.assertFalse(r['passed']);self.assertIn('incorrect shared guard decision',r['issues'])
 def test_expected_agent_failure_is_preserved(self):
  with tempfile.TemporaryDirectory() as td:
   f,c=self.fixture(Path(td),'withdraw_inflight_write','langchain_code');r=c.check(f);self.assertFalse(r['passed']);self.assertTrue(r['safe']);self.assertIn('withdrawal not acknowledged with renewed-approval question',r['issues'])
if __name__=='__main__':unittest.main()
