#Script for the automation of mesh generation on Star-CCM+ designed to run on the Imperial College London RCS HPC system

import subprocess
import os
import sys
import argparse

def main(np):
    try:
        # Check and remove existing files
        if os.path.exists('./mesh.cga'):
            os.remove('./mesh.cga')

        if os.path.exists('./star@meshed.sim'):
            os.remove('./star@meshed.sim')

        # Check if input file exists
        if os.path.exists('./wing.stp'):
            print("Meshing... ")
            # Run STAR-CCM+ command
            cmd_str = "starccm+ -batch ./macro.java -power -podkey dKplKc2NAEVUlBALKVUwPA -licpath 1999@flex.cd-adapco.com -np {0}".format(np)
            subprocess.run(cmd_str, shell=True)

            # Check if mesh file is generated
            while not os.path.exists('./mesh.cga'):
                pass  # Wait until the mesh file is generated

        else:
            print("Input file 'wing.stp' not found. Please provide the input file.")
            sys.exit(1)  # Exit with error code 1 if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit with error code 1 if an exception occurs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Number of cores to run in parallel')
    parser.add_argument('-np', type=int, help='Number of processes')
    args = parser.parse_args()

    if args.np is None:
        parser.error("Please provide an integer as number of processes to run in parallel")

    main(args.np)