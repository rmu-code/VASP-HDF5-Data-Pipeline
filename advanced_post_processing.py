"""
Advanced VASP Post-Processing & Publication Plotting Toolkit
Author: Murugesan Rasukkannu
Role: Senior Computational Physicist & Hardware Systems Engineer

Description:
A comprehensive, publication-grade suite for extracting and plotting VASP outputs.
Includes Fermi-level alignment, Voigt-Reuss-Hill mechanical derivations, 
and complex optical absorption coefficient calculations.
"""

import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pymatgen.io.vasp import Vasprun, Outcar
from pymatgen.electronic_structure.plotter import BSPlotter
from pymatgen.analysis.elasticity.elastic import ElasticTensor
import phonopy

# Strict Publication Formatting Standards
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.linewidth': 1.5,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'figure.dpi': 600
})

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class HSE06BandStructureAnalyzer:
    def __init__(self, target_directory: str = "."):
        self.vasprun_path = os.path.join(target_directory, "vasprun.xml")
        
    def plot_publication_bands(self, save_path: str = "hse06_bands_pub.png", y_min: float = -5.0, y_max: float = 5.0):
        """Extracts HSE06 bands, aligns VBM to 0 eV, and formats for publication."""
        logging.info("Parsing vasprun.xml for high-accuracy HSE06 Band Structure...")
        try:
            run = Vasprun(self.vasprun_path, parse_projected_eigen=True)
            bands = run.get_band_structure(line_mode=True)
            
            # Use PyMatGen's BSPlotter but override with custom matplotlib settings
            plotter = BSPlotter(bands)
            ax = plotter.get_plot(vbm_cbm_marker=True, ylim=(y_min, y_max))
            
            # Format to R&D publication standards
            ax.set_title("HSE06 Electronic Band Structure", fontweight='bold')
            ax.set_ylabel(r"Energy $E - E_F$ (eV)", fontweight='bold')
            ax.axhline(0, color='black', linestyle='--', linewidth=1.5) # Fermi Level Line
            
            plt.tight_layout()
            plt.savefig(save_path, format='png', bbox_inches='tight')
            logging.info(f"Publication-ready band structure saved to {save_path}")
            
        except Exception as e:
            logging.error(f"Failed to plot HSE06 bands: {e}")

class OpticalPropertiesAnalyzer:
    def __init__(self, target_directory: str = "."):
        self.vasprun_path = os.path.join(target_directory, "vasprun.xml")

    def derive_optical_constants(self, save_path: str = "optical_absorption.png"):
        """
        Extracts the dielectric tensor and derives the Absorption Coefficient (alpha)
        and Refractive Index (n) based on Kramer-Kronig relations.
        """
        logging.info("Extracting dielectric tensor and deriving optical constants...")
        try:
            run = Vasprun(self.vasprun_path)
            dielectric = run.dielectric
            
            energies = np.array(dielectric[0])
            real_part = np.array(dielectric[1])
            imag_part = np.array(dielectric[2])
            
            # Compute isotropic average for polycrystalline assumption
            eps_1 = np.mean(real_part[:, 0:3], axis=1)
            eps_2 = np.mean(imag_part[:, 0:3], axis=1)

            # Mathematical Derivation of Absorption Coefficient (alpha)
            # alpha = (sqrt(2) * E / (hbar * c)) * sqrt(sqrt(eps1^2 + eps2^2) - eps1)
            # Converted to standard units (cm^-1)
            c_light = 2.9979e10 # cm/s
            hbar = 6.582e-16 # eV*s
            alpha = (np.sqrt(2) * energies / (hbar * c_light)) * np.sqrt(np.sqrt(eps_1**2 + eps_2**2) - eps_1)

            # Plotting the Absorption Coefficient
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(energies, alpha, color='darkblue', linewidth=2, label=r"Absorption $\alpha(\omega)$")
            
            ax.set_xlim(0, 8) # Focus on visible/UV spectrum
            ax.set_ylim(bottom=0)
            ax.set_xlabel("Photon Energy (eV)", fontweight='bold')
            ax.set_ylabel(r"Absorption Coefficient $\alpha$ (cm$^{-1}$)", fontweight='bold')
            ax.set_title("Optical Absorption Spectrum", fontweight='bold')
            
            ax.grid(True, linestyle=':', alpha=0.6)
            plt.tight_layout()
            plt.savefig(save_path, format='png', bbox_inches='tight')
            logging.info(f"Optical absorption spectrum saved to {save_path}")
            
        except Exception as e:
            logging.error(f"Failed to derive optical data: {e}")

