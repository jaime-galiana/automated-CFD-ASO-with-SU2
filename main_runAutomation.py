"""
Code part of FYP: "Aerodynamic shape optimization of wings with compliant winglets"

Author: Jaime Galiana Herrera
Date: 2024-02-01

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


def modify_script(filename, np, mem, time, cant, sweep):
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
                elif "geometry_generation.py -c" in stripped_line:
                    new_line = f"python3 /rds/general/user/jg2219/ephemeral/Final-try/bin/geometry_generation.py -c {cant} -s {sweep}"
                elif "mesh_generation.py -np" in stripped_line:
                    new_line = f"python3 /rds/general/user/jg2219/ephemeral/Final-try/bin/mesh_generation.py -np {np}"
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

def main(np, mem, time):
    list_cant = [-120, -105, -90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90, 105, 120]
    list_sweep = [-20, -10, 0, 10, 20]

    main_folder = "/path/to/main"
    template_folder = "bin/submit_template.pbs"

    for cant in list_cant:
        for sweep in list_sweep:
            # Change directory to main
            os.chdir(main_folder)

            # Change to output directory
            output_folder = f"output/winglet_c{cant}_s{sweep}"
            create_directory(output_folder)

            # Copy template to output folder
            subprocess.run(['cp', os.path.join(main_folder, template_folder), os.path.join(main_folder, output_folder, "submit.pbs")])

            # Copy winggen.vspscript file
            subprocess.run(['cp', os.path.join(main_folder, "bin/winggen.vspscript"), os.path.join(main_folder, output_folder, "winggen.vspscript")])

            # Copy macro file
            subprocess.run(['cp', os.path.join(main_folder, "bin/macro.java"), os.path.join(main_folder, output_folder, "macro.java")])

            # Copy macro file
            subprocess.run(['cp', os.path.join(main_folder, "bin/Euler-shapeOptimisation.py"), os.path.join(main_folder, output_folder, "Euler-shapeOptimisation.py")])

            # Change directory to output/wing_c{}_s{}
            os.chdir(output_folder)
            modify_script("submit.pbs", np, mem, time, cant, sweep)

            try:
                subprocess.run(["qsub", "submit.pbs"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error executing qsub: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to submit batch jobs')
    parser.add_argument('-np', type=int, help='Number parallel processes')
    parser.add_argument('-mem', type=int, help='Memory of each process')
    parser.add_argument('-time', type=int, help='Job time')

    args = parser.parse_args()

    if args.np is None or args.mem is None or args.time is None:
        parser.error("Please provide both -np, -mem and -time arguments.")

    main(args.np, args.mem, args.time)