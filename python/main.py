"""
Main entry point for the Distributed DB Capacity Planner script.

Loads configuration, defines input scenario, runs calculations, and prints a report.
"""

from typing import Dict, Any
from config import (
    TOPOLOGY_DEFAULTS, WORKLOAD_DEFAULTS, SERVER_DEFAULTS,
    CLUSTER_STORAGE_OVERHEAD_PCT, OVERHEAD_MEMORY_PCT
)
from capacity_calculator import calculate_capacity

def get_input_scenario() -> Dict[str, Any]:
    """
    Combines all default settings to create a sample input scenario.
    In a real-world script, this is where user input would be parsed.
    """
    
    # --- SAMPLE SCENARIO (Can be modified here for testing) ---
    
    scenario = {}
    scenario.update(TOPOLOGY_DEFAULTS)
    scenario.update(WORKLOAD_DEFAULTS)
    scenario.update(SERVER_DEFAULTS)

    # Example adjustment to stress memory: High SI Count
    # scenario['NSI'] = 10
    
    # Example adjustment to stress storage: Low device count, high record size
    # scenario['DPN'] = 1
    # scenario['ARS'] = 1024 
    
    return scenario

def print_report(inputs: Dict[str, Any], results: Dict[str, float]):
    """
    Prints a well-formatted capacity planning report.
    """
    
    # --- Helper Functions for Formatting ---
    def format_pct(value: float) -> str:
        if value > 1.0:
            return f"{value * 100:.2f}% (OVER)"
        return f"{value * 100:.2f}%"

    def format_gb(value: float) -> str:
        return f"{value:,.2f} GB"

    def format_raw(value: Any) -> str:
        if isinstance(value, float):
            return f"{value:,.2f}"
        return str(value)

    print("\n" + "="*80)
    print(" " * 20 + "DISTRIBUTED DB CAPACITY PLANNING REPORT")
    print("="*80 + "\n")

    # --- INPUT SUMMARY ---
    print("--- 1. Input Parameters ---")
    print(f"{'Replication Factor (RF):':<40} {inputs['RF']}")
    print(f"{'Nodes per Cluster (NPC):':<40} {inputs['NPC']}")
    print(f"{'Devices per Node (DPN):':<40} {inputs['DPN']}")
    print(f"{'Device Size (DS):':<40} {format_gb(inputs['DS'])}")
    print("-" * 40)
    print(f"{'Master Object Count (MOC):':<40} {inputs['MOC']:,.0f} objects")
    print(f"{'Average Record Size (ARS):':<40} {inputs['ARS']} B")
    print(f"{'Avg SI Entries per Object (ASEO):':<40} {inputs['ASEO']}")
    print(f"{'Number of Secondary Indexes (NSI):':<40} {inputs['NSI']}")
    print(f"{'Tombstone Pct (TP):':<40} {format_pct(inputs['TP'])}")
    print("-" * 40)
    print(f"{'Available Memory per Node (AMPN):':<40} {format_gb(inputs['AMPN'])}")
    print(f"{'Cluster Storage Overhead Pct:':<40} {format_pct(CLUSTER_STORAGE_OVERHEAD_PCT)}")
    print(f"{'Overhead Memory Pct:':<40} {format_pct(OVERHEAD_MEMORY_PCT)}\n")
    
    # --- CAPACITY ANALYSIS (OUTPUT) ---
    print("--- 2. Capacity Analysis (Utilization) ---")
    
    # Storage Utilization
    asu = results['ASU']
    storage_status = "CRITICAL" if asu > 1.0 else ("WARNING" if asu > 0.85 else "OK")
    print(f"{'Actual Storage Utilization (ASU):':<40} {format_pct(asu):<15} [Status: {storage_status}]")
    
    # Memory Base Utilization
    tmbu = results['TMBU']
    mem_base_status = "WARNING" if tmbu > 0.8 else "OK"
    print(f"{'Total Memory Base Utilization (TMBU):':<40} {format_pct(tmbu):<15} [Status: {mem_base_status}]")

    # Memory Utilization w/ Tombstones
    tmut = results['TMUT']
    mem_tombstone_status = "CRITICAL" if tmut > 1.0 else ("WARNING" if tmut > 0.85 else "OK")
    print(f"{'Memory Utilization w/ Tombstones (TMUT):':<40} {format_pct(tmut):<15} [Status: {mem_tombstone_status}]")
    
    print("\n--- 3. Physical Capacity and Consumption (GB) ---")

    # Storage Metrics
    print(f"{'Total Available Storage per Cluster (TSAPC):':<45} {format_gb(results['TSAPC'])}")
    print(f"{'Total Data Stored (TDS) (with RF):':<45} {format_gb(results['TDS'])}")
    print("-" * 45)
    
    # Memory Metrics
    print(f"{'Total Available Memory per Cluster (TMAPC):':<45} {format_gb(results['TMAPC'])}")
    print(f"{'Total Memory Used (Base Index + Overhead):':<45} {format_gb(results['TMU'])}")
    print(f"{'Total Memory w/ Tombstones (Worst Case):':<45} {format_gb(results['TMT'])}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    
    # 1. Load the input scenario
    input_parameters = get_input_scenario()
    
    # 2. Calculate results
    calculated_results = calculate_capacity(input_parameters)
    
    # 3. Print report
    print_report(input_parameters, calculated_results)
