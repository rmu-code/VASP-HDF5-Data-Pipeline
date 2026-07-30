# VASP-HDF5-Data-Pipeline
# VASP HDF5 Data Extractor & Automation Pipeline

## Overview
This repository contains a high-throughput Python pipeline designed to automate the extraction and processing of Density Functional Theory (DFT) data from VASP (Vienna Ab initio Simulation Package) outputs. 

Historically, parsing `vasprun.xml` or raw VASP outputs was a significant bottleneck in computational materials science. This pipeline leverages `py4vasp` and `pandas` to interface directly with VASP 6.x `vaspout.h5` files, enabling rapid extraction of Band Structures and Density of States (DOS) for large-scale HPC job arrays.

## Core Features
* **HDF5 Integration:** Reads directly from `vaspout.h5` for fast, memory-efficient data loading.
* **Automated Data Structuring:** Converts complex quantum mechanical arrays into clean, analyzable `pandas` DataFrames.
* **Robust Error Handling:** Built-in logging and exception handling for deployment on remote SLURM clusters.
* **Scalability:** Designed to be executed iteratively over hundreds of directories in high-throughput screening workflows.

## Prerequisites
Ensure you have Python 3.8+ installed. The required dependencies are listed in `requirements.txt`.

## Usage
To execute the pipeline locally or on a supercomputing node, define the target directory containing your `vaspout.h5` file and run the extractor:

```python
from vasp_extractor import VaspDataExtractor

# Initialize the pipeline
extractor = VaspDataExtractor(target_directory="/path/to/calc")

# Extract Density of States (DOS) to a CSV format
dos_dataframe = extractor.extract_dos(export_csv=True)



# HPC SLURM Automation for VASP 6.x

## Overview
This repository contains a production-ready Bash scripting architecture for deploying GPU-accelerated VASP (Vienna Ab initio Simulation Package) calculations on enterprise/national supercomputing clusters (e.g., Norwegian Sigma2/Betzy or EuroHPC LUMI).

## Architecture Highlights
* **GPU Scaling:** Configured for Multi-Node, Multi-GPU (NVIDIA A100) architecture using OpenACC-enabled VASP binaries to reduce HSE06 hybrid functional calculation times by up to 10x.
* **Memory Management:** Hard-coded RAM limits (`--mem=256G`) and optimized thread binding (`OMP_NUM_THREADS=1`) to prevent node-level Out-Of-Memory (OOM) crashes during heavy wavefunction iterations.
* **Automated CI/CD-style Pipeline:** The bash script doesn't just run the physics simulation. It actively parses the output file for convergence verification, and if successful, automatically triggers a Python-based post-processing toolkit to extract data and plot publication-ready graphics.

## Deployment
Submit the job to the SLURM workload manager using:
```bash
sbatch vasp_sigma2_gpu_submit.sh
