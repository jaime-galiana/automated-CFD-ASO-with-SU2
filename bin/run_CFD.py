#Tool for the automation of geometry parametrisation, meshing and CFD simulation for aerodynamic shape optimisation
#designed to run on the Imperial College London RCS HPC system

import subprocess
import os
import sys

def main():
    try:
        # Set environment variables
        os.environ['SU2_RUN'] = '/rds/general/user/jg2219/home/Compiled-SU2-7.2.0-mpi/bin'
        os.environ['SU2_HOME'] = '/rds/general/user/jg2219/home/Source/SU2-7.2.0/SU2-7.2.0'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']

        # Check and remove existing files
        if os.path.exists('./flow_winglet.vtu'):
            os.remove('./flow_winglet.vtu')

        # Check if input file exists
        if os.path.exists('./mesh.cga'):
            print("Simulating... ")
            cmd_str = "mpiexec /rds/general/user/jg2219/home/Compiled-SU2-7.2.0-mpi/bin/SU2_CFD /rds/general/user/jg2219/ephemeral/Final-try/bin/EULER-cfd.cfg"
            subprocess.run(cmd_str, shell=True)
        else:
            print("Input file 'mesh.cga' not found. Please provide the input file.")
            sys.exit(1)  # Exit with error code 1 if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit with error code 1 if an exception occurs

if __name__ == "__main__":
    main()