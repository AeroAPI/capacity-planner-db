"""
Core calculation functions for the Distributed DB Capacity Planner.

This module is designed to be pure logic, isolated from UI/Widgets.
"""
from typing import Dict, Any
import math
import config

def calculate_capacity(inputs: Dict[str, Any]) -> Dict[str, float]:
    """
    Performs all capacity, memory, and performance calculations.
    """
    
    # --- Input Mapping ---
    RF = inputs['RF']
    NPC = inputs['NPC']
    DPN = inputs['DPN']
    DS = inputs['DS']
    AMPN = inputs['AMPN']
    TP = inputs['TP'] / 100 
    NODES_LOST = inputs['NODES_LOST']
    
    # MOC is in Billions in the config, convert to raw count (10^9)
    MOC = inputs['MOC'] * 1000000000
    ARS = inputs['ARS']
    ASEO = inputs['ASEO']
    NSI = inputs['NSI']
    
    results = {}

    # --- 2.2.1 COMMON CALCULATIONS (Capacity and Index Sizing) ---
    
    # Capacity Fundamentals
    results['AMC'] = NPC * AMPN
    results['OMRC'] = results['AMC'] * config.OVERHEAD_MEMORY_PCT

    # Index Sizing
    PISU_bytes = MOC * RF * config.PI_ENTRY_SIZE_BYTES
    results['PISU'] = PISU_bytes / config.BYTES_TO_GB

    SI_part_1_bytes = (MOC * RF * ASEO * config.SI_ENTRY_SIZE_BYTES) / config.SI_DENSITY_FACTOR
    SI_part_2_gb = NSI * config.SI_OVERHEAD_MIB / config.MIB_TO_GB
    results['SISU'] = (SI_part_1_bytes / config.BYTES_TO_GB) + SI_part_2_gb

    results['TMU'] = results['OMRC'] + results['PISU'] + results['SISU']
    results['TMT'] = results['TMU'] * (1 + TP) 
    
    results['TSAPC'] = NPC * DPN * DS * (1 - config.CLUSTER_STORAGE_OVERHEAD_PCT)
    TDS_bytes = MOC * RF * ARS
    results['TDS'] = TDS_bytes / config.BYTES_TO_GB
    
    # Performance Fundamentals (Node-level)
    results['TPUT_Node'] = DPN * config.THROUGHPUT_PER_DISK_MBPS
    results['IOPS_Node'] = DPN * config.IOPS_PER_DISK_K


    # --- 2.2.2 HEALTHY CLUSTER UTILIZATION ---
    results['ASU'] = (results['TDS'] / results['TSAPC']) * 100 if results['TSAPC'] else float('inf')
    results['TMBU'] = (results['TMU'] / results['AMC']) * 100 if results['AMC'] else float('inf')
    results['TMUT'] = (results['TMT'] / results['AMC']) * 100 if results['AMC'] else float('inf')
    results['TMAPC'] = results['AMC']

    results['Healthy_TPUT'] = NPC * results['TPUT_Node']
    results['Healthy_IOPS'] = NPC * results['IOPS_Node']


    # --- 2.2.3 FAILURE SCENARIO CALCULATIONS ---
    
    effectiveNodes = max(0, NPC - NODES_LOST)
    
    results['Fail_TSAPC'] = effectiveNodes * DPN * DS * (1 - config.CLUSTER_STORAGE_OVERHEAD_PCT)
    results['Fail_AMC'] = effectiveNodes * AMPN

    results['Fail_TPUT'] = effectiveNodes * results['TPUT_Node']
    results['Fail_IOPS'] = effectiveNodes * results['IOPS_Node']
    
    # Utilization Recalculation (Capacity)
    results['Fail_ASU'] = (results['Fail_TSAPC'] > 0) and (results['TDS'] / results['Fail_TSAPC']) * 100 or float('inf')
    results['Fail_TMBU'] = (results['TMU'] / results['Fail_AMC']) * 100 or float('inf')
    results['Fail_TMUT'] = (results['TMT'] / results['Fail_AMC']) * 100 or float('inf')

    return results
