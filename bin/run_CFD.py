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
import math
import vtk
from vtk.util.numpy_support import vtk_to_numpy

def read_vtu(file_path):
    """
    Reads the VTU file and extracts the y+ values.
    """
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_path)
    reader.Update()
    output = reader.GetOutput()
    yplus = output.GetPointData().GetArray("Y_Plus")
    yp = vtk_to_numpy(yplus)
    return max(yp)

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

def run_cfd(solver, directory):
    """
    Main function to set up and run SU2 CFD simulation.
    """
    try:
        # Set environment variables for SU2
        os.environ['SU2_RUN'] = '/path/to/SU2/Compiled-v7.2.0/bin'
        os.environ['SU2_HOME'] = '/path/to/SU2/Source-v7.2.0'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']

        # Define the working directory
        work_dir = os.path.join(directory, 'CFD', solver)
        os.makedirs(work_dir, exist_ok=True)

        # Remove existing flow output file if it exists in the working directory
        flow_output = os.path.join(work_dir, 'flow_winglet.vtu')
        if os.path.exists(flow_output):
            os.remove(flow_output)

        # Check for input mesh file in the MESH directory
        mesh_file = os.path.join(directory, 'MESH', 'mesh.cga')
        if not os.path.exists(mesh_file):
            print(f"Input mesh file '{mesh_file}' not found. Please generate the mesh first.")
            sys.exit(1)  # Exit if input file is missing

        # Copy the mesh file to the working directory
        subprocess.run(['cp', mesh_file, work_dir])

        # Determine the configuration file based on the solver type
        cfg_file = os.path.join(directory, 'CFD', solver, f'{solver.lower()}-cfd.py')

        # Run SU2_CFD with the chosen configuration file
        cmd_str = f"mpiexec /path/to/SU2/Compiled-v7.2.0/bin/SU2_CFD {cfg_file}"
        subprocess.run(cmd_str, cwd=work_dir, shell=True)

        # Wait until the flow file is generated
        while not os.path.exists(flow_output):
            pass

        # If the solver is RANS, check y+ values and iterate if necessary
        if solver == 'RANS':
            while True:
                # Read the maximum y+ value from the flow output
                max_yplus = read_vtu(flow_output)

                if max_yplus < 1:
                    print("Simulations complete with acceptable y+ value.")
                    break
                else:
                    print("Y+ > 1 ... Re-calculating prism layer...")
                    update_prism_layer(os.path.join(directory, 'MESH', 'macro_with_prism.java'), max_yplus)

                    # Remove existing mesh files
                    if os.path.exists(mesh_file):
                        os.remove(mesh_file)
                    if os.path.exists('./star@meshed.sim'):
                        os.remove('./star@meshed.sim')

                    # Regenerate the mesh
                    cmd_str = f"python3 {os.path.join(directory, 'MESH', 'mesh_generation.py')} -np 8 -i {os.path.join(directory, 'GEOMETRY')} -o {os.path.join(directory, 'MESH')} -pl 1 -my {max_yplus}"
                    subprocess.run(cmd_str, shell=True)

                    # Rerun the CFD simulation
                    cmd_str = f"mpiexec /path/to/SU2/Compiled-v7.2.0/bin/SU2_CFD {cfg_file}"
                    subprocess.run(cmd_str, cwd=work_dir, shell=True)

                    # Wait until the flow file is generated
                    while not os.path.exists(flow_output):
                        pass

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run SU2 CFD simulation with either Euler or RANS solver.')
    parser.add_argument('solver', choices=['Euler', 'RANS'], help='Choose the solver type: Euler or RANS')
    parser.add_argument('directory', help='Directory to run the simulation in')

    args = parser.parse_args()
    run_cfd(args.solver, args.directory)