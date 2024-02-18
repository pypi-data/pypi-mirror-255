

Heat Pump and Organic Rankine Cycles
====================================

Heat Pump
----------

For heat pumps of this simple structure (so far).

.. image:: 2-storage_no_discharge.jpg
  :width: 400
  :alt: heat pump with storage
  
As one of the outputs, one gets such plots:


.. image:: last_T_H_dot_plot.png
  :width: 400
  :alt: heat pump with storage, T-H_dot plot
  
.. automodule:: src.models.coupled.heat_pump_simple_v2
    :members:
    :special-members: __init__ 
    :undoc-members:
    :show-inheritance:

Organic Rankine Cycle
---------------------

Organic Rankine cycles with this structure are modelled:


.. image:: 2023-12-15-16-28cycle.png
    :width: 400
    :alt: organic rankine cycle with storages, structure plot
    
Typical results (here for a mixture) look like this:
    
.. image:: last_T_H_dot_plot_orc.png
    :width: 400
    :alt: organic rankine cycle with storages, results
    
.. automodule:: src.models.coupled.orc_simple_v2
    :members:
    :special-members: __init__ 
    :undoc-members:
    :show-inheritance:
    
Cycle Structure
---------------
    
The structure of cycles are read from excel files 
, to create the structure plot, as shown above. **graphviz** must be installed on the computer 
to use this script. An exemplary excel-file is found in the **data**-folder.
Here is the first page of it.

.. image:: orc_structure_Page1.png
   :width: 700
   
.. automodule:: src.models.coupled.read_cycle_structure
    :members:
    :undoc-members:
    :show-inheritance:


   
