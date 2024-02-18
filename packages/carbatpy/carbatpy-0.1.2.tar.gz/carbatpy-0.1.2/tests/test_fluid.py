# -*- coding: utf-8 -*-
"""
first test for fluid


Created on Sun Oct 15 18:07:07 2023

@author: atakan
"""


import unittest
import carbatpy as cb
# import src.models.fluids.fluid_props as fprop
# import src.models.components.throttle_simple as throt


class TestFluidModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """We only want to pull this data once for each TestCase since it is
        an expensive operation"""

        fluid_mixture = "Propane * Pentane"
        self.flm = cb.fprop.FluidModel(fluid_mixture)

    def test_fluid_values(self):
        """ensures that the expected enthalpies are correct"""
        fluid_mixture = "Propane * Pentane"
        self.flm = cb.fprop.FluidModel(fluid_mixture)
        print(self.flm.fluid)
        comp = [.50, 0.5]
        self.my_fluid = cb.fprop.Fluid(self.flm, comp)
        st0 = self.my_fluid.set_state([300., 1e5], "TP")
        self.assertAlmostEqual(self.my_fluid.properties.enthalpy,
                               453021.3769789692, places=14)

        # fluid, different composition
        st0 = self.my_fluid.set_state([300., 1e5], "TP", composition=[.35, .65])
        self.assertAlmostEqual(self.my_fluid.properties.enthalpy,
                               414499.55081964, places=14)

        # Water
        self.flm = cb.fprop.FluidModel("Water")
        self.my_fluid = cb.fprop.Fluid(self.flm, [1])
        st0 = self.my_fluid.set_state([300., 1e5], "TP")
        self.assertAlmostEqual(self.my_fluid.properties.enthalpy,
                               112653.67968890067, places=14)
        print(self.flm.fluid)

    def test_throttle(self):
        # throttle:
        fluid_mixture = "Propane * Pentane"
        self.flm = cb.fprop.FluidModel(fluid_mixture)
        print(self.flm.fluid)
        comp = [.50, 0.5]
        self.my_fluid = cb.fprop.Fluid(self.flm, comp)
        state_in = self.my_fluid.set_state([320., 19e5], "TP")
        p_out = 5e5
        state_out = cb.throttle_simple.throttle(p_out, self.my_fluid)
        self.assertAlmostEqual(self.my_fluid.properties.enthalpy,
                               143230.6314641813, places=14)

    def test_heat_pump_simple_v2(self):


        fluid_mixture = "Propane * Ethane * Pentane *Isobutane"
        # comp = [.75, 0.05, 0.15, 0.05]
        x1 = 0.25
        x2 = 0.05
        x3 = 0.05
        x4 = 1 - x1-x2-x3
        comp = [x1, x2, x3, x4]  # [0.164,.3330,.50300,0.0]
        print(f"{fluid_mixture}, composition:\n{comp}")
        temp_surrounding = 273.15+20
        fluid_storage = "Water"  #
        fluid_cold_storage = "Water"  # "Methanol"  # "Water"  #

        flm = cb.fprop.FluidModel(fluid_mixture)
        my_fluid = cb.fprop.Fluid(flm, comp)

        sec_fluid_model = cb.fprop.FluidModel(fluid_storage)
        sec_fluid = cb.fprop.Fluid(sec_fluid_model, [1.])

        cold_fluid_model = cb.fprop.FluidModel(fluid_cold_storage)
        cold_fluid = cb.fprop.Fluid(cold_fluid_model, [1.])

        # Condenser(c) and storage (s), secondary fluids fix all, temperatures(T in K),
        # pressures (p in Pa)
        _eta_s_ = 0.57  # interesting when changed from 0.69 to 0.65, the efficiency
        # decreases, the reason is the low quality along throtteling then
        _storage_temp_in = 273.15 + 50
        _cold_storage_temp_in = temp_surrounding
        _storage_temp_out_ = 273.15 + 60  # 395.0
        _cold_storage_temp_out_ = 284.15
        _storage_pres_in_ = 5e5
        _cold_storage_pres_in_ = 5e5
        _q_dot_required_ = 1e3  # and heat_flow rate (W)
        _D_T_SUPER_ = 15  # super heating of working fluid
        _temp_diff_min_ = 4.  # minimum approach temperature (pinch point)
        # high T-storages
        state_sec_out = sec_fluid.set_state(
            [_storage_temp_out_, _storage_pres_in_], "TP")
        state_sec_in = sec_fluid.set_state(
            [_storage_temp_in, _storage_pres_in_], "TP")

        #  low T sorages:
        state_cold_out = cold_fluid.set_state(
            [_cold_storage_temp_out_, _cold_storage_pres_in_], "TP")
        state_cold_in = cold_fluid.set_state(
            [_cold_storage_temp_in, _cold_storage_pres_in_], "TP")

        # working fluid
        T_DEW = _storage_temp_out_  # + _temp_diff_min_
        state_in_cond = my_fluid.set_state(
            [T_DEW, 1.], "TQ")  # find high pressure
        state_out_cond = my_fluid.set_state([_storage_temp_in + _temp_diff_min_,
                                            state_in_cond[1]], "TP")
        state_satv_evap = my_fluid.set_state(
            [_storage_temp_in-_temp_diff_min_-_D_T_SUPER_, 1.], "TQ")  # find minimum pressure
        p_low = state_satv_evap[1]

        T_IN = _storage_temp_in - _temp_diff_min_

        state_out_evap = my_fluid.set_state([p_low,
                                            T_IN], "PT")

        FIXED_POINTS = {"eta_s": _eta_s_,
                        "p_low": state_out_evap[1],
                        "p_high": state_in_cond[1],
                        "T_hh": _storage_temp_out_,
                        "h_h_out_sec": state_sec_out[2],
                        "h_h_out_w": state_out_cond[2],
                        "h_l_out_cold": state_cold_out[2],
                        "h_l_out_w": state_out_evap[2],
                        "T_hl": _storage_temp_in,
                        "T_lh": _storage_temp_in,
                        "T_ll": _cold_storage_temp_out_,  # 256.0,
                        "Q_dot_h": _q_dot_required_,
                        "d_temp_min": _temp_diff_min_}

        print(
            f"p-ratio: {state_in_cond[1]/state_out_evap[1]: .2f}, p_low: {state_out_evap[1]/1e5: .2} bar")
        hp0 = cb.hp_simple.HeatPump(
            [my_fluid, sec_fluid, cold_fluid], FIXED_POINTS)
        cop = hp0.calc_p_high(FIXED_POINTS["p_high"], verbose=False)
        hp0.hp_plot()
        out = hp0.evaluation
        print(
            f"COP: {cop},p-ratio: {out['p_high']/out['p_low']:.2f}, p_low {out['p_low']/1e5:.2f} bar")
        print(
            f"COP: {cop},p-ratio: {out['p_high']/out['p_low']}, p_low {out['p_low']/1e5}")
        print(
            f'exergy loss rate: {out["exergy_loss_rate"]}, eff: {1-out["exergy_loss_rate"]/out["Power"]:.4f}')

        self.assertAlmostEqual(cop,
                               3.2679531973379765, places=14)
        self.assertAlmostEqual(out["exergy_loss_rate"],
                               185.3145101271498, places=14)
        self.assertAlmostEqual(1-out["exergy_loss_rate"]/out["Power"],
                               0.39440085411686,
                               places=14)

    def test_fluid_screening(self):
        # mixture search:
        # ["DME", "Ethane", "Butane","CO2"]
        fluids_all = ["Propane", "Ethane", "Pentane", "Butane"]
        T_low = 285.00
        T_high = 363.00
        p_low = 10e4
        p_high = 22e5
        dir_name = cb._RESULTS_DIR + r"\testing"
        temp_limit = True
        results = cb.property_eval_mixture.mixture_search(fluids_all, [T_low, T_high], [p_low, p_high],
                                                          dir_name, resolution=21, temp_limit=temp_limit)
        self.assertAlmostEqual(results["results_DataFrame"]["COP_is"].max(),
                               3.7777223672974976, places=14)


if __name__ == "__main__":
    unittest.main()
