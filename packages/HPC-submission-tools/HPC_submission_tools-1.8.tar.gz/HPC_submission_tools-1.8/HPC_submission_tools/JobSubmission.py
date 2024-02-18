# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 10:22:56 2023

@author: Ross James

Script for calling in to submit jobs.
The script will creat a directory from the base name of the job,
move the associated files to that directory and then submit them.

Usage:
    
from job_submitter import JobSubmitter
    
job_submitter = JobSubmitter()
job_submitter.submit_job(["path/to/your/task.sh"], additional_ext: list else None)

╭╮╱╭┳━━━┳━━━╮╱╱╭━━━╮╱╱╭╮╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╭━━━━╮╱╱╱╱╭╮
┃┃╱┃┃╭━╮┃╭━╮┃╱╱┃╭━╮┃╱╱┃┃╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱┃╭╮╭╮┃╱╱╱╱┃┃
┃╰━╯┃╰━╯┃┃╱╰╯╱╱┃╰━━┳╮╭┫╰━┳╮╭┳┳━━┳━━┳┳━━┳━╮╱╱╰╯┃┃┣┻━┳━━┫┃╭━━╮
┃╭━╮┃╭━━┫┃╱╭┳━━╋━━╮┃┃┃┃╭╮┃╰╯┣┫━━┫━━╋┫╭╮┃╭╮┳━━╮┃┃┃╭╮┃╭╮┃┃┃━━┫
┃┃╱┃┃┃╱╱┃╰━╯┣━━┫╰━╯┃╰╯┃╰╯┃┃┃┃┣━━┣━━┃┃╰╯┃┃┃┣━━╯┃┃┃╰╯┃╰╯┃╰╋━━┃
╰╯╱╰┻╯╱╱╰━━━╯╱╱╰━━━┻━━┻━━┻┻┻┻┻━━┻━━┻┻━━┻╯╰╯╱╱╱╰╯╰━━┻━━┻━┻━━╯
"""

import os
import pathlib
import shutil

class JobSubmitter:
    def __init__(self):
        self.submitted = 0
        self.i = 0
        self.extensions = [".inp", 
                           ".sh", 
                           ".out", 
                           ".opt", 
                           "_original.opt", 
                           "_original.out", 
                           ".xyz"]
        
    def dos2unix(self, file):
        """
        Function to convert dos (Windows) created files to unix based files.
        
        Parameters
        ----------
        file : str
            Path to file.

        Returns
        -------
        unix file or None.

        """
        with open(file.split("/")[-1], 'rb') as f:
            content = f.read()
            if b'\r\n' in content:
                os.system(f'dos2unix {file}')
            f.close()

    def submit_jobs(self, tasks: list, additional_ext = None):
        
        """
        Function to convert dos (Windows) created files to unix based files.
        
        Parameters
        ----------
        tasks : list
            List of paths to sbatch files.
        aidditional_ext: list
            List of additional file extensions to look for
            default: None

        Returns
        -------
        Submits jobs, returns nothing

        """

        if additional_ext is not None: # add additional extensions to search pool
            self.extensions += additional_ext
        
        for task in tasks: # loop over .sh files
            task_path = pathlib.Path(task) # get path
            name = task_path.stem.replace(".sh", "")
            stripped_name = name
            

            cdir = os.path.abspath(".") # set working directory
            folder = task_path.parent # get folder that the task is in

            os.chdir(folder) # move to that folder
            if os.name == 'posix': # check if the system is unix based
                self.dos2unix(task) # if so then run dos2unix on the file
            stripped_folder = os.path.join(folder, stripped_name) # get a name for the task folder
            os.makedirs(stripped_folder, exist_ok=True) # make the task folder

            for ext in self.extensions: # loop over extensions
                source = f"{name}{ext}"
                if os.path.exists(source): # if the file exists move the file to the task folder
                    shutil.move(source, os.path.join(stripped_folder, source))

            os.chdir(stripped_folder) # move to the task folder
            os.system(f"sbatch {name}.sh") # submit the job
            os.chdir(cdir) # move back to the working directory

            self.submitted += 1 # add 1
            self.i += 1 # add 1
            print(f"{self.i} Jobs have been submitted\n")