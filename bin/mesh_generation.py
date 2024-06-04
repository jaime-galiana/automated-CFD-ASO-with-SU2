"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-06-03
    Description: Automates the meshing process using STAR-CCM+. 
"""

import subprocess
import os
import sys
import argparse

def main(np, input_dir, output_dir):
    """
    Main function to set up and run the meshing process with STAR-CCM+.

    Parameters:
    np (int): Number of processes to run in parallel.
    """
    try:
        os.chdir(output_dir)

        # Remove existing files if they exist
        if os.path.exists('./mesh.cga'):
            os.remove('./mesh.cga')

        if os.path.exists('./star@meshed.sim'):
            os.remove('./star@meshed.sim')

        # Check for input STEP file
        input_file = os.path.join(input_dir, 'wing.stp')
        if os.path.exists(input_file):
            # Run STAR-CCM+ command
            cmd_str = f"starccm+ -batch ./macro.java -power -podkey KEY -licpath 1999@flex.cd-adapco.com -np {np}"
            subprocess.run(cmd_str, shell=True)

            # Wait until the mesh file is generated
            while not os.path.exists('./mesh.cga'):
                pass
        else:
            print(f"Input file '{input_file}' not found. Please provide the input file.")
            sys.exit(1)  # Exit if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Number of cores to run in parallel')
    parser.add_argument('-np', type=int, help='Number of processes')
    parser.add_argument('-i', '--input', type=str, help='Input directory', default='.')
    parser.add_argument('-o', '--output', type=str, help='Output directory', default='.')
    args = parser.parse_args()

    if args.np is None:
        parser.error("Please provide an integer as number of processes to run in parallel")

    main(args.np, args.input, args.output)