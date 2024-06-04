<p align="center">
  <img src="images/ImperialNewLogo.jpg" alt="Imperial Logo" width="500"/>
</p>

# Automated Workflow for Geometry Generation, Mesh Generation, CFD Simulation, and ASO

**Author**: Jaime Galiana Herrera

**Final-Year Project** in fulfillment of MEng Aeronautics with Spacecraft Engineering

**To be run on Imperial HPC**


## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Preparing the Environment](#step-1-preparing-the-environment)
4. [Running the Automation Script](#step-2-running-the-automation-script)
   - [Command-Line Arguments](#command-line-arguments)
   - [Example Command](#example-command)
5. [Understanding the Workflow](#step-3-understanding-the-workflow)
6. [Usage Notes](#usage-notes)
7. [License](#license)

## Overview

This workflow automates the following steps:

1. **Geometry Generation**: Creating the geometry of the winglet.
2. **Mesh Generation**: Generating the computational mesh with or without a prism layer.
3. **CFD Simulation**: Running the Computational Fluid Dynamics (CFD) simulation to analyze the flow.
4. **ASO**: Running the Aerodynamic Shape Optimization based on CFD results.

<p align="center">
  <img src="images/flowchart.jpg" alt="Winglet design process" width="800"/>
</p>

## Prerequisites

Ensure all required modules are installed and available in your environment. This includes tools like:
- [OpenMPI](https://www.open-mpi.org/)
- [STAR-CCM+](https://mdx.plm.automation.siemens.com/star-ccm-plus) (v16.04.012-R8)
- [Anaconda](https://www.anaconda.com/products/distribution)
- [SU2](https://su2code.github.io/) (v7.2.0 and v8.0.0)S
- [OpenVSP](http://openvsp.org/) (v3.37.0)

## Step 1: Preparing the Environment

Ensure you have all the necessary input files:
- `winggen.vspscript` for geometry generation.
- `macro_with_prism.java` and `macro_without_prism.java` for mesh generation.
- `Euler-cfd.py` and `RANS-cfd.py` for CFD simulation.
- `Euler-shapeOptimisation.py` and `RANS-shapeOptimisation.py` for ASO.

## Step 2: Running the Automation Script

Use the `main_runAutomation.py` script to set up and submit the job. This script takes various arguments to control which steps to run and their configurations.

### Command-Line Arguments:

| Argument       | Description                                 |
|----------------|---------------------------------------------|
| `-np`          | Number of parallel processes                |
| `-mem`         | Total memory of the process                 |
| `-time`        | Job time in hours                           |
| `-geo`         | Run geometry generation (0: No, 1: Yes)     |
| `-mesh`        | Run mesh generation (0: No, 1: Yes)         |
| `-prism-layer` | Include prism layer in mesh (0: No, 1: Yes) |
| `-cfd`         | Run CFD (0: No, 1: Yes)                     |
| `-cfd-solver`  | CFD Solver to use (`Euler` or `RANS`)       |
| `-aso`         | Run ASO (0: No, 1: Yes)                     |
| `-aso-solver`  | ASO Solver to use (`Euler` or `RANS`)       |

### Example Command:
```sh
python3 main_runAutomation.py -np 8 -mem 32 -time 8 -geo 1 -mesh 1 -prism-layer 0 -cfd 1 -cfd-solver euler -aso 1 -aso-solver euler
```

## Step 3: Understanding the Workflow

1. Setting Up Directories

- The `main_runAutomation.py` script creates directories for each winglet configuration and for each step (`GEOMETRY`, `MESH`, `CFD`, `ASO`).

2. Modifying the PBS Script

- The `main_runAutomation.py` script modifies the `submit_template.pbs` script to include the correct parameters and paths based on the user's input.

3. Submitting the Job

- The modified `submit_template.pbs` script is submitted to the job scheduler (qsub).

4. Running Geometry Generation

- If geometry generation is enabled (-geo 1), the winggen.vspscript file is used to generate the geometry.

5. Running Mesh Generation

- If mesh generation is enabled (-mesh 1), the mesh_generation.py script is invoked.
- The prism_layer argument determines whether the mesh includes a prism layer.
- For the RANS solver, the script iterates to adjust the prism layer based on y+ values.

6. Running CFD Simulation

- If CFD is enabled (`-cfd 1`), the run_CFD.py script runs the CFD simulation.
- For the RANS solver, the script checks y+ values and iterates mesh generation if necessary.

7. Running ASO

- If ASO is enabled (`-aso 1`), the `run_ASO.py` script runs the shape optimization based on CFD results.

## Usage Notes

- Use the `main_runAutomation.py´ script to set up and submit the job.
- Ensure the correct directories and input files are in place.
- The `run_CFD.py` script includes an iterative process to adjust the mesh if the y+ values are too high, but this only applies to the RANS solver.
- Each script has specific roles and works together to complete the full workflow.

## License

This project is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License. You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

The licensor cannot revoke these freedoms as long as you follow the license terms.

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **NonCommercial** — You may not use the material for commercial purposes.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

View the full license at: [http://creativecommons.org/licenses/by-nc/4.0/](http://creativecommons.org/licenses/by-nc/4.0/)