"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-02-01
    Description: Automates the execution of CFD on SU2.
"""

import subprocess
import os
import sys
import argparse

def main():
    """
    Main function to set up and run SU2 CFD simulation.
    """
    parser = argparse.ArgumentParser(description='Run SU2 CFD simulation with either Euler or RANS solver.')
    parser.add_argument('solver', choices=['Euler', 'RANS'], help='Choose the solver type: Euler or RANS')
    parser.add_argument('directory', help='Directory to run the simulation in')

    args = parser.parse_args()

    try:
        # Set environment variables for SU2
        os.environ['SU2_RUN'] = '/path/to/SU2/Compiled-v7.2.0/bin'
        os.environ['SU2_HOME'] = '/path/to/SU2/Source-v7.2.0'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']

        # Define the working directory
        work_dir = os.path.join(args.directory, 'CFD', args.solver)
        os.makedirs(work_dir, exist_ok=True)

        # Remove existing flow output file if it exists in the working directory
        flow_output = os.path.join(work_dir, 'flow_winglet.vtu')
        if os.path.exists(flow_output):
            os.remove(flow_output)

        # Check for input mesh file in the MESH directory
        mesh_file = os.path.join(args.directory, 'MESH', 'mesh.cga')
        if os.path.exists(mesh_file):
            # Determine the configuration file based on the solver type
            cfg_file = os.path.join(args.directory, 'CFD', args.solver, f'{args.solver.lower()}-cfd.py')

            # Run SU2_CFD with the chosen configuration file
            cmd_str = f"mpiexec /path/to/SU2/Compiled-v7.2.0/bin/SU2_CFD {cfg_file}"
            subprocess.run(cmd_str, cwd=work_dir, shell=True)
        else:
            print(f"Input file '{mesh_file}' not found. Please provide the input file.")
            sys.exit(1)  # Exit if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    main()
