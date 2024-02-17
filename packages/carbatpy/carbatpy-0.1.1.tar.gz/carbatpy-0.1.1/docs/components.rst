
Components evaluation
=========================

A very basic approach to calculate heat exchangers, compressores(and expanders) 
as well as throttles.

Heat exchangers
---------------
Simple heat exchangers, only thermodynamic balances are calculated (no UA),
and by varying the mass flow rate and one state-point (temperature), a
minimum approach temperature is satisfied, but only if the given restrictions
allow it.
   
.. automodule:: src.models.components.heat_exchanger_thermo_v2
    :members:
    :special-members: __init__ 
    :undoc-members:
    :show-inheritance:

Compressors and Expanders
-------------------------

According to the given pressure levels, the script decides,
whether it is a compressor or an expander. At the moment the 
isentropic efficiency must be provided.

.. automodule:: src.models.components.compressor_simple
    :members:
    :special-members: __init__ 
    :undoc-members:
    :show-inheritance:

Throttle
-------------
For isenthalpic throttles only.

.. automodule:: src.models.components.throttle_simple
    :members:
    :special-members: __init__ 
    :undoc-members:
    :show-inheritance: