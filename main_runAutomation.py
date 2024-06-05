"""
    FYP: "Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster"

    Author: Jaime Galiana Herrera
    Date: 2024-06-03

    Script for automated generation of wing geometry with OpenVSP, mesh with StarCCM+, CFD simulation on SU2 and ASO on SU2 using discrete-adjoint.

    Input:  -np: number of processors to run in parallel.
            -mem: memory to request to HPC
            -time: walltime to request to HPC
"""

import os
import subprocess
import argparse

def create_directory(path):
    """Creates a directory if it doesn't exist."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory: {path} - {e}")

def normalize_solver_name(solver):
    """Normalizes the solver name to the correct format."""
    solver_mapping = {
        'euler': 'Euler',
        'rans': 'RANS'
    }
    return solver_mapping.get(solver.lower(), solver)

def modify_script(filename, np, mem, time, cant, sweep, steps, workdir):
    """Modifies a script by replacing specific lines with new values."""
    try:
        with open(filename, "r") as file:
            replaced_content = ""
            for line in file:
                stripped_line = line.strip()
                if "#PBS -l walltime=" in stripped_line:
                    new_line = f"#PBS -l walltime={time}:00:00"
                elif "#PBS -l select=1:ncpus=" in stripped_line:
                    new_line = f"#PBS -l select=1:ncpus={np}:mem={mem}gb"
                elif stripped_line.startswith("# Read parameters from environment variables"):
                    new_line = f'GEO={steps["geo"]}\nMESH={steps["mesh"]}\nPRISM_LAYER={steps["prism_layer"]}\nCFD={steps["cfd"]}\nCFD_SOLVER={steps["cfd_solver"]}\nASO={steps["aso"]}\nASO_SOLVER={steps["aso_solver"]}\nWORKDIR={workdir}'
                else:
                    new_line = line
                replaced_content += new_line + "\n"
            file.close()
        with open(filename, "w") as write_file:
            write_file.write(replaced_content)
            write_file.close()
    except FileNotFoundError as e:
        print(f"Error: File not found - {filename} - {e}")
    except Exception as e:
        print(f"Error modifying script: {filename} - {e}")

def main(np, mem, time, steps, list_cant, list_sweep):
    if steps['cfd_solver'] == 'RANS' and steps['prism_layer'] != 1:
        raise ValueError("RANS solver requires the mesh to be generated with a prism layer. Please set -prism-layer to 1.")
    if steps['cfd_solver'] == 'Euler' and steps['prism_layer'] != 0:
        raise ValueError("Euler solver requires the mesh to be generated without a prism layer. Please set -prism-layer to 0.")

    main_folder = "/path/to/main"
    template_folder = "bin/submit_template.pbs"

    for cant in list_cant:
        for sweep in list_sweep:
            # Change directory to main
            os.chdir(main_folder)

            # Change to output directory for the specific configuration
            output_folder = f"output/winglet_c{cant}_s{sweep}"
            create_directory(output_folder)

            # Create subdirectories for each step and solver only when needed
            if steps['geo'] == 1:
                create_directory(os.path.join(output_folder, "GEOMETRY"))
                subprocess.run(['cp', os.path.join(main_folder, "bin/winggen.vspscript"), os.path.join(output_folder, "GEOMETRY", "winggen.vspscript")])
            if steps['mesh'] == 1:
                create_directory(os.path.join(output_folder, "MESH"))
                macro_file = "macro_with_prism.java" if steps['prism_layer'] == 1 else "macro_without_prism.java"
                subprocess.run(['cp', os.path.join(main_folder, "bin", macro_file), os.path.join(output_folder, "MESH", "macro.java")])
            if steps['cfd'] == 1:
                cfd_solver_dir = os.path.join(output_folder, "CFD", steps['cfd_solver'])
                create_directory(cfd_solver_dir)
                subprocess.run(['cp', os.path.join(main_folder, f"bin/{steps['cfd_solver']}-cfd.py"), os.path.join(cfd_solver_dir, f"{steps['cfd_solver']}-cfd.py")])
            if steps['aso'] == 1:
                aso_solver_dir = os.path.join(output_folder, "ASO", steps['aso_solver'])
                create_directory(aso_solver_dir)
                subprocess.run(['cp', os.path.join(main_folder, f"bin/{steps['aso_solver']}-shapeOptimisation.py"), os.path.join(aso_solver_dir, f"{steps['aso_solver']}-shapeOptimisation.py")])

            # Copy template to output folder
            subprocess.run(['cp', os.path.join(main_folder, template_folder), os.path.join(output_folder, "submit.pbs")])

            # Change directory to output/winglet_c{cant}_s{sweep}
            os.chdir(output_folder)
            modify_script("submit.pbs", np, mem, time, cant, sweep, steps, output_folder)

            try:
                subprocess.run(["qsub", "submit.pbs"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error executing qsub: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to submit batch jobs')
    parser.add_argument('-np', type=int, help='Number of parallel processes')
    parser.add_argument('-mem', type=int, help='Memory of each process in GB')
    parser.add_argument('-time', type=int, help='Job time in hours')
    parser.add_argument('-geo', type=int, choices=[0, 1], help='Run geometry generation (0: No, 1: Yes)')
    parser.add_argument('-mesh', type=int, choices=[0, 1], help='Run mesh generation (0: No, 1: Yes)')
    parser.add_argument('-prism-layer', type=int, choices=[0, 1], help='Include prism layer in mesh (0: No, 1: Yes)')
    parser.add_argument('-cfd', type=int, choices=[0, 1], help='Run CFD (0: No, 1: Yes)')
    parser.add_argument('-cfd-solver', type=str, help='CFD Solver to use (Euler or RANS)')
    parser.add_argument('-aso', type=int, choices=[0, 1], help='Run ASO (0: No, 1: Yes)')
    parser.add_argument('-aso-solver', type=str, help='ASO Solver to use (Euler or RANS)')
    parser.add_argument('-cant-list', nargs='+', type=int, help='List of cant angles to test')
    parser.add_argument('-sweep-list', nargs='+', type=int, help='List of sweep angles to test')

    args = parser.parse_args()

    if args.np is None or args.mem is None or args.time is None:
        parser.error("Please provide -np, -mem, and -time arguments.")

    # Normalize solver names
    if args.cfd_solver:
        args.cfd_solver = normalize_solver_name(args.cfd_solver)
    if args.aso_solver:
        args.aso_solver = normalize_solver_name(args.aso_solver)

    steps = {
        'geo': args.geo,
        'mesh': args.mesh,
        'prism_layer': args.prism_layer,
        'cfd': args.cfd,
        'cfd_solver': args.cfd_solver,
        'aso': args.aso,
        'aso_solver': args.aso_solver
    }

    main(args.np, args.mem, args.time, steps, args.cant_list, args.sweep_list)