# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 11:04:42 2023

@author: bwb16179
"""

from distutils.core import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'HPC_submission_tools',         # How you named your package folder (MyLib)
  packages = ['HPC_submission_tools'],   # Chose the same as "name"
  version = '1.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Tools pertaining to use of HPC clusters with slurm file systems',   # Give a short description about your library
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Ross Urquhart',                   # Type in your name
  author_email = 'ross.urquhart@strath.ac.uk',      # Type in your E-Mail
  url = 'https://github.com/RossJamesUrquhart/HPC_submission_tools',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/RossJamesUrquhart/HPC_submission_tools/archive/refs/tags/v1.8.tar.gz',    # I explain this later on
  keywords = ['HPC', 'Command line'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',      #Specify which pyhton versions that you want to support
  ],
)