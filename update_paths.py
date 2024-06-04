"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-06-03
    Description: Updates all the paths required to run this project. This includes:
                - path to your main folder in HPC where the project is located
                - path to OpenVSP v3.37.0 Compiled
                - path to SU2 v7.2.0 Source files
                - path to SU2 v7.2.0 Compiled binaries
                - path to SU2 v8.0.0 Source files
                - path to SU2 v8.0.0 Compiled binaries
"""

import os
import argparse

def replace_path_in_file(file_path, old_paths, new_paths):
    """
    Replace paths in a file.
    
    Parameters:
    file_path (str): Path to the file.
    old_paths (list of str): List of paths to be replaced (default or previously updated).
    new_paths (list of str): List of new paths to replace the old ones.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    updated_content = content
    for old_path, new_path in zip(old_paths, new_paths):
        if old_path in content:
            updated_content = updated_content.replace(old_path, new_path)
        else:
            print(f"Warning: '{old_path}' not found in {file_path}. Skipping replacement for this path.")
    
    if content != updated_content:
        with open(file_path, 'w') as file:
            file.write(updated_content)
        print(f"Updated paths in {file_path}")
    else:
        print(f"No paths updated in {file_path}. Please check if the paths are correct.")

def replace_key_in_file(file_path, placeholder_key, actual_key):
    """
    Replace the placeholder KEY in a file with the actual KEY.
    
    Parameters:
    file_path (str): Path to the file.
    placeholder_key (str): Placeholder key to be replaced.
    actual_key (str): Actual key to replace the placeholder.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    if placeholder_key in content:
        content = content.replace(placeholder_key, actual_key)
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Updated KEY in {file_path}")
    else:
        print(f"Warning: Placeholder KEY not found in {file_path}. No replacement made.")

def update_paths_in_files(directory, files_to_modify, old_paths, new_paths, key_placeholder=None, actual_key=None):
    """
    Update paths in specific Python files within a directory.

    Parameters:
    directory (str): Directory to search for Python files.
    files_to_modify (list of str): List of specific files to modify.
    old_paths (list of str): List of paths to be replaced (default or previously updated).
    new_paths (list of str): List of new paths to replace the old ones.
    key_placeholder (str, optional): Placeholder key to be replaced in mesh_generation.py.
    actual_key (str, optional): Actual key to replace the placeholder.
    """
    for file in files_to_modify:
        file_path = os.path.join(directory, file)
        if os.path.exists(file_path):
            replace_path_in_file(file_path, old_paths, new_paths)
        else:
            print(f"Warning: File {file_path} does not exist.")

    # Special handling for the mesh_generation.py file if key replacement is needed
    if key_placeholder and actual_key:
        mesh_gen_file = os.path.join(directory, 'bin/mesh_generation.py')
        if os.path.exists(mesh_gen_file):
            replace_key_in_file(mesh_gen_file, key_placeholder, actual_key)
        else:
            print(f"Warning: File {mesh_gen_file} does not exist.")

def main():
    parser = argparse.ArgumentParser(description="Update paths in specific Python files.")
    parser.add_argument('directory', type=str, help="Directory where the project is located")
    parser.add_argument('--main', type=str, help="New path to your main folder in HPC")
    parser.add_argument('--openvsp', type=str, help="New path to OpenVSP v3.37.0 Compiled")
    parser.add_argument('--su2_v72_src', type=str, help="New path to SU2 v7.2.0 Source files")
    parser.add_argument('--su2_v72_bin', type=str, help="New path to SU2 v7.2.0 Compiled binaries")
    parser.add_argument('--su2_v80_src', type=str, help="New path to SU2 v8.0.0 Source files")
    parser.add_argument('--su2_v80_bin', type=str, help="New path to SU2 v8.0.0 Compiled binaries")
    parser.add_argument('--output', type=str, help="New path to main/output/")
    parser.add_argument('--key', type=str, help="Actual key to replace the placeholder")
    args = parser.parse_args()

    files_to_modify = [
        'main_runAutomation.py',
        'bin/geometry_generation.py',
        'bin/run_CFD.py',
        'bin/run_ASO.py',
        'bin/extract_coefficients.py'
    ]
    
    default_paths = [
        'path/to/main',
        'path/to/OpenVSP_v3.37.0_Compiled',
        'path/to/SU2_v7.2.0_Source',
        'path/to/SU2_v7.2.0_Binaries',
        'path/to/SU2_v8.0.0_Source',
        'path/to/SU2_v8.0.0_Binaries',
        'path/to/main/output'
    ]
    
    new_paths = [
        args.main if args.main else 'path/to/main',
        args.openvsp if args.openvsp else 'path/to/OpenVSP_v3.37.0_Compiled',
        args.su2_v72_src if args.su2_v72_src else 'path/to/SU2_v7.2.0_Source',
        args.su2_v72_bin if args.su2_v72_bin else 'path/to/SU2_v7.2.0_Binaries',
        args.su2_v80_src if args.su2_v80_src else 'path/to/SU2_v8.0.0_Source',
        args.su2_v80_bin if args.su2_v80_bin else 'path/to/SU2_v8.0.0_Binaries',
        args.output if args.output else 'path/to/main/output'
    ]
    
    # Filter out unchanged paths to minimize unnecessary replacements
    old_paths = [default_path for default_path, new_path in zip(default_paths, new_paths) if new_path != default_path]
    paths_to_replace = [new_path for new_path in new_paths if new_path not in default_paths]

    update_paths_in_files(args.directory, files_to_modify, old_paths, paths_to_replace, 'KEY', args.key if args.key else None)

if __name__ == "__main__":
    main()