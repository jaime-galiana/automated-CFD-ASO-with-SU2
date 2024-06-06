"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-06-03
    Description: Automates the execution of SU2 shape optimization process.
"""

import subprocess
import os
import sys
import argparse

def main():
    """Main function to set up and run SU2 shape optimization."""
    parser = argparse.ArgumentParser(description='Run SU2 shape optimization.')
    parser.add_argument('solver', choices=['Euler', 'RANS'], help='Choose the solver type: Euler or RANS')
    parser.add_argument('directory', help='Directory to run the optimization in')

    args = parser.parse_args()

    try:
        # Set environment variables for SU2
        os.environ['SU2_RUN'] = '/path/to/SU2_v7.2.0_Binaries'
        os.environ['SU2_HOME'] = '/path/to/SU2_v8.0.0_Source'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']

        # Define the working directory
        work_dir = os.path.join(args.directory, 'ASO', args.solver)
        os.makedirs(work_dir, exist_ok=True)

        # Check for input mesh file in the MESH directory
        mesh_file = os.path.join(args.directory, 'MESH', 'mesh.cga')
        if not os.path.exists(mesh_file):
            print(f"Input mesh file '{mesh_file}' not found. Please generate the mesh first.")
            sys.exit(1)  # Exit if input file is missing

        # Copy the mesh file to the working directory
        subprocess.run(['cp', mesh_file, work_dir])

        # Check for configuration file
        cfg_file = os.path.join(args.directory, 'ASO', args.solver, f'{args.solver.lower()}-shapeOptimisation.py')
        if os.path.exists(cfg_file):
            # Run SU2_DEF to preprocess the configuration
            cmd_str = f"mpiexec /path/to/SU2_v7.2.0_Binaries/SU2_DEF {cfg_file}"
            subprocess.run(cmd_str, cwd=work_dir, shell=True)

            # Remove existing mesh file
            if os.path.exists(os.path.join(work_dir, 'mesh.su2')):
                os.remove(os.path.join(work_dir, 'mesh.su2'))

            # Rename the output mesh
            os.rename(os.path.join(work_dir, 'mesh_out.su2'), os.path.join(work_dir, 'mesh.su2'))

            # Run SU2_GEO to evaluate geometry
            cmd_str = f"mpiexec /path/to/SU2_v7.2.0_Binaries/SU2_GEO {cfg_file}"
            subprocess.run(cmd_str, cwd=work_dir, shell=True)

            # Run the shape optimization
            cmd_str = f"python3 /path/to/SU2_v7.2.0_Binaries/shape_optimization.py -n 48 -g DISCRETE_ADJOINT -f {cfg_file}"
            subprocess.run(cmd_str, cwd=work_dir, shell=True)
        else:
            print(f"Input configuration file '{cfg_file}' not found. Please provide the configuration file.")
            sys.exit(1)  # Exit if configuration file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    main()