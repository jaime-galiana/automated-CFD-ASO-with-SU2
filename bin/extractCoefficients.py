
    #  Author: Jaime Galiana Herrera
    #  Date: 2024-05-01
    #  Script that extracts the aerodynamic coefficients from simulation. To be run in HPC.
    #  Inputs from PBS file:


import os
import re

def extract_last_cl_cd(file_path):
    last_cl = None
    last_cd = None

    with open(file_path, 'r') as file:
        for line in file:
            if re.match(r'\|\s*\d+\s*\|', line):
                parts = line.split('|')
                if len(parts) > 4:
                    try:
                        last_cl = float(parts[4].strip())
                        last_cd = float(parts[5].strip())
                    except ValueError:
                        # Handle cases where conversion to float fails
                        print(f"Conversion failed for line: {line.strip()}")
                    
    return last_cl, last_cd
def main():
    base_dir = '/rds/general/user/jg2219/ephemeral/Final-try/output'
    list_cant = [-120, -105, -90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90, 105, 120]
    list_sweep = [-20, -10, 0, 10, 20]

    results = []

    for cant in list_cant:
        for sweep in list_sweep:
            winglet_dir = f'winglet_c{cant}_s{sweep}'
            full_dir_path = os.path.join(base_dir, winglet_dir)

            if os.path.exists(full_dir_path):
                for root, dirs, files in os.walk(full_dir_path):
                    for file in files:
                        if file.startswith('submit.pbs.o'):
                            file_path = os.path.join(root, file)
                            cl, cd = extract_last_cl_cd(file_path)
                            results.append((cant, sweep, cl, cd))

    with open('results.dat', 'w') as output_file:
        for result in results:
            output_file.write(f"{result[0]} {result[1]} {result[2]} {result[3]}\n")

    print("Results saved to results.dat")

if __name__ == "__main__":
    main()