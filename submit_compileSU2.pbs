#!/bin/bash
#PBS -l walltime=8:00:00
#PBS -l select=1:ncpus=8:mem=200gb

# FYP: "Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster"
# Author: Jaime Galiana Herrera
# Date: 2024-06-03

# Description: This script sets up the necessary environment and compiles the SU2 code with 
#              Automatic Differentiation (AD) capabilities on the Imperial HPC cluster. The process 
#              includes loading required modules, setting environment variables, cloning the SU2 
#              source code, and compiling it with specific options enabled.
#
# Inputs required:
# - None. 

module load tools/prod
module load Python/3.10.8-GCCcore-12.2.0
module load OpenMPI/4.1.4-GCC-12.2.0
module load CMake/3.24.3-GCCcore-12.2.0

# Environmental variables, not entirely sure if they are needed
export MPICC=$(which mpicc)
export MPICXX=$(which mpicxx)
export CC=mpicc
export CXX=mpicxx

# Path to folder where you want to place your source code
cd /rds/general/user/username/home/

# Clone last version of source code in the directory
git clone https://github.com/su2code/SU2.git

# Access the folder containing the source code
cd SU2

# --prefix= specify the path where you want the compiled code to be 
python3 ./meson.py build -Denable-autodiff=true -Denable-directdiff=true -Dwith-mpi=enabled --prefix=/path/to/install/directory

# j defines the number of cores to use (all available cores are used by default)
./ninja -j8 -C build install