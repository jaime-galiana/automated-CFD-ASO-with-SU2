import subprocess
import os
import sys

def main():
    try:
        # Set environment variables
        os.environ['SU2_RUN'] = '/path/to/SU2/Compiled-v8.0.0/bin'
        os.environ['SU2_HOME'] = '/path/to/SU2/Source-v8.0.0'
        os.environ['PATH'] += ':' + os.environ['SU2_RUN']
        os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.environ['SU2_RUN']
        
        # Check and remove existing files
        if os.path.exists('./EULER-shapeOptimisation.cfg'):
            cmd_str = "mpiexec /path/to/SU2/bin/SU2_DEF ./EULER-shapeOptimisation.cfg"
            subprocess.run(cmd_str, shell=True)
            if os.path.exists('mesh.su2'):
                cmd_str = "rm -r mesh.su2"
                subprocess.run(cmd_str, shell=True)  
                
            cmd_str = "mv mesh_out.su2 mesh.su2"
            subprocess.run(cmd_str, shell=True)

            cmd_str = "mpiexec /path/to/SU2/bin/SU2_GEO ./EULER-shapeOptimisation.cfg"
            subprocess.run(cmd_str, shell=True)
            
            cmd_str = "python3 /path/to/SU2/bin/shape_optimization.py -n 48 -g DISCRETE_ADJOINT -f EULER-shapeOptimisation.cfg"
            subprocess.run(cmd_str, shell=True)
        else:
            print("Input file 'mesh.cga' not found. Please provide the mesh file.")
            sys.exit(1)  # Exit with error code 1 if input file is missing

    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)  # Exit with error code 1 if an exception occurs

if __name__ == "__main__":
    main()