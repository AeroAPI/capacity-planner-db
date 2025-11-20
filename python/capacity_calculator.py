"""
Core calculation functions for the Distributed DB Capacity Planner.

This module contains the logic for determining storage and memory utilization 
based on topology, workload, and server configurations.
"""

from typing import Dict, Any
from config import (
    CLUSTER_STORAGE_OVERHEAD_PCT, OVERHEAD_MEMORY_PCT,
    PI_ENTRY_SIZE_BYTES, SI_ENTRY_SIZE_BYTES, SI_PER_INDEX_OVERHEAD_MIB,
    BYTES_TO_GB, MIB_TO_GB
)

def calculate_capacity(inputs: Dict[str, Any]) -> Dict[str, float]:
    """
    Performs all capacity planning calculations based on input parameters.

    Args:
        inputs: A dictionary containing all system and workload parameters.

    Returns:
        A dictionary containing all calculated output metrics.
    """
    
    # --- Input Parameter Extraction ---
    RF = inputs['RF']
    NPC = inputs['NPC']
    DPN = inputs['DPN']
    DS = inputs['DS']
    MOC = inputs['MOC']
    ARS = inputs['ARS']
    ASEO = inputs['ASEO']
    NSI = inputs['NSI']
    TP = inputs['TP']
    AMPN = inputs['AMPN']
    
    # --- INTERNAL CALCULATIONS ---
    
    # Available memory per cluster (GB) [AMC]
    # AMC = NPC * AMPN
    AMC = NPC * AMPN

    # Overhead memory required per cluster (GB) [OMRC]
    # OMRC = AMC * OMP
    OMRC = AMC * OVERHEAD_MEMORY_PCT

    # Primary index shmem used (GB) [PISU]
    # PISU = (MOC * RF * 64) / (1024^3)
    PISU_bytes = MOC * RF * PI_ENTRY_SIZE_BYTES
    PISU = PISU_bytes / BYTES_TO_GB

    # Secondary index shmem used (GB) [SISU]
    # SISU = (MOC * RF * ASEO * 21) / 0.75 + (NSI * 16 MiB)
    # Note: 0.75 is the density factor mentioned in the prompt.
    SI_part_1_bytes = (MOC * RF * ASEO * SI_ENTRY_SIZE_BYTES) / 0.75
    SI_part_2_gb = NSI * SI_PER_INDEX_OVERHEAD_MIB / MIB_TO_GB
    SISU = (SI_part_1_bytes / BYTES_TO_GB) + SI_part_2_gb

    # Total mem + tombstones (GB) [TMT]
    # TMT = (PISU + SISU) * (1 + TP) + OMRC
    TMT = (PISU + SISU) * (1 + TP) + OMRC

    # --- OUTPUT CALCULATIONS ---
    
    results = {}

    # Total Storage available per cluster (GB) [TSAPC]
    # TSAPC = NPC * DPN * DS * (1 - CSOP)
    results['TSAPC'] = NPC * DPN * DS * (1 - CLUSTER_STORAGE_OVERHEAD_PCT)

    # Total Data Stored (GB) [TDS]
    # TDS = MOC * RF * ARS / (1024^3)
    TDS_bytes = MOC * RF * ARS
    results['TDS'] = TDS_bytes / BYTES_TO_GB

    # Actual storage utilization with RF included [ASU]
    # ASU = TDS / TSAPC
    results['ASU'] = results['TDS'] / results['TSAPC'] if results['TSAPC'] else 0

    # Total memory available per cluster (GB) [TMAPC] - Same as AMC
    results['TMAPC'] = AMC

    # Total memory used (GB) [TMU]
    # TMU = OMRC + PISU + SISU
    results['TMU'] = OMRC + PISU + SISU

    # Total Memory base utilization (GB) [TMBU]
    # TMBU = TMU / AMC
    results['TMBU'] = results['TMU'] / AMC if AMC else 0

    # Total Memory utilization + tombstones (GB) [TMUT]
    # TMUT = TMT / AMC
    results['TMUT'] = TMT / AMC if AMC else 0

    # Add intermediate/raw values for reporting
    results['AMC'] = AMC
    results['TMT'] = TMT
    
    return results
