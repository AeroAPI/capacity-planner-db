# Distributed DB Capacity Planner

A real-time, comprehensive tool for capacity planning of a distributed database and its underlying infrastructure. It models how topology, workload, and server specifications affect storage and memory utilization.

## 🚀 Project Versions

This repository contains two versions of the tool:

1.  **Web GUI Orginal MVP (`https://wmaddux.github.io/capacity-planner-db/capacity_planner_mvp.html`):** An interactive, real-time web application using JavaScript/HTML/Tailwind.
2.  **Modular Script (`python/`):** A modular, command-line tool written in Python for batch processing and reporting.

-----

## I. Web GUI (Interactive Tool)

### How to Run

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/capacity-planner-db.git](https://github.com/your-username/capacity-planner-db.git)
    ```
2.  **Open Locally:** Open **`capacity_planner_mvp.html`** directly in any modern web browser.
3.  **Interact:** Adjust the sliders in the configuration panel to see instant updates in utilization metrics and the dynamic topology diagram.

-----

## II. Python Script (Modular Reporting)

### File Organization

The Python implementation is broken down for maximum modularity:

  * **`config.py`**: Holds all fixed constants, defaults, and unit conversion factors.
  * **`capacity_calculator.py`**: Contains the core mathematical logic and calculation functions.
  * **`main.py`**: The entry point for the application; loads configuration, executes calculations, and prints the formatted capacity report to the console.

### How to Run

1.  **Navigate to the script directory:**
    ```bash
    cd capacity-planner-db/python
    ```
2.  **Run the main script:**
    ```bash
    python main.py
    ```
3.  **To Modify Inputs:** Edit the `get_input_scenario()` function inside `main.py` to test different configurations, or change the default values inside `config.py`.

-----

## 💡 Key Metrics Calculated

The tool focuses on three primary utilization metrics:

1.  **Actual Storage Utilization (ASU):** Ratio of total data size (including Replication Factor) to total usable storage.
2.  **Total Memory Base Utilization (TMBU):** Memory used by the system and core indexes versus total available memory.
3.  **Total Memory Utilization w/ Tombstones (TMUT):** Worst-case memory consumption, accounting for delete overhead.

## 🛠️ Technology Stack

  * **Web GUI:** HTML5, Tailwind CSS (CDN), Pure JavaScript.
  * **Script:** Python 3.x.
