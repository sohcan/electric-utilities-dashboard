# Facilities QUBO Optimizer

A synthetic Streamlit dashboard exploring project selection under budget constraints using Quadratic Unconstrained Binary Optimization (QUBO).

QUBO means Quadratic Unconstrained Binary Optimization. It is a way to model yes/no selection problems using binary variables and penalty terms.

## What this app demonstrates

This project models a simplified facility-planning problem using synthetic data:

- candidate deficiencies or repair items
- synthetic facility inventory records
- synthetic funding and work-breakdown categories
- project-type funding splits
- budget limits
- binary project selection
- simulated annealing results
- visual summaries of selected and excluded project sets

## Synthetic data notice

All data in this repository is synthetic.

The facility, inventory, cost, deficiency, funding, and scenario fields are invented for demonstration purposes. They are not derived from real organizational data, internal systems, controlled datasets, or National Laboratory records. Some labels are public-sector-inspired fictional examples for demonstration only. This project is not affiliated with, endorsed by, or derived from any real agency, laboratory, facility, or internal system.

## Current structure

app.py  
requirements.txt  
runtime.txt  
PUBLICATION_CHECKLIST.md  
data_synthetic/  
data_synthetic_out/

## Run locally

Install the requirements:

pip install -r requirements.txt

Run the app:

streamlit run app.py

## Status

Portfolio prototype. This is a learning and demonstration project, not an official planning tool.