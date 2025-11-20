Distributed DB Capacity Planner

A real-time, interactive web tool for capacity planning of a distributed database and its underlying infrastructure. It models how topology, workload, and server specifications affect storage and memory utilization.

🚀 How to Use

Clone the Repository:

git clone [https://github.com/your-username/capacity-planner-db.git](https://github.com/your-username/capacity-planner-db.git)


Run Locally: Open capacity_planner.html directly in any modern web browser.

Interact: Adjust the sliders in the System & Workload Configuration panel (Section 1) to see instant updates in:

Capacity Analysis: Key utilization percentages for Storage and Memory (Section 2).

System Topology: A dynamic SVG diagram visualizing the cluster and device layout (Section 4).

💡 Key Metrics Calculated

The tool focuses on three primary utilization metrics:

Actual Storage Utilization (ASU): Ratio of total data size (including Replication Factor) to total usable storage.

Total Memory Base Utilization (TMBU): Memory used by the system and core indexes versus total available memory.

Total Memory Utilization w/ Tombstones (TMUT): Worst-case memory consumption, accounting for delete overhead.

🛠️ Technology Stack

The tool is entirely contained within a single HTML file using:

HTML5

Tailwind CSS (via CDN) for styling.

Pure JavaScript for logic and calculations.

SVG for the dynamic topology diagram.
