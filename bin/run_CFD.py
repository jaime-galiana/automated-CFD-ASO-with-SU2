"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-02-01
    Description: Automates the execution of CFD on SU2.
"""

import subprocess
import os
import sys

def main():
    """
    Main function to set up and run SU2 CFD simulation.
    """
    try:
        # Set environment variables for SU2
        os.environ['SU2_RUN'] = '/rds/general/user/jg2219/home/Compiled-SU2-7.2.0-mpi/bin'
        os.environ['SU2_HOME'] = '/rds/general/user/jg2219/home/Source/SU2-7.2.0/SU2-7.2.0'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']

        # Remove existing flow output file if it exists
        if os.path.exists('./flow_winglet.vtu'):
            os.remove('./flow_winglet.vtu')

        # Check for input mesh file
        if os.path.exists('./mesh.cga'):
            print("Simulating... ")
            # Run SU2_CFD with the given configuration file
            cmd_str = "mpiexec /rds/general/user/jg2219/home/Compiled-SU2-7.2.0-mpi/bin/SU2_CFD /rds/general/user/jg2219/ephemeral/Final-try/bin/EULER-cfd.cfg"
            subprocess.run(cmd_str, shell=True)
        else:
            print("Input file 'mesh.cga' not found. Please provide the input file.")
            sys.exit(1)  # Exit if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    main()