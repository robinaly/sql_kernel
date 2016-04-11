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

