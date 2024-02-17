# -*- coding: utf-8 -*-
"""
Created on Sun May 21 08:51:33 2023

@author: atakan
"""


import carbatpy as cb


def throttle(p_out, fluid, calc_type="const_h", name="throttle"):
    """
    throttle output state calculation

    so far only for a constant enthalpy

    Parameters
    ----------
    p_out : float
        output pressure.
    fluid : fprop.Fluid
        entering fluid, including properties, composition, and model.
    calc_type : string, optional
        how to calculate, so far, only one implemented. The default is
        "const_h".
    name : string, optional
        name of the device. The default is "throttle".

    Returns
    -------
    state_out : array of float
        compressor output state containing [T,p,h,v,s,q].

    """
    if calc_type == "const_h":
        state_out = fluid.set_state([fluid.properties.enthalpy, p_out], "HP")
    else:
        raise Exception(
            f"The option{calc_type} is not yet implemented for throttles")
    return state_out


if __name__ == "__main__":
    FLUID = "Propane * Pentane"
    comp = [.50, 0.5]
    flm = cb.fprop.FluidModel(FLUID)
    myFluid = cb.fprop.Fluid(flm, comp)
    state_in = myFluid.set_state([320., 19e5], "TP")

    P_OUT = 5e5

    state_out_main = throttle(P_OUT, myFluid)
    print("Throttle:\nInput:", state_in, "\nOutput:",
          state_out_main, "\nDifference", state_out_main-state_in)
