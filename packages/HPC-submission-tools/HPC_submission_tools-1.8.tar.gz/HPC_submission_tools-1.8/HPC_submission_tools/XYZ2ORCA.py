# -*- coding: utf-8 -*-
"""
Created on Wed May  4 13:57:18 2022

@author: bwb16179
"""
from ase.io import read
import os

def buffer(string, L, end=True):
    while len(string) < L:
        string = string+"0"
    return string

class XYZ2ORCA:
    
    def __init__(self, XYZ: list, job: str, functional: str, basis_set: str, charge: int, multiplicity: int, solvent: str, cores: int, time: str, kwargs: list):
        self.XYZ = XYZ # path of xyz file (string) i.e. path/to/job
        self.job = job # Type of DFT job i.e. (string) Opt Freq, OptTS, etc.
        self.functional = functional # Functional for the job i.e. (string)  wB97X
        self.basis_set = basis_set # Basis set for the job, i.e. (string) Def2-SVP
        self.charge = charge # Charge of the system, i.e. (integer) 1
        self.multiplicity = multiplicity # Multiplicity of the system, i.e. singlet = 1, doublet = 2
        self.solvent = solvent # solvent system i.e. (string) CPCM(Water)
        self.cores = cores # Number of cores for the job (integer), i.e. 4
        self.time = time # Time for the job i.e. (string) 02:00:00 (hours:minutes:seconds)
        self.add_kwargs = kwargs # additional keyword arguements i.e. list of strings - dispersion, SCF conv, etc.
        
        if os.environ['USER'] == 'bwb16179' or os.environ['USER'] == 'rkb19187':
            self.partition = 'standard'
            self.account = 'tuttle-rmss'
        else:
            self.partition = 'teaching'
            self.account = 'teaching'
            
        self.CPU = """#!/bin/bash
#SBATCH --export=ALL
#SBATCH --job-name={}
#SBATCH --account={}
#SBATCH --partition={}
#SBATCH --time="{}"
#SBATCH --ntasks={} --nodes=1
module purge
module load orca/5.0.4
    
/opt/software/scripts/job_prologue.sh\n
    """
        self.ElectronNos = {"H" : 1, "B" : 5, "C" : 6, "N" : 7, "O" : 8,
                            "F" : 9, "P" : 15, "S" : 16, "Cl" : 17, "Ir" : 77}
    
    def xyz2orca(self):
        frames = read(self.XYZ, index=":") # read in xyz file
        
        if not frames: # Sanity check, if empty then quit
            return False
        
        species = frames[0].get_chemical_symbols() # get elements in molecule
        
        CPUS = self.cores # number of CPU cores
        
        PAL = f"%PAL NPROCS {CPUS} END" if CPUS > 1 else "" # add in parallel line if needed
        
        strT = self.time # hours:minutes:seconds
        
        hours, mins, secs = map(int, strT.split(":")) # split time up
        
        if hours > 168: # check job won't sit in queue indefinitely
            print("Time is more than partition limit, must be <= 168 hours")
            print("Setting time to max available: 168 hours")
            strT = "168:00:00"
        
        for i,frame in enumerate(frames): # loop over the frames (we only want the first though)
            jobname = self.XYZ.replace(".xyz", ".inp") # Set a job name
            inp = jobname.split("/")[-1] # input file
            out = jobname.split("/")[-1].replace(".inp", ".out") # output file
            xyz = self.XYZ.split("/")[-1] # XYZ file
    
            with open(jobname.replace(".inp", ".sh"), 'w') as sbatch: # write an sbatch file
                sbatch.write(self.CPU.format(inp.replace(".inp", ""), self.account, self.partition, strT, str(CPUS))) # write in the formatted Preamble for the job 

                charge = self.charge # set charge
                solvent = self.solvent # set solvent
                species = frame.get_chemical_symbols() # get species
                electrons = sum(self.ElectronNos.get(atom, 0) for atom in species) # get number of electrons in molecule
                multiplicity = self.multiplicity

                with open(jobname, 'w') as f: # open input file
                    functional = self.functional
                    basis_set = self.basis_set
                    job = self.job
                    add_kwargs = " ".join(self.add_kwargs)

                    f.write(f"""# ORCA 5.0.4 - {jobname} # write input file
# Basic Mode
#
! {job} {functional} {basis_set} {add_kwargs} {solvent}

{PAL}

%maxcore 4500

%geom
Maxiter 150
END

* xyzfile {str(charge)} {multiplicity} {xyz}
""")
                sbatch.write("/opt/software/orca/5.0.4/orca {} > {}\n".format(inp, out)) # write output file end
                sbatch.write("\n/opt/software/scripts/job_epilogue.sh")

        return True
        
    def FilterChemistry(self, atomlist): # check atoms in molecule are allowed under defined parameters
        species_order = ["H", "C", "N", "O"]
        return all(atom in species_order for atom in atomlist)