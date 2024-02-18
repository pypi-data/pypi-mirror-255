

Fluid Property evaluation (general)
===================================

At the moment REFPROP (NIST)  can be used for property evaluations of 
pure fluids and mixures, TREND (RU Bochum) usage  will be included in near future. 
They will have to be installed on your system!

First an instance of the Fluid class hast to be generated, for a given fluid model
(for now: only RefProp), then the composition and state can be set.
The evaluated properties are then  available through the FluidState class. In general they are: 
"Temperature", "Pressure", "spec. Enthalpy",
"spec. Volume", "spec. Entropy", "quality", "spec. internal Energy"

Example

.. code-block:: python

    FLUID = "Propane * Pentane"
    comp = [.50, 0.5]
    flm = FluidModel(FLUID)
    myFluid = Fluid(flm, comp)
    st0 = myFluid.set_state([300., 1e5], "TP")
    st1 = myFluid.set_state([300., 1e5], "TP", _TRANS_STRING)
    print(st0, st1)
    myFluid.print_state()
    myFluid.set_composition([.2,.8])
    st0 = myFluid.set_state([300., 1e5], "TP", composition =[.35, .65])
    myFluid.print_state()

.. automodule:: src.models.fluids.fluid_props
    :members:
    :special-members: __init__ , _PROPS
    :undoc-members:
    :show-inheritance:
    :inherited-members:

