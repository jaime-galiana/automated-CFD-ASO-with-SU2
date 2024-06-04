"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-02-01
    Description: Automates the execution of SU2 shape optimization process.
"""

import subprocess
import os
import sys

def main():
    """
    Main function to set up and run SU2 shape optimization.
    """
    try:
        # Set environment variables for SU2
        os.environ['SU2_RUN'] = '/path/to/SU2/Compiled-v8.0.0/bin'
        os.environ['SU2_HOME'] = '/path/to/SU2/Source-v8.0.0'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']
        
        # Check for configuration file
        if os.path.exists('./EULER-shapeOptimisation.cfg'):
            # Run SU2_DEF to preprocess the configuration, transform CGNS mesh to SU2 mesh. Set up FFD box.
            cmd_str = "mpiexec /path/to/SU2/bin/SU2_DEF ./EULER-shapeOptimisation.cfg"
            subprocess.run(cmd_str, shell=True)
            
            # Remove existing mesh file
            if os.path.exists('mesh.su2'):
                subprocess.run("rm -r mesh.su2", shell=True)  
                
            # Rename the output mesh
            subprocess.run("mv mesh_out.su2 mesh.su2", shell=True)

            # Run SU2_GEO to evaluate geometry
            cmd_str = "mpiexec /path/to/SU2/bin/SU2_GEO ./EULER-shapeOptimisation.cfg"
            subprocess.run(cmd_str, shell=True)
            
            # Run the shape optimization
            cmd_str = "python3 /path/to/SU2/bin/shape_optimization.py -n 48 -g DISCRETE_ADJOINT -f EULER-shapeOptimisation.cfg"
            subprocess.run(cmd_str, shell=True)
        else:
            print("Input file 'EULER-shapeOptimisation.cfg' not found. Please provide the configuration file.")
            sys.exit(1)  # Exit if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit if an exception occurs

if __name__ == "__main__":
    main()