# HPC_Submission_Tools

Repo for tools to help with slurm submission and management within ARCHIE-WeST HPC cluster

## Install

From cloning repo

```
git clone https://www.github.com/RossJamesUrquhart/HPC_submission_tools
pip install .
```

From PyPi

```
pip install HPC-submission-tools
```

## JobSubmitter - Usage

```
from HPC_submission_tools import JobSubmission
JobSubmitter = JobSubmitter()

JobSubmitter.submit_jobs([path/to/sbatch/files], additional_ext=None)

```

The ```additional_ext``` keyword will take a list of any extensions not already considered by the script to search for those to mvoe alongside the sbatch files.

## XYZ2ORCA - Usage

```
from HPC_submission_tools import XYZ2ORCA

xyz = ["2,6-XylH+.xyz"] # list of xyz files to process

functional = "wB97X"
job = "Opt Freq"
basis_set= "Def2-SVP"
solvation = "CPCM(Water)"
time = "01:00:00"
cores = 4
charge = 1
kwargs = ["SlowConv", "TightSCF", "DEFGRID2", "Def2/J", "RIJCOSX"]

for x in xyz:
    process = XYZ2ORCA(x, job, functional, basis_set, charge, solvation, cores, time, kwargs)
    process.xyz2orca()
```
