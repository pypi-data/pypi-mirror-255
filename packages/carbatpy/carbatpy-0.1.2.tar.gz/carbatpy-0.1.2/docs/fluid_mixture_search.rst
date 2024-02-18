

Fluid Mixture search
====================

This utility script searches for mixture compositions, which evaporate at a
given temperture and condense at a second given temperature, while having 
pressures within given limits. The idea is to find fluid mixtures for heat
pumps (and later Carnot Batteries) which work between two pairs of storages.
Each of them start at room temperature, one is heated up, the other cooled
down. Thus room temperature is one posssible restriction. 


.. image:: 2-storage_no_discharge.jpg
  :width: 300
  :alt: heat pump with storage
  
As states are also checked after isentropic compression, throtteling saturated
liquid or checking 
the temperature of the saturated liquid at low pressure.
It works well for quaternary mixtures. As 
programmed, 21 mole fractions between 0 and 1 are tried for each compund,
but checking that the sum is 1 for all compounds. 
The results are plotted, stored as a csv file with further thermodynamic 
properties of the two evaluated states, and a jason file with the compunds,
temperatures (in K) and pressures (Pa) is written into a given directory.


.. image:: explanation-sketch-Ts-property_eval_mixture.jpg
  :width: 300
  :alt: heat pump with storage


The csv output file structure is as follows:

* number of calculation
* the four mole fractions, species names are in the title
* index l: the properties for saturated vapor at the given low temperature
* index sup: the poperties at superheating at pressure p_l for a prescribed superheating
* index h: the properties for saturated vapor at the given high temperature
* index is: the properties for the isentropic state (sup ->p_h) at the given low temperature
* index dew: the properties for the saturated liquid at p_h
* index thr: the properties for the isenthalpic throtteling from saturated liquid to p_l
* index hplT: the properties at T_l and p_h
* index thrlow: the properties for the isenthalpic throtteling from hplt ->p_l
* index bol: the properties for saturated liquid at the low pressure p_l
* p_ratio: the pressure ratio
* T_glide_h: the temperature glide at high pressure
* dv/v'': (ca.) the mean change in volume along throtteling relative to the specific volume of the vapor, this is a measure of how much work is 'lost' along throtteling
* dv/v''-b: similar volume ratio after subcooling to thrlow, answer the question: will subcooling reduce losses (strongly)?
* COP_is: What is the predicted COP for isentropic compression (losses along throtteling are seen here)

For each indexed state : T,p,h,v,s,q,u in SI units(mass base) are listed.


It is found at: src.utils.property_eval_mixture.
The results are stored in a directory, which is set in config.py. Best is to
set the environment variable CARBATPY_RES_DIR to an appropriate path. As an
alternative results are stored in TEMP.
 

.. image:: 2023-10-25-14-03EthProHexBut.png
  :width: 300
  :alt: p-ratio vs. T-glide plot

Example

.. code-block:: python

    fluids_all = ["Ethane","Propane","Hexane","Butane"]
    T_low = 285.00
    T_high = 363.00
    p_low = 10e4
    p_high = 22e5
    dir_name = r"C:\Users\atakan\sciebo\results\optimal_hp_fluid"
    
    mixture_search(fluids_all, [T_low, T_high], [p_low, p_high], 
                   dir_name, resolution = 21)


.. automodule:: src.utils.property_eval_mixture
    :members:
    :undoc-members:
    

.. automodule:: src.utils.optimize
    :members:
    :undoc-members:
    