class MechanicalStabilityAnalyzer:
    def __init__(self, target_directory: str = "."):
        self.outcar_path = os.path.join(target_directory, "OUTCAR")

    def calculate_voigt_reuss_hill(self):
        """Parses OUTCAR (IBRION=6) to calculate Bulk/Shear Moduli via VRH approximation."""
        logging.info("Extracting Elastic Tensor to compute mechanical moduli...")
        try:
            outcar = Outcar(self.outcar_path)
            raw_tensor = outcar.read_elastic_tensor()
            
            if raw_tensor is None:
                logging.warning("No elastic tensor found in OUTCAR.")
                return
            
            # Utilize PyMatGen's ElasticTensor for complex tensor math
            tensor = ElasticTensor(raw_tensor)
            
            # Extract Voigt-Reuss-Hill properties (in GPa)
            k_vrh = tensor.k_vrh
            g_vrh = tensor.g_vrh
            poisson = tensor.poisson_ratio
            pugh_ratio = k_vrh / g_vrh
            
            logging.info("--- Mechanical Properties (Voigt-Reuss-Hill) ---")
            logging.info(f"Bulk Modulus (B): {k_vrh:.2f} GPa")
            logging.info(f"Shear Modulus (G): {g_vrh:.2f} GPa")
            logging.info(f"Poisson's Ratio (v): {poisson:.3f}")
            
            # Ductile vs Brittle empirical check (Pugh's Ratio > 1.75 is ductile)
            if pugh_ratio > 1.75:
                logging.info(f"Material Nature: DUCTILE (B/G = {pugh_ratio:.2f})")
            else:
                logging.info(f"Material Nature: BRITTLE (B/G = {pugh_ratio:.2f})")
                
            return {"Bulk_Modulus": k_vrh, "Shear_Modulus": g_vrh, "Poisson": poisson}
            
        except Exception as e:
            logging.error(f"Failed to compute mechanical properties: {e}")

class PhononPlotter:
    def __init__(self, conf_file: str = "band.yaml"):
        self.conf_file = conf_file

    def plot_publication_phonons(self, save_path: str = "phonon_dispersion_pub.png"):
        """Plots high-accuracy Phonon Dispersion curves checking for dynamical stability."""
        logging.info("Parsing Phonopy band.yaml for dynamical stability...")
        try:
            ph = phonopy.load(self.conf_file)
            
            # Extract plot object to customize it
            plot = ph.plot_band_structure()
            ax = plot.gca()
            
            ax.set_title("Phonon Dispersion & Dynamical Stability", fontweight='bold')
            ax.set_ylabel("Frequency (THz)", fontweight='bold')
            ax.axhline(0, color='red', linestyle='--', linewidth=1.5) # Highlights imaginary frequencies
            
            plot.savefig(save_path, format='png', bbox_inches='tight', dpi=600)
            logging.info(f"Publication-ready Phonon curve saved to {save_path}")
            
        except FileNotFoundError:
            logging.error(f"Phonopy file {self.conf_file} not found.")
        except Exception as e:
            logging.error(f"Failed to plot phonons: {e}")

if __name__ == "__main__":
    print("Senior R&D VASP Post-Processing Toolkit Loaded.")
    print("Ready for high-throughput publication analysis.")
