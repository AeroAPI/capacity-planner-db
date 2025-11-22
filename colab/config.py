"""
Configuration settings for the Distributed DB Capacity Planner (v113).

This file centralizes all global constants, slider input defaults, 
and full descriptive names for output clarity.
"""

# --- FIXED SYSTEM CONSTANTS ---
CLUSTER_STORAGE_OVERHEAD_PCT = 0.024
OVERHEAD_MEMORY_PCT = 0.17
PI_ENTRY_SIZE_BYTES = 64
SI_ENTRY_SIZE_BYTES = 21
SI_OVERHEAD_MIB = 16
SI_DENSITY_FACTOR = 0.75
BYTES_TO_GB = 1024 ** 3 
MIB_TO_GB = 1024 
THROUGHPUT_PER_DISK_MBPS = 1500
IOPS_PER_DISK_K = 320

# --- DESCRIPTIVE DISPLAY NAMES ---
DISPLAY_NAMES = {
    'RF': 'Replication Factor',
    'NPC': 'Nodes per Cluster',
    'DPN': 'Devices per Node',
    'DS': 'Device Size',
    'NODES_LOST': 'Nodes Lost (Failure Scenario)',
    'MOC': 'Master Object Count',
    'ARS': 'Average Record Size',
    'ASEO': 'Avg SI Entries per Object',
    'NSI': 'Number of Secondary Indexes',
    'TP': 'Tombstone Percentage',
    'AMPN': 'Available Memory per Node',
    'CSOP': 'Cluster Storage Overhead Pct',
    'OMP': 'Overhead Memory Pct',
}

# --- SLIDER INPUT CONFIGURATION ---
INPUT_CONFIG = {
    # Topology
    'RF': { 'min': 1, 'max': 5, 'step': 1, 'default': 3, 'suffix': '' },
    'NPC': { 'min': 1, 'max': 150, 'step': 1, 'default': 12, 'suffix': '' },
    'DPN': { 'min': 1, 'max': 32, 'step': 1, 'default': 18, 'suffix': '' },
    'DS': { 'min': 50, 'max': 1000, 'step': 5, 'default': 55, 'suffix': ' GB' },
    'NODES_LOST': { 'min': 0, 'max': 150, 'step': 1, 'default': 1, 'suffix': '' }, 

    # Workload
    'MOC': { 'min': 1, 'max': 1000, 'step': 1, 'default': 8, 'suffix': ' Billion' }, 
    'ARS': { 'min': 100, 'max': 4096, 'step': 32, 'default': 250, 'suffix': ' Bytes' },
    'ASEO': { 'min': 0.0, 'max': 5.0, 'step': 0.1, 'default': 1.0, 'suffix': '' },
    'NSI': { 'min': 0, 'max': 32, 'step': 1, 'default': 5, 'suffix': '' },
    'TP': { 'min': 0, 'max': 100, 'step': 5, 'default': 10, 'suffix': ' %' }, 
    
    # Server Specs
    'AMPN': { 'min': 16, 'max': 256, 'step': 8, 'default': 64, 'suffix': ' GB' }
}
