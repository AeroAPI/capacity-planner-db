# Distributed DB Capacity Planner

## Design goals (developing)
1. Highly intuitive method of exploring the relationship between configuration inputs and system characteristic outputs
2. Relate system characteristics to healthcheck type indicators
3. Ensure the "math" is easy to validate (and compare to real results)
4. The development platform is effectively extensible for continuous iteration
5. Produce comparison reports to snapshot decisions and explore input ranges (such as record size)

## 🚀 Project Versions

1.  **Initial MVP:** Currently, displays utilization estimates based on basic sizing imputs. Access the tool here: [Capacity Planner Web GUI](https://wmaddux.github.io/capacity-planner-db/capacity_planner_mvp.html)
1.  **Spreadsheet MVP version:** Basically, the same for the purpose of playing with and preserving the math: [Capacity Planner GSheet](https://docs.google.com/spreadsheets/d/175XXko30EAZ8zoe-InmQY2H8Cn2FDO4tBE_9y6NwgW0/edit?usp=sharing)
1.  **Current Standard Spreadsheet:** Current version mostly used by SE team: [Tool: Aerospike Sizing Estimator
](https://docs.google.com/spreadsheets/d/1c_CBjbZg4ykPqJgW-5aZnoUQHCwnsosDuBO-dkDa_sU/edit?usp=sharing)


## Sub-projects (to be combined later)
AWS Instance Type Lookup: [AWS Instance Specs](https://wmaddux.github.io/capacity-planner-db/aws_instance_viewer.html)
