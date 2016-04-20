#!/usr/bin/env python
from jupyter_client.kernelspec import install_kernel_spec
from IPython.utils.tempdir import TemporaryDirectory
import json
import os
import sys

kernel_json = {
  "argv":[sys.executable,"-m","sql_kernel", "-f", "{connection_file}"],
  "display_name":"SQL Kernel",
  "language":"sql",
  "codemirror_mode":"sql"
}

def install_my_kernel_spec(user=True):
  with TemporaryDirectory() as td:
    os.chmod(td, 0o755) # Starts off as 700, not user readable
    with open(os.path.join(td, 'kernel.json'), 'w') as f:
        json.dump(kernel_json, f, sort_keys=True)
    install_kernel_spec(td, 'sql_kernel', user=user, replace=True)

def _is_root():
  try:
      return os.geteuid() == 0
  except AttributeError:
      return False # assume not an admin on non-Unix platforms

argv = sys.argv
user = '--user' in argv or not _is_root()
install_my_kernel_spec(user=user)