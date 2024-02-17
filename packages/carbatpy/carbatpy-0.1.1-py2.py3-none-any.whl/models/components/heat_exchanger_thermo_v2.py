# -*- coding: utf-8 -*-
"""
Created on Sun May 21 08:51:33 2023

@author: atakan
"""


import copy

# import src.models.fluids.fluid_props as fprop
import numpy as np
from scipy.optimize import minimize  # root, root_scalar
import matplotlib.pyplot as plt
import carbatpy as cb


class StaticHeatExchanger:
    """
    Class for static counter-flow heat exchanger

    means: no time dependence and no heat transfer coefficients * areas
    are used (UA)! Instead a minimum approach temperature is tried to be met.
    At the moment, this is mainly done by varying one of the mass flow rates.
    But this is sometimes not enough and a variation of the working fluid
    pressure will soon be included.
    Only the first law and second law will be checked (the latter must be
    improved).

    """

    def __init__(self, fluids, h_dot_min, h_out_w, h_limit_s=np.NAN,
                 points=50, d_temp_separation_min=0.5, calc_type="const",
                 name="evaporator"):
        """
        class to calculate (static/steady state) heat-exchangers

        includes pinch-point analysis and plotting,
        only implemented for simple thermodynamic calculations
        (no convection coefficients and heat exchanger areas regarded yet)

        Parameters
        ----------
        fluids : list of 2 fprop.Fluid
            The definition of the two fluids, as they enter the heat exchangers.
            Typically at room temperature.
        h_dot_min : float
            enthalpy flow rate (W) which has to be transfered.
        h_out_w : float
            exit enthalpy of the working fluid.
        h_limit_s : float or NAN, optional
            if there is a limit in enthalpy for the secondary fluid, it can be
            given here. The default is NAN.
        points : integer, optional
            for how many points (array) shall the minimum approach temperature
            be checked and properties be returned (for plotting etc.)
            The default is 30.
        d_temp_separation_min : float, optional
            Minimium approach temperature (pinch point) between the two fluids.
            The default is 0.5.
        calc_type : string, optional
            which calculation type shall be performed; only one implemented so
            far. The default is "const".
        name : string, optional
            name of the heat exchanger. The default is "evaporator".

        Returns
        -------
        None.

        """
        self.fluids = fluids
        state_in_w = fluids[0].properties.state
        self.m_dot_s = 0
        self.h_limit_s = h_limit_s
        self.q_dot = h_dot_min
        self.m_dot_w = np.abs(h_dot_min/(h_out_w-state_in_w[2]))
        self.h_out_w = h_out_w
        self.h_out_s = copy.copy(h_limit_s)  # this may be varied
        self.points = points
        self. d_temp_separation_min = d_temp_separation_min
        self.heating = -1
        if h_out_w < state_in_w[2]:
            self.heating = 1  # condenser (heating of the secondary fluid)
        self.calc_type = calc_type
        self.name = name
        self.all_states = np.zeros(
            (points, len(cb.fprop._THERMO_STRING.split(";"))))
        self.h_in_out = np.zeros((2, 4))
        self.warning = 0

    def pinch_calc(self,  verbose=False):
        """
        Calculate the changes in enthalpy and temperature in the heat exchanger

        counter-flow hex assumed! Both flows are isobaric.
        Is used to check, whether the second law is violated. The factor can
        be used to vary the mass flow rate of the working fluid, until no
        violation is found (done in root finding).

        Parameters
        ----------


        Raises
        ------
        Exception
            if temperatures are not consistent.

        Returns
        -------
        m_dot_s : float
            secondary fluid mass flow rate (kg/s.
        d_tempall : numpy-array
            The temperature differences along the counter-flow heat exchanger.
        w_array : array
            properties of the working fluid along the heat exchanger
            (T,p,h, etc. see fluid class).
        s_array : array
            properties of the secondary fluid along the heat exchanger
            (T,p,h, etc. see fluid class).

        """
        w_in = copy.copy(self.fluids[0])
        s_in = copy.copy(self.fluids[1])

        w_out = copy.copy(self.fluids[0])  # not yet the correct state!
        s_out = copy.copy(self.fluids[1])

        #  fixed values
        self. h_in_out[1, 0] = s_in.properties.enthalpy
        self. h_in_out[0, 0] = w_in.properties.enthalpy
        self. h_in_out[0, 1] = self.h_out_w

        # fixed limiting state, secondary fluid
        state_out_s = s_out.set_state([self.h_out_s,
                                       s_in.properties.pressure], "HP")

        self. h_in_out[1, 1] = state_out_s[2]

        h_delta_s = np.abs(
            state_out_s[2] - s_in.properties.enthalpy)

        # fixed heat flow,  determines mass flow rate
        self.m_dot_s = self.q_dot / h_delta_s

        h_array = np.linspace(
            self.h_in_out[1, 0], self.h_in_out[1, 1], self.points)
        values = np.zeros((self.points, 2))
        values[:, 0] = h_array
        values[:, 1] = s_out.properties.pressure

        s_array = s_out.set_state_v(values, given="HP")
        # if not(self.heating): s_array =np.flip(s_array, axis =0)

        # now working fluid:

        h_array = np.linspace(self.h_in_out[0, 1],
                              self.h_in_out[0, 0],
                              self.points)

        values = np.zeros((self.points, 2))
        values[:, 0] = h_array.T
        values[:, 1] = w_out.properties.pressure

        w_array = w_out.set_state_v(values, "HP")
        d_tempall = w_array[:, 0]-s_array[:, 0]

        # if self.heating:
        #     d_tempall = w_array[:, 0]-s_array[:, 0]
        # else:
        #     d_tempall = w_array[:, 0] - np.flip(s_array[:, 0],axis=0)
        if verbose:
            if self.heating > 0:
                print("cond", d_tempall[0], d_tempall[-1],
                      d_tempall.min(), d_tempall.max())
            else:
                print("evap", d_tempall[0], d_tempall[-1],
                      d_tempall.max(), d_tempall.min())

        return self.m_dot_s, d_tempall*self.heating, w_array, s_array

    def pinch_root(self, h_out_s, verbose=False):
        """
        function for root-finding of the minimum approach temperature

        the output enthalpy/state of the secondary fluid is varied.
        input
        for root

        Parameters
        ----------
        factor : float
            as said above.

        Returns
        -------
        minimumk T-difference, float
            root tries to reach a value of 0.

        """

        self.h_out_s = h_out_s
        mdot_s, d_temps, wf_states, sf_states = self.pinch_calc()

        shifted = d_temps - self.d_temp_separation_min
        mind_temp = shifted.min()
        # Approach to find both minima, if there are two, and to
        # reduce both their distance to the required minimum value.

        grad = np.gradient(d_temps)
        grad2 = np.gradient(grad)
        idx = np.where(np.sign(grad[:-1]) != np.sign(grad[1:]))[0] + 1
        idx_min = np.where(grad2[idx] > 0)

        if len(idx) > 0:
            # wanted =min(d_temps[idx] - self.d_temp_separation_min)
            sum_shifted = np.sum(shifted[idx[idx_min]])
        else:
            sum_shifted = mind_temp

        # print(h_out_s,idx, d_temps[idx])

        if (mind_temp <= -5e-6) or (self.m_dot_s <= 0):
            return -5e3*mind_temp

        # else:
            # mind_temp = np.abs(d_temps).min() # was here before
            # but two values should be at the minimum distance

            # value = np.sum(self.d_temp_separation_min -d_temps)
            # print(sum_shifted, "wanted",  mind_temp)

        if verbose:
            print("H", mind_temp - self.d_temp_separation_min,
                  mind_temp,  self.d_temp_separation_min, self.m_dot_s,
                  mdot_s, h_out_s)
        # return  self.d_temp_separation_min -mind_temp
        return sum_shifted

    def find_pinch(self):
        """
        Function tries to vary the secondary fluid enthalpy  until a
        minimum approach temperature is reached. This also changes the
        mass flow rate.  This is then also the new
        exit state
        within the heat exchanger. If this is also not succesful,
        self.warning is set to 1. This should be checked.

        Returns
        -------
        float
            the factor to multiply the mass flow rate with, to reach the
            minimum approach temperature. Igf not succesful the initial factor
            is returned.

        """
        verbose = False

        x0 = copy.copy(self.h_out_s)

        tolerance = 3e-3

        try:
            result = minimize(self.pinch_root, x0)

            if verbose:
                print(
                    f"result {result}, heating {self.heating}")

            if result.success or result.status == 2:
                if result.status == 2:
                    self.warning = 2  # T-difference probably smaller

                return result.x

        # except:
        except Exception as inst:
            print(type(inst))    # the exception type
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
            # but may be overridden in exception subclasses

            result = np.array([1e4])
            print("root-exception", self.heating)
            return result
        print("root-finding problem! (in heat_exchanger_thermo_v2.find_pinch)",
              result)
        print(f"Heating: {self.heating}")
        self.warning = 1
        return self.warning

    def pinch_plot(self, plot_fname="", plotting=True):
        """
        calculates the secondary fluid output state and mass flow, for the
        minimum approach temperature of the HeatExchanger instance. When wanted,
        this is also plotted

        Parameters
        ----------
        plot_fname : string, optional
            file-name to store the plot. The default is "".
        plotting : Boolean, optional
            should it be plotted? The default is True.

        Returns
        -------
        m_dot_s : float
            mass flow raete of the secondary fluid in SI units (kg/s).
        d_tempall : np.array
            the temperature differences between the two fluids along the heat
            exchanger.
        w_array : np.array [self.points, 7]
            the states of the working fluid along the heat exchanger.
        s_array : np.array [self.points, 7]
            the states of the secondary fluid along the heat exchanger.

        """
        print(f"------pinch-plot running -----plot:{plotting}")
        m_dot_s, d_tempall, w_array, s_array = self.pinch_calc()

        if plotting:
            h_w_plot_array = (
                w_array[:, 2] - w_array[:, 2].min()) * self.m_dot_w
            fig, ax_one = plt.subplots(1, 1)
            ax_one.plot((s_array[:, 2] - s_array[:, 2].min()) * self.m_dot_s,
                        s_array[:, 0], "v")
            ax_one.plot(h_w_plot_array, w_array[:, 0], "o")
            ax_one.set_xlabel(
                "specific enthalpy flow per mass of secondary fluid / (J / kg)")
            ax_one.set_ylabel("temperature / (K)")
            ax_one.set_title("heat exchanger, simple")
        if plot_fname != "":
            fig.savefig(plot_fname)

        return m_dot_s, d_tempall, w_array, s_array


