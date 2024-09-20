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
import math

def update_prism_layer(macro_path, max_yplus):
    """
    Updates the prism layer configuration in the macro file based on the max y+ value.
    """
    with open(macro_path, "r") as file:
        content = file.readlines()

    current_near_wall = None
    for line in content:
        if "PrismWallThickness.class).setValue" in line.strip():
            line = line.strip()
            line = line.strip("autoMeshOperation_0.getDefaultValues().get(PrismWallThickness.class).setValue(")
            line = line.strip(");")
            current_near_wall = float(line)
            break

    if current_near_wall is None:
        raise ValueError("PrismWallThickness.class).setValue not found in macro file.")

    new_near_wall = current_near_wall / (max_yplus * 1.1)
    num_prism_layers = math.ceil((math.log(1 + (0.2 * 0.01 / new_near_wall)) / math.log(1.2)))

    new_content = []
    for line in content:
        if "PrismWallThickness.class).setValue" in line.strip():
            new_line = "autoMeshOperation_0.getDefaultValues().get(PrismWallThickness.class).setValue({0});".format(str(new_near_wall))
            new_content.append(new_line + "\n")
        elif "integerValue_0.getQuantity().setValue" in line.strip():
            new_line = "integerValue_0.getQuantity().setValue({0});".format(str(num_prism_layers))
            new_content.append(new_line + "\n")
        else:
            new_content.append(line)

    with open(macro_path, "w") as file:
        file.writelines(new_content)

def main(np, input_dir, output_dir, prism_layer, max_yplus=None):
    """
    Main function to set up and run the meshing process with STAR-CCM+.

    Parameters:
    np (int): Number of processes to run in parallel.
    input_dir (str): Directory containing the input files.
    output_dir (str): Directory to save the output files.
    prism_layer (int): Whether to include prism layer (0: No, 1: Yes).
    max_yplus (float, optional): Maximum y+ value to adjust the prism layer.
    """
    try:
        mesh_subdir = "with_prism" if prism_layer == 1 else "without_prism"
        output_dir = os.path.join(output_dir, mesh_subdir)
        
        os.chdir(output_dir)

        # Remove existing files if they exist
        if os.path.exists('./mesh.cga'):
            os.remove('./mesh.cga')

        if os.path.exists('./star@meshed.sim'):
            os.remove('./star@meshed.sim')

        # Check for required input STEP files
        wing_file = os.path.join(input_dir, 'wing.stp')
        domain_file = os.path.join(output_dir, 'domain.stp')

        if not os.path.exists(wing_file):
            print(f"Input file '{wing_file}' not found. Please run the geometry generation step first.")
            sys.exit(1)  # Exit if wing.stp file is missing

        if not os.path.exists(domain_file):
            print(f"Input file '{domain_file}' not found. Please provide the domain.stp file in the MESH directory.")
            sys.exit(1)  # Exit if domain.stp file is missing

        # Copy the wing.stp file to the output directory
        subprocess.run(['cp', wing_file, output_dir])

        # Select the appropriate macro file based on prism layer configuration
        macro_file = "macro_with_prism.java" if prism_layer == 1 else "macro_without_prism.java"
        macro_path = os.path.join(output_dir, macro_file)

        # Check if the correct macro file exists
        if prism_layer == 1 and not os.path.exists(macro_path):
            print(f"Required macro file for prism layer '{macro_path}' not found.")
            sys.exit(1)  # Exit if macro file is missing for prism layer
        elif prism_layer == 0 and not os.path.exists(macro_path):
            print(f"Required macro file without prism layer '{macro_path}' not found.")
            sys.exit(1)  # Exit if macro file is missing for no prism layer

        # Update the prism layer if max_yplus is provided
        if max_yplus and prism_layer == 1:
            update_prism_layer(macro_path, max_yplus)

        # Run STAR-CCM+ command
        cmd_str = f"starccm+ -batch {macro_path} -power -podkey KEY -licpath 1999@flex.cd-adapco.com -np {np}"
        subprocess.run(cmd_str, shell=True)

        # Wait until the mesh file is generated
        while not os.path.exists('./mesh.cga'):
            pass

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Number of cores to run in parallel')
    parser.add_argument('-np', type=int, help='Number of processes')
    parser.add_argument('-i', '--input', type=str, help='Input directory', default='.')
    parser.add_argument('-o', '--output', type=str, help='Output directory', default='.')
    parser.add_argument('-pl', '--prism-layer', type=int, choices=[0, 1], help='Include prism layer in mesh (0: No, 1: Yes)', default=0)
    parser.add_argument('-my', '--max-yplus', type=float, help='Maximum y+ value to adjust the prism layer', default=None)
    args = parser.parse_args()

    if args.np is None:
        parser.error("Please provide an integer as number of processes to run in parallel")

    main(args.np, args.input, args.output, args.prism_layer, args.max_yplus)