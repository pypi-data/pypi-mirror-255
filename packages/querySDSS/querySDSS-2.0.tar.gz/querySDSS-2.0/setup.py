import setuptools
from setuptools import setup, find_packages
import os
import subprocess

# Verifica se o pandoc está instalado
try:
    subprocess.check_call(['pandoc', '--version'])
    pandoc_installed = True
except (OSError, subprocess.CalledProcessError):
    pandoc_installed = False

# Converte o README.md para rst usando pandoc, se estiver instalado
if pandoc_installed:
    subprocess.call(['pandoc', 'README.md', '-o', 'README.rst'])
    with open('README.rst', 'r') as f:
        long_description = f.read()
else:
    long_description = open('README.md').read()

# Restante do seu setup.py
setup(
    name='querySDSS',
    version='2.0',
    license='MIT',
    author="aCosmicDebbuger",
    author_email='acosmicdebugger@gmail.com',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/aCosmicDebugger/querySDSS',
    keywords='example project',
    install_requires=[
          'astropy', 'astroquery',
      ],
    description='Query for SDSS datarelease 18',
    long_description=long_description,
)

