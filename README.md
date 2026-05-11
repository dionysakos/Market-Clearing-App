# Clearit ⚡

## Nodal Market-Clearing App & Congestion Analytics

Clearit is a  simulation environment designed for **Locational Marginal Pricing** analysis and **Economic Dispatch** within linearized power systems. Leveraging a **Mixed-Integer Linear Programming**  core, the application provides a transparent, data-driven visualization of market-clearing mechanisms, transmission constraints, and system-wide economic efficiency.

## Live Deployment

The application is deployed as a cloud-native service and can be accessed via the following URL:

`make my url`

## Technical Framework

* **Linearized Flow** Equations: Utilizes Power Transfer Distribution Factors (**PTDFs**) for flow sensitivity analysis.

* Optimization Engine: Employs **MILP** solver to determine the optimal dispatch points while satisfying some basic constraints.

> The constraints include: Generation Capacity Limits (`P_max`,`P_min`), Network Thermal Limits (MW Flow constraints) & System Load Balance (Market Clearing)           

## Key Features

### Nodal Pricing Dashboard

An interactive visualization of the grid topology. It highlights price decoupling across nodes and identifies congested lines.

### Network Configuration

A modular interface to define:

* Generator Parameters: **Marginal costs** and **technical production limits**.
* Transmission Topology: Admittance matrix parameters and **thermal strain** thresholds.
* System Demand: **Nodal load profiles** for various dispatch scenarios.


### Market Analytics

A comprehensive suite of  charts detailing:

* Generation Mix: Real-time **dispatch levels** relative to capacity.
* LMP Decomposition: Analysis of Energy, **Congestion**, and Loss components.

### Learn

A dedicated knowledge repository containing short, key academic insights:

* **LMP vs. SMP** market structures.
* **Merit Order** dispatch logic.
* **Redispatching** mechanics in constrained networks.
* **Optimal** status.
* **Energy Makets** & Horizon.
* **Zonal vs Nodal** Pricing.
* **MILP** Logic.
* **Congestion**

## Installation & Setup

To execute the Clearit environment locally, ensure you have a Python 3.10+ environment established.

### Steps:

* Clone the Repository:

`git clone https://github.com/your-username/Market-Clearing-App.git`
`cd Market-Clearing-App`

* Install Dependencies:
`pip install -r requirements.txt`

* Launch the Application:
`streamlit run app/app.py`