if __name__ == "__main__":
    # two test cases condenser and evaporator:

    FLUID = "Propane * Pentane"  # working fluid
    FLS = "Methanol"  # "Water"  # secondary fluid
    comp = [.50, 0.5]
    flm = cb.fprop.FluidModel(FLUID)
    myFluid = cb.fprop.Fluid(flm, comp)

    secFlm = cb.fprop.FluidModel(FLS)
    secFluid = cb.fprop.Fluid(secFlm, [1.])
    D_TEMP_MIN = 6.0

    # Condenser, working fluid fixes all, secondary output enthalpy can be varied:
    SEC_TEMP_IN = 300.0
    SEC_TEMP_OUT_MAX = 370.0
    SEC_PRES_IN = 5e5
    H_DOT = 1e3
    state_sec_out = secFluid.set_state([SEC_TEMP_OUT_MAX, SEC_PRES_IN], "TP")

    state_sec_in = secFluid.set_state(
        [SEC_TEMP_IN, SEC_PRES_IN], "TP")  # this is the entering state

    # working fluid

    TEMP_SAT_VAP = SEC_TEMP_OUT_MAX + D_TEMP_MIN
    state_in = myFluid.set_state(
        [TEMP_SAT_VAP, 1.], "TQ")  # find minimum pressure

    WF_TEMP_IN = TEMP_SAT_VAP + D_TEMP_MIN
    WF_TEMP_OUT = SEC_TEMP_IN + D_TEMP_MIN
    state_out = myFluid.set_state([WF_TEMP_OUT, state_in[1]], "TP")

    state_in = myFluid.set_state([myFluid.properties.pressure,
                                  WF_TEMP_IN],
                                 "PT")

    hex0 = StaticHeatExchanger([myFluid, secFluid], H_DOT, state_out[2],
                               state_sec_out[2],
                               d_temp_separation_min=D_TEMP_MIN)
    # ms, d_tempall_first, w, s = hex0.pinch_calc()
    # f, ax_plot = plt.subplots(1)
    # ax_plot.plot((w[:, 2]-w[:, 2].min()) * hex0.m_dot_w, w[:, 0])
    # ax_plot.plot((s[:, 2]-s[:, 2].min()) * hex0.m_dot_s, s[:, 0])
    factor0 = hex0.find_pinch()
    ms0, d_tempall0, w0, s0 = hex0.pinch_plot("hex-plot.png")
    # print(f"w0 {w0[0]}")

    #  Evaporator: ----------------------------

    SEC_TEMP_IN = 300.0
    SEC_TEMP_OUT = 279
    SEC_PRES_IN = 15e5
    H_DOT = 1e3
    # D_TEMP_SUPER = 5.
    D_TEMP_MIN = 6.0
    state_sec_out = secFluid.set_state([SEC_TEMP_OUT, SEC_PRES_IN], "TP")
    # this mus be the last set_state before the hex is constructed:
    state_sec_in = secFluid.set_state([SEC_TEMP_IN, SEC_PRES_IN], "TP")

    # WF_TEMP_IN = SEC_TEMP_OUT  # - D_TEMP_MIN
    state_out = myFluid.set_state([SEC_TEMP_IN-D_TEMP_MIN, 1.0], "TQ")
    state_in = myFluid.set_state([SEC_TEMP_OUT-D_TEMP_MIN, state_out[1]], "TP")

    # print("state in", state_in)

    hex1 = StaticHeatExchanger([myFluid, secFluid], H_DOT, state_out[2],
                               state_sec_out[2],
                               d_temp_separation_min=D_TEMP_MIN)
    # ms1, d_tempall1, w1, s1 = hex1.pinch_calc()
    f, ax_plot = plt.subplots(1)
    # ax_plot.plot((w1[:, 2]-w1[:, 2].min()) * hex1.m_dot_w, w1[:, 0])
    # ax_plot.plot((s1[:, 2]-s1[:, 2].min()) * hex1.m_dot_s, s1[:, 0], ":")

    factor_out = hex1.find_pinch()
    ms, d_tempall_second, w1, s1 = hex1.pinch_plot()
    ax_plot.plot((w1[:, 2]-w1[:, 2].min()) * hex1.m_dot_w, w1[:, 0])
    ax_plot.plot((s1[:, 2]-s1[:, 2].min()) * hex1.m_dot_s, s1[:, 0], ":")
    # # print(f"w {w[0]}")
    # print("hex:",hex1.h_in_out)

    # p_out = 5e5

    # state_out = throttle(p_out, myFluid)
    # print("Throttle:\nInput:", state_in,"\nOutput:",
    # state_out,"\nDifference", state_out-state_in)
