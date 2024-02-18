# -*- coding: utf-8 -*-
"""
functions for compressor and expander output state calcultations

so far/here: only for fixed isentropic efficiencies

((Part of carbatpy.))
Created on Sun May 21 08:51:33 2023

@author: atakan
"""

import carbatpy as cb


def compressor(p_out, eta_s, fluid, calc_type="const_eta",
               name="compressor"):
    """
    compressor or expander output state calculation

    so far only for a constant isentropic efficiency, according to the pressure
    change an expansion or compression is detected and handled.

    Parameters
    ----------

    p_out : float
        output pressure.
    eta_s : float
        isentropic efficiency.
    fluid : fprop.Fluid
        entering fluid, including properties, composition, and model.
    calc_type : string, optional
        how to calculate, so far, only one implemented. The default is
        "const_eta".
    name : string, optional
        name of the device. The default is "compressor".

    Returns
    -------
    state_out : array of float
        compressor output state containing [T,p,h,v,s,q].
    work_specific : float
        work per kg of fluid, positive for compressor; units:J/kg.

    """
    expander = False
    if fluid.properties.pressure > p_out:
        expander = True

    if calc_type == "const_eta":
        h_in = fluid.properties.enthalpy

        fluid.set_state(
            [fluid.properties.entropy, p_out], "SP")

        diff_enthalpy_s = fluid.properties.enthalpy-h_in

        if expander:
            work_specific = diff_enthalpy_s * eta_s
        else:
            work_specific = diff_enthalpy_s / eta_s

        state_out = fluid.set_state([h_in + work_specific, p_out], "HP")
    else:
        raise Exception(
            f"The option{calc_type} is not yet implemented for compressors")
    return state_out, work_specific



def pump(p_out, eta_s, fluid, calc_type="const_eta", name="pump"):
    """
    Calculate the exit state of a pump assuming an incompressible fluid.

    Only formulated for constant isentropic efficiency

    Parameters
    ----------
    p_out : float
        output pressure.
    eta_s : float
        isentropic efficiency.
    fluid : fprop.Fluid
        entering fluid, including properties, composition, and model.
    calc_type : string, optional
        how to calculate, so far, only one implemented. The default is
        "const_eta".
    name : string, optional
        name of the device. The default is "pump".

    Returns
    -------
    state_out : array of float
        compressor output state containing [T,p,h,v,s,q].
    work_specific : float
        work per kg of fluid, positive for compressor; units:J/kg.

    """
    if calc_type == "const_eta":
        state_in_ = fluid.properties.state
        work_is = state_in_[3] * (p_out - state_in_[1])
        if work > 0:
            work_specific =  work_is / eta_s
        else:
            work_specific =  work_is * eta_s
        h_out = state_in_[2] + work_specific
        state_out = fluid.set_state([h_out, p_out], "HP")
    else:
        raise Exception(
            f"The option{calc_type} is not yet implemented for compressors")

    return state_out, work_specific


if __name__ == "__main__":

    FLUID = "Propane * Pentane"
    comp = [.80, 0.2]
    flm = cb.fprop.FluidModel(FLUID)
    myFluid = cb.fprop.Fluid(flm, comp)
    P_LOW = 1e5
    T_IN = 310.
    DT_IN_LIQ = -5
    state_in = myFluid.set_state([T_IN, P_LOW], "TP")
    P_OUT = 10e5
    ETA_S = .7

    # Compressor-------------
    state_o, work = compressor(P_OUT, ETA_S, myFluid)
    print(myFluid.properties.temperature, work)
    print("\nCompressor", state_in, "\n", state_o, "\n", state_o-state_in)
    state_in = state_o
    state_o,work = compressor(P_LOW, ETA_S, myFluid)
    print("\nExpander:", state_in, "\n", state_o, "\n", state_o-state_in, work)

    # Pump, incompressible:

    state_in = myFluid.set_state([P_OUT, 0], "PQ")
    state_in = myFluid.set_state([P_OUT, state_in[0]+DT_IN_LIQ], "PT")
    state_o,work = pump(P_LOW, ETA_S, myFluid)
    print(f"pump work: {work:.3f} J/kg, state:{state_o}")
