"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-06-03
    Description: Automates the execution of SU2 shape optimization process.
"""

import os
import sys
import argparse
import subprocess

def main():
    """Main function to set up and run SU2 shape optimization."""
    parser = argparse.ArgumentParser(description='Run SU2 shape optimization.')
    parser.add_argument('solver', choices=['Euler', 'RANS'], help='Choose the solver type: Euler or RANS')
    parser.add_argument('directory', help='Directory to run the optimization in')

    args = parser.parse_args()

    try:
        # Set environment variables for SU2
        os.environ['SU2_RUN'] = '/path/to/SU2/Compiled-v8.0.0/bin'
        os.environ['SU2_HOME'] = '/path/to/SU2/Source-v8.0.0'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']

        # Define the working directory
        work_dir = os.path.join(args.directory, 'ASO', args.solver)
        os.makedirs(work_dir, exist_ok=True)

        # Check for configuration file
        cfg_file = os.path.join(args.directory, 'ASO', args.solver, f'{args.solver.lower()}-shapeOptimisation.py')
        if os.path.exists(cfg_file):
            # Run SU2_DEF to preprocess the configuration
            cmd_str = f"mpiexec /path/to/SU2/Compiled-v8.0.0/bin/SU2_DEF {cfg_file}"
            subprocess.run(cmd_str, cwd=work_dir, shell=True)

            # Remove existing mesh file
            if os.path.exists(os.path.join(work_dir, 'mesh.su2')):
                os.remove(os.path.join(work_dir, 'mesh.su2'))

            # Rename the output mesh
            os.rename(os.path.join(work_dir, 'mesh_out.su2'), os.path.join(work_dir, 'mesh.su2'))

            # Run SU2_GEO to evaluate geometry
            cmd_str = f"mpiexec /path/to/SU2/Compiled-v8.0.0/bin/SU2_GEO {cfg_file}"
            subprocess.run(cmd_str, cwd=work_dir, shell=True)

            # Run the shape optimization
            cmd_str = f"python3 /path/to/SU2/Compiled-v8.0.0/bin/shape_optimization.py -n 48 -g DISCRETE_ADJOINT -f {cfg_file}"
            subprocess.run(cmd_str, cwd=work_dir, shell=True)
        else:
            print(f"Input file '{cfg_file}' not found. Please provide the configuration file.")
            sys.exit(1)  # Exit if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    main()