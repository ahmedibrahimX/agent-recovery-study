#!/usr/bin/env python3
"""Inspect protected evidence locally; do not post decrypted AppWorld material online."""
import argparse,sys
from verify import Store
p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',nargs='?');p.add_argument('--extract-to');a=p.parse_args();s=Store()
try:
 if not a.path:
  for path in s.call(op='manifest')['files']:print(path)
 elif a.extract_to:s.extract(a.path,a.extract_to)
 else:sys.stdout.buffer.write(s.get(a.path))
finally:s.close()
