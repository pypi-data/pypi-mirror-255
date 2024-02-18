#!/usr/bin/env python
from setuptools import setup, find_packages

with open('fsl_sub_plugin_slurm/version.py', mode='r') as vf:
    vl = vf.read().strip()

PLUGIN_VERSION = vl.split(' = ')[1].strip("'")

with open('README.md', mode='rt') as f:
    README = f.read().strip()

setup(
    name='fsl_sub_plugin_slurm',
    version=PLUGIN_VERSION,
    description='FSL Cluster Submission Plugin for Slurm',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Duncan Mortimer',
    author_email='duncan.mortimer@ndcn.ox.ac.uk',
    url='https://git.fmrib.ox.ac.uk/fsl/fsl_sub_plugin_slurm',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Natural Language :: English',
        'Environment :: Console',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='FSL fsl Neuroimaging neuroimaging cluster'
             ' grid slurm',
    project_urls={
        'Documentation': 'https://fsl.fmrib.ox.ac.uk/fsl/fslwiki',
        'Source': 'https://git.fmrib.ox.ac.uk/fsl/fsl_sub_plugin_slurm'
    },
    packages=find_packages(),
    license='Apache License Version 2.0',
    install_requires=['fsl_sub>=2.8.0', 'ruamel.yaml>=0.16.7', ],
    python_requires='~=3.7',
    package_data={
        'fsl_sub_plugin_slurm': [
            'fsl_sub_slurm.yml', 'README.md', 'CHANGES.md',
            'BUILD.md', 'INSTALL.md', 'LICENSE', ],
    },
    include_package_data=True,
)
