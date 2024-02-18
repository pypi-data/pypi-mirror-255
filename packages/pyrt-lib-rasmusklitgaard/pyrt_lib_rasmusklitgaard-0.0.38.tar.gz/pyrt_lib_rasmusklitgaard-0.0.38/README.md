# pyrt-lib

Python based helper library for RT cohort analysis


# Classes:
## Patient
A class for a patient. Initializes with the path to the directory containing DICOMS, dvhs' (made with makedvh from gitlab.com/dcpt-research/fluka-simulation-batch-tools). Automatically reads all the data and can be queried for dvh parameters and so forth.
Also reads metadata - right now from an excel sheet for these patients, but could be altered to any patient cohort.


## Cohort
A class for a cohort, a group of patients. Primary function is that it can make sub-cohorts based on a constraint, 
such as age, toxicity, gamma-pass score or dvh parameters or whatever you want.


# Plans
Will contain classes to help with data-flow for patients with CT's, RTSTRUCT's, RTPLAN's, planning RTDOSE distributions as well as 
Monte Carlo simulations of dose and Linear Energy Transfer.

The library will also include functionality for variable RBE for at least the most used models. 
