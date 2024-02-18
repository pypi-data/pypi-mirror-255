# -*- coding: utf-8 -*-
"""

A script to evaluate mixtures, in order to find some with vapor pressures
in some limits at given temperatures, together with the temperature glide.
The results are stored as figure, as csv and in a json-file(Input); all in the
given directory.


The csv output file structure is as follows:

* number of calculation
* the four mole fractions, species names are in the title
* index l: the properties for saturated vapor at the given low temperature
* index sup: the poperties at superheating at pressure p_l for a prescribed superheating
* index h: the properties for saturated vapor at the given high temperature
* index is: the properties for the isentropic state (sup ->p_h) at the given low temperature
* index is80: the properties for the isentropic effic. of 80 % (sup ->p_h) at the given low temperature
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


part of carbatpy

Created on Thu Oct 19 14:11:14 2023

@author: atakan
"""


import json
import itertools
import matplotlib.pyplot as plt
import seaborn as sbn
import pandas as pd
import numpy as np
import carbatpy as cb



def mixture_search(fluids_all, temp_both, p_both, res_dir, d_temp_superheating=5,
                   resolution=21, temp_limit=False, **kwargs):
    """
    Mixtures are evaluated/screened to find mixtures with a given temperature
    glide in a certain pressure range. For all possible mixture compositions
    first the saturated vapor pressure at the given low temperature and composition
    is evaluated, if it is in the allowed regime, the saturated vapor pressure
    (p_h) of the mixture at the high temperature is evaluated.
    If this is below the allowed high
    pressure, the saturated liquid temperature at this p_h is evaluated and the
    temperature difference is taken as temperature glide. The pressure ratio is
    plotted as a function of temperature glide.
    The plot, the states (as csv-file) and the input parameters (as .json-file)
    are stored.
    in the csv-File first the mole fractions are given followed by the
    properties of the low temperature sat.vapor, after superheating,
    for thehigh temperature sat. vapor, the isentropic state after compression,
    high pressure sat.liquid, low pressuer isenthalpic (throtteling) state to
    the high pressure sat. liquid, and the low pressure saturated liquis state.
    For each of them: T,p,h,v,s,q,u in SI units(mass base)

    Parameters
    ----------
    fluids_all : list of strings
        up to 4 fluid names of the mixture, as defined in the fluid model
        (REFPROP).
    temp_both : List of two floats
        the minimum (at low pressure) and the maximum (at high pressure)
        saturated vapor temperature (both dew points) in K.
    p_both : List of two floats
        allowed min and max pressure in Pa.
    res_dir : string
        Directory name, where the results are stored.
    d_temp_superheating : float. optional
        super heating temperature in K. The default is 5.
    resolution : integer, optional
        inverse is the interval for the mole fraction screening (21 means every
        0.05 a value is calculated). The default is 21.
    temp_limit : Boolean, optional
        selects only values, where the temperature of the saturated liquid at
        high pressure is above temp_both[0]. The default is False.
    kwargs : dict
        is not implemented yet, but can be used later to select another fluid
        model, instead of REFPROP.

    Returns
    -------
    None.

    """
    # dir_name = r"C:\Users\atakan\sciebo\results\optimal_hp_fluid"
    eff_isentropic = 0.8  # isentropic efficiency, compressor
    all_results = {}
    exception_messages = []
    all_results["warn"] = 0
    if len(kwargs) > 0:
        print(f"These arguments are not implemented yet{kwargs}")
        all_results["warn"] = 1
    dir_name = res_dir

    plt.style.use('seaborn-v0_8-poster')  # 'seaborn-v0_8-poster')
    # fluids_all = ["Ethane", "Propane", "Pentane", "CO2"]
    fluid_mixture = "*".join(fluids_all)
    # fluid_mixture = "Dimethylether * Butane * Pentane * Hexane" #  "Propane * Butane * Pentane * Hexane"
    names = ["x_" + s for s in fluids_all]

    fn_end = "".join([s[:3] for s in fluids_all])
    fname = cb.helpers.file_copy.copy_script_add_date(
        fn_end, __file__, dir_name)
    # fname = date + fn_end
    comp = [.5, 0., 0.5, 0.0]  # , 0.0]

    flm = cb.fprop.FluidModel(fluid_mixture)
    my_fluid = cb.fprop.Fluid(flm, comp)
    temp_low, temp_high = temp_both
    p_low, p_high = p_both
    xi = np.linspace(0, 1, resolution)
    results = []

    n_species = len(fluids_all)

    variables_dict = {"File_name": fname,
                      "Dir_name": dir_name,
                      "Fluid": fluid_mixture,
                      "T_low": temp_low,
                      "T_high": temp_high,
                      "d_temp_superheating": d_temp_superheating,
                      "p_low": p_low,
                      "p_high": p_high,
                      "eta_is80": eff_isentropic,
                      "what": "T_sat_l, T_sat_h, T_super, T_is,T_is80, T_throt,Tsat_l_high"
                      }

    # Dateipfad, in dem die JSON-Datei gespeichert wird
    json_file_path = fname+"_variablen.json"

    # Speichern des Dictionaries in einer JSON-Datei
    with open(json_file_path, 'w', encoding="utf-8") as json_file:
        json.dump(variables_dict, json_file)

    print(f"Variablen wurden in '{json_file_path}' gespeichert.")
    mole_fractions = np.zeros((n_species))

    for positions in itertools.product(range(len(xi)), repeat=n_species-1):
        # positions ist ein Tupel, das die ausgewählten Positionen enthält
        actual_x = np.array([xi[i] for i in positions])
        if (actual_x.sum() <= 1):
            mole_fractions[:3] = actual_x
            mole_fractions[n_species-1] = 1 - actual_x.sum()
            my_fluid.set_composition(mole_fractions)

            try:
                state_low = my_fluid.set_state(
                    [temp_low - d_temp_superheating, 1.], "TQ")  # find low pressure
                state_sup = my_fluid.set_state([state_low[1], temp_low],
                                              "PT")  # super heated state at low pressure

                if (state_low[1] > p_low) and (state_low[1] < p_high):
                    state_low_boil = my_fluid.set_state([state_low[1], 0],
                                                       "PQ")  # saturated liquid at low pressure
                    state_high = my_fluid.set_state(
                        [temp_high, 1.], "TQ")  # find high pressure, sat. vapor

                    if (state_high[1] < p_high and state_high[1] > p_low):

                        state_is = my_fluid.set_state(
                            [state_high[1], state_sup[4]], "PS")  # isentropic compression
                        work_is = state_is[2] - state_sup[2]
                        work_80 = work_is / eff_isentropic
                        # state after compression with eff_isentropic
                        state_is80 = my_fluid.set_state(
                            [state_high[1], state_sup[2] + work_80], "PH")
                        # saturated liquid at high pressure
                        state_dew = my_fluid.set_state([state_high[1], 0], "PQ")

                        if temp_limit and state_dew[0] > temp_low:
                            state_throttle = my_fluid.set_state([state_dew[2],
                                                               state_low[1]], "HP")  # throtteling the liquid to low pressure
                            state_high_p_low_T = my_fluid.set_state(
                                [state_high[1], temp_low], "PT")  # high pressure cooled to low_t
                            state_throttle_low = my_fluid.set_state([state_high_p_low_T[2],
                                                                    state_low[1]], "HP")
                            results.append(np.array([*mole_fractions, *state_low,
                                                     *state_sup,
                                                     *state_high,
                                                     *state_is,
                                                     *state_is80,
                                                     *state_dew,
                                                     *state_throttle,
                                                     *state_high_p_low_T,
                                                     *state_throttle_low,
                                                     *state_low_boil]))
            except Exception as ex_message:
                exception_messages.append(ex_message)
                

    n0 = cb.fprop._fl_properties_names[:7]
    results = np.array(results)
    names = [*names, *[n+"_l" for n in n0],
             *[n+"_sup" for n in n0],
             *[n+"_h" for n in n0],
             *[n+"_is" for n in n0],
             *[n+"_is80" for n in n0],
             *[n+"_dew" for n in n0],
             *[n+"_thr" for n in n0],
             *[n+"_hplt" for n in n0],
             *[n+"_thrlow" for n in n0],
             *[n+"_bol" for n in n0]
             ]

    dframe = pd.DataFrame(data=results, columns=names)
    dframe.to_csv(fname+".csv")
    dframe["p_ratio"] = dframe["Pressure_h"] / dframe["Pressure_l"]
    dframe["T_glide_h"] = dframe["Temperature_h"] - dframe["Temperature_dew"]
    dframe["dv_v''"] = 1 - (dframe[n0[3]+"_thr"]
                            + dframe[n0[3]+"_dew"]) / \
        (dframe[n0[3]+"_is"] + dframe[n0[3]+"_sup"])
    if temp_limit:
        dframe["dv_v''"] = 1 - (dframe[n0[3]+"_thr"]
                                + dframe[n0[3]+"_dew"]) / \
            (dframe[n0[3]+"_is"] + dframe[n0[3]+"_sup"])
        dframe["dv_v''_b"] = 1 - (dframe[n0[3]+"_thrlow"]  # does it help to subcool?
                                  + dframe[n0[3]+"_hplt"]) / \
            (dframe[n0[3]+"_is"] + dframe[n0[3]+"_sup"])
        dframe["COP_is"] = (dframe[n0[2]+"_is"] - dframe[n0[2]+"_dew"]) /\
            ((dframe[n0[2]+"_is"]-dframe[n0[2]+"_sup"]))

    dframe.to_csv(fname+".csv")

    # Plot
    f, ax = plt.subplots(
        figsize=(10, 10), layout="constrained", nrows=1, ncols=1)
    fff = sbn.scatterplot(x="T_glide_h", y="p_ratio",
                          hue=names[0], size=names[1],
                          style=names[2], data=dframe.round(3), ax=ax)
    sbn.move_legend(fff, "upper left", bbox_to_anchor=(1, 1))
    ax.set_title(f"Mixture: {fluids_all}")
    f.savefig(fname+".png")
    all_results["exception_messages"] = exception_messages
    all_results["results_DataFrame"] = dframe
    return all_results


if __name__ == "__main__":
    FLUIDS_ACTUAL = ["Propane", "Ethane", "Pentane",
                     "Butane"]  # ["DME", "Ethane", "Butane","CO2"]
    TEMP_LOW = 285.00
    TEMP_HIGH = 363.00
    PRESSURE_LOW = 10E4
    PRESSURE_HIGH = 22E5
    DIRECTORY_NAME = cb._RESULTS_DIR + r"\optimal_hp_fluid\fluid_select_restricted"
    TEMPERATURE_LIMIT = True
    warn = mixture_search(FLUIDS_ACTUAL, [TEMP_LOW, TEMP_HIGH],
                          [PRESSURE_LOW, PRESSURE_HIGH],
                          DIRECTORY_NAME, resolution=21,
                          temp_limit=TEMPERATURE_LIMIT)
