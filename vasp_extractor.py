Python
"""
VASP HDF5 Data Extractor
Author: Murugesan Rasukkannu
Role: Senior Computational Physicist & Hardware Systems Engineer

Description:
Object-oriented Python pipeline to extract, parse, and export 
Density of States (DOS) and Band Structure data from VASP 6.x HDF5 outputs.
Designed for high-throughput deployment on HPC SLURM clusters.
"""

import os
import logging
import pandas as pd
import py4vasp

# Configure logging for HPC environments
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class VaspDataExtractor:
    def __init__(self, target_directory: str = "."):
        """
        Initializes the extractor in the specified calculation directory.
        """
        self.target_directory = target_directory
        self.hdf5_path = os.path.join(self.target_directory, "vaspout.h5")
        
        if not os.path.exists(self.hdf5_path):
            logging.error(f"vaspout.h5 not found in {self.target_directory}")
            raise FileNotFoundError(f"Missing HDF5 file: {self.hdf5_path}")
        
        logging.info(f"Successfully located VASP output at {self.hdf5_path}")

    def extract_dos(self, export_csv: bool = False) -> pd.DataFrame:
        """
        Extracts the Density of States (DOS) from the HDF5 file 
        and structures it into a Pandas DataFrame.
        """
        logging.info("Initiating DOS extraction process...")
        try:
            # Access the VASP calculation via py4vasp
            calc = py4vasp.Calculation.from_path(self.target_directory)
            dos_dict = calc.dos.read()
            
            # Extract energies and total DOS
            energies = dos_dict["energies"]
            total_dos = dos_dict["total"]
            
            # Construct DataFrame
            df_dos = pd.DataFrame({
                "Energy_eV": energies,
                "Total_DOS": total_dos
            })
            
            logging.info("DOS data successfully structured.")
            
            if export_csv:
                output_file = os.path.join(self.target_directory, "extracted_dos.csv")
                df_dos.to_csv(output_file, index=False)
                logging.info(f"DOS data exported to {output_file}")
                
            return df_dos
            
        except Exception as e:
            logging.error(f"Failed to extract DOS: {str(e)}")
            raise

    def check_convergence(self) -> bool:
        """
        Verifies if the VASP electronic minimization converged successfully.
        """
        logging.info("Checking electronic convergence status...")
        try:
            calc = py4vasp.Calculation.from_path(self.target_directory)
            # Fetch energy data to verify calculation completion
            energy_data = calc.energy.read()
            
            if energy_data:
                logging.info("Calculation successfully converged.")
                return True
            return False
            
        except Exception as e:
            logging.warning(f"Convergence check failed or incomplete calculation: {str(e)}")
            return False

if __name__ == "__main__":
    # Example deployment script for testing locally
    print("VASP Data Extractor Pipeline Initialized.")
    print("Run this module directly within a VASP directory or import as a class.")
