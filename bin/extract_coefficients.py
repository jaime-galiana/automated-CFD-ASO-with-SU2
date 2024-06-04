"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-02-01
    Description: Extracts the last Cl and Cd values from simulation output files.
"""

import os
import re

def extract_last_cl_cd(file_path):
    """
    Extracts the last Cl and Cd values from a output SU2 file.

    Parameters:
        file_path (str): Path to the file.

    Returns:
        tuple: Last Cl and Cd values, or (None, None) if not found.
    """
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
                        print(f"Conversion failed for line: {line.strip()}")  # Handle conversion error
                    
    return last_cl, last_cd

def main():
    """
    Main function to traverse directories, extract Cl and Cd values, and save the results.
    """
    base_dir = '/path/to/main/output'
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

