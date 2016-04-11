from setuptools import setup, find_packages
from pip.req import parse_requirements
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'Readme.md')).read()

version = '0.1'

install_reqs = parse_requirements(os.path.join(here, 'requirements.txt'), session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(name='sql_kernel',
    version=version,
    description="SQL Kernel for Jupyter",
    long_description=README,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
    keywords='database jupyter sqlalchemy ipython dbms',
    author='Robin Aly',
    author_email='r.aly@utwente.nl',
    url='bitbucket.org/alyr/sql_kernel',
    license='MIT',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs,
)

from jupyter_client.kernelspec import install_kernel_spec
from IPython.utils.tempdir import TemporaryDirectory
import json
import os
import sys

kernel_json = {
  "argv":[sys.executable,"-m","sql_kernel", "-f", "{connection_file}"],
  "display_name":"SQL Kernel",
  "language":"sql",
  "codemirror_mode":"sql",
  "env":{"PS1": "$"}
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