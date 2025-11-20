"""
Configuration settings for the Distributed DB Capacity Planner.

This file centralizes all constant values, default parameters, and unit conversion factors.
"""

# --- FIXED CONSTANTS (Based on system architecture) ---

# Cluster storage overhead pct (typically fixed at 2.4%) [CSOP]
CLUSTER_STORAGE_OVERHEAD_PCT = 0.024

# Overhead memory pct (typically fixed at 17.00%) [OMP]
OVERHEAD_MEMORY_PCT = 0.17

# Size assumptions for index entries (bytes)
PI_ENTRY_SIZE_BYTES = 64
SI_ENTRY_SIZE_BYTES = 21
SI_PER_INDEX_OVERHEAD_MIB = 16

# Unit conversion factors
BYTES_TO_GB = 1024 ** 3 # 1 GB = 1024 * 1024 * 1024 bytes
MIB_TO_GB = 1024 # 1 MiB = 1024 KB, 1 GB = 1024 MiB


# --- DEFAULT AND RANGE SETTINGS ---

# Topology defaults and limits
TOPOLOGY_DEFAULTS = {
    'RF': 2,     # Replication Factor (1 to 5)
    'NPC': 3,    # Nodes per Cluster (1 to 150)
    'DPN': 3,    # Devices per Node (1 to 32)
    'DS': 500,   # Device Size (GB) (100 to 1000)
}

# Workload defaults and limits
WORKLOAD_DEFAULTS = {
    'MOC': 100000000, # Master object count (100 million default for script entry)
    'ARS': 512,       # Average record size (B)
    'ASEO': 1.0,      # Average SI entries per object (default is 1)
    'NSI': 5,         # Number of secondary indexes
    'TP': 0.10,       # Tombstone pct (0.0 to 1.0, 10% default)
}

# Server stats defaults and limits
SERVER_DEFAULTS = {
    'AMPN': 64,  # Available memory per node (GB)
}
