from typing import Any, List, Dict, Tuple, Union, Optional
from dataclasses import dataclass

import numpy as np


class BuckleyLeverett:
    # phase mobility
    @staticmethod
    def mobility_phase(s, kr_phase, visc_phase):
        return kr_phase(s) / visc_phase

    # fractional flow function
    @staticmethod
    def fractional_flow_function(s, mob_displacing_phase, mob_displaced_phase):
        return np.divide(mob_displacing_phase(s), mob_displacing_phase(s) + mob_displaced_phase(s))

    # numerical derivative
    @staticmethod
    def derivative_numeric(f, start, end, step=0.00001):
        N = int(np.floor((end - start) / step)) if step else 10000
        u = np.linspace(start, end, N + 1)
        df_du_values = np.diff(f(u)) / np.diff(u)
        return lambda x: np.interp(
            x, u, np.concatenate(([df_du_values[0]], df_du_values), axis=0)
        )

    @staticmethod
    # get front solution
    def get_front_solution(
        kr_wet_phase=None,
        kr_non_wet_phase=None,
        visc_wet_phase=1.0,
        visc_non_wet_phase=1.0,
        sat_wet_inj=1.0,
        sat_wet_init=0.0,
    ):
        """
        Get saturation at the front
        """
        from scipy.optimize import minimize, root
        import matplotlib.pyplot as plt

        m1 = lambda s: BuckleyLeverett.mobility_phase(s, kr_wet_phase, visc_wet_phase)
        m2 = lambda s: BuckleyLeverett.mobility_phase(s, kr_non_wet_phase, visc_non_wet_phase)
        f = lambda s: BuckleyLeverett.fractional_flow_function(s, m1, m2)
        df_ds = BuckleyLeverett.derivative_numeric(f, sat_wet_init, sat_wet_inj)

        # residual = lambda x: df_ds(x)-(f(x)-f(s_init))/(x-s_init)
        # s0 = 0.5*(s_init+s_inj)
        # s_bounds = ((s_init+0.01, s_inj-0.01),)
        # result = minimize(residual,s0,
        #                   bounds=s_bounds,
        #                   method='Nelder-Mead',
        #                  )
        # result = root(residual, s0)
        # s_front = result.x[0]
        # v_front = df_ds(s_front)
        # v_front = (f(s_front)-f(s_init))/(s_front-s_init)

        s = np.linspace(sat_wet_init, sat_wet_inj, 10001)
        s_idx = np.argmax((f(s[1:]) - f(sat_wet_init)) / (s[1:] - sat_wet_init))
        s_front = s[s_idx]
        v_front = df_ds(s_front)

        s_avg = sat_wet_init + (1.0 - f(sat_wet_init)) / v_front
        # s_avg = s_init + (s_front-s_init)*(1.0-f(s_init))/(f(s_front)-f(s_init))

        s = np.linspace(sat_wet_init, sat_wet_inj, 10001)
        # plt.plot(s,df_ds(s),color='blue')
        # plt.plot(s,(f(s)-f(s_init))/(s-s_init),color='green')
        plt.plot(s, f(s))
        plt.plot([sat_wet_init, s_front, s_avg], [f(sat_wet_init), f(s_front), 1.0])
        plt.axvline(s_front, linestyle="--", color="red")
        plt.axvline(s_avg, linestyle="--", color="red")
        plt.text(s_front - 0.05, 0.01, "Swf")
        plt.text(s_avg, 0.9, "Swavg")
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.xlabel("Saturation [-]")
        plt.ylabel("Fractional flow function [-]")
        plt.title("Fractional flow function")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.minorticks_on()
        plt.show()

        return s_front, v_front

    # get saturation profiles
    @staticmethod
    def get_saturation_profiles(
        td,
        xd,
        v_front,
        s_front,
        kr_wet_phase=None,
        kr_non_wet_phase=None,
        visc_wet_phase=1.0,
        visc_non_wet_phase=1.0,
        sat_wet_inj=1.0,
        sat_wet_init=0.0,
    ):
        """
        Get saturation profiles
        """
        m1 = lambda s: BuckleyLeverett.mobility_phase(s, kr_wet_phase, visc_wet_phase)
        m2 = lambda s: BuckleyLeverett.mobility_phase(s, kr_non_wet_phase, visc_non_wet_phase)
        f = lambda s: BuckleyLeverett.fractional_flow_function(s, m1, m2)

        ds = 0.001
        dfds = lambda s: np.diff(f(s)) / np.diff(s)
        ys = np.arange(start=s_front, stop=sat_wet_inj, step=ds)
        y = np.concatenate(([sat_wet_inj], ys[::-1], [sat_wet_init]), axis=0)
        v = dfds(ys)[::-1]
        v = np.concatenate(([0.0], [v[0]], v, [v_front]), axis=0)
        sat_prof = lambda t: np.interp(
            xd,
            np.concatenate((v * t, [1.0]), axis=0),
            np.concatenate((y, [sat_wet_init]), axis=0),
        )

        s = []
        for i in range(0, len(td)):
            s.append(sat_prof(td[i]))
        return np.asarray(s)

    # get pressure profiles
    @staticmethod
    def get_pressure_profiles(
        td,
        xd,
        v_front,
        s_front,
        kr_wet_phase=None,
        kr_non_wet_phase=None,
        visc_wet_phase=1.0,
        visc_non_wet_phase=1.0,
        sat_wet_inj=1.0,
        sat_wet_init=0.0,
    ):
        """
        Get pressure profiles
        """
        m1 = lambda s: BuckleyLeverett.mobility_phase(s, kr_wet_phase, visc_wet_phase)
        m2 = lambda s: BuckleyLeverett.mobility_phase(s, kr_non_wet_phase, visc_non_wet_phase)
        mt = lambda s: m1(s) + m2(s)
        f = lambda s: BuckleyLeverett.fractional_flow_function(s, m1, m2)

        # ds_step = 0.001
        ds_step = 0.0001
        ds = lambda s: np.diff(s)
        dfds = lambda s: np.diff(f(s)) / np.diff(s)
        dmtds = lambda s: np.diff(mt(s)) / np.diff(s)

        sat_all = np.concatenate(
            (np.arange(start=s_front, stop=sat_wet_inj, step=ds_step), [sat_wet_inj]), axis=0
        )
        sat_v_all = dfds(sat_all)
        sat_v_all = np.concatenate(([v_front], sat_v_all), axis=0)
        dfds_value = lambda s: np.interp(s, sat_all, sat_v_all)
        # breakthrough time
        tbt = 1 / v_front
        # end saturation
        x_end = 1.0
        s_end = (
            lambda t: s_front
            if t < tbt
            else np.interp(x_end, t * sat_v_all[::-1], sat_all[::-1])
        )

        # pressure gradient integral
        def dp_int(s_end_value):
            sat = np.concatenate(
                (np.arange(start=s_end_value, stop=sat_wet_inj, step=ds_step), [sat_wet_inj]),
                axis=0,
            )
            if len(sat) <= 1:
                return 0
            dsat = np.concatenate(([ds_step], ds(sat)), axis=0)
            sat_v = dfds(sat)
            sat_v = np.concatenate(
                ([v_front if s_end_value <= s_front else sat_v[0]], sat_v), axis=0
            )
            dv = np.diff(sat_v)
            return -0.5 * (np.sum(dv / mt(sat[:-1])) + np.sum(dv / mt(sat[1:])))

        # before breakthrough
        dp_bt = dp_int(s_front)

        # pressure difference
        def dp_dt_cal(t):
            s_end_value = s_end(td[i])
            if td[i] < tbt:
                # calculate pressure difference behind front
                dp_behind = td[i] * dp_bt
                # calculate pressure difference infront
                dp_infront = (1.0 - v_front * td[i]) / mt(sat_wet_init)
                return dp_behind + dp_infront
            else:
                dp_behind = td[i] * dp_int(s_end_value)
                return dp_behind

        # pressure
        dpd = []
        for i in range(0, len(td)):
            dp = dp_dt_cal(td[i])
            dpd.append(dp)
            dp_prev = dp
        return np.asarray(dpd)

    # get average saturation
    @staticmethod
    def get_average_saturation(
        td,
        xd,
        v_front,
        s_front,
        kr_wet_phase=None,
        kr_non_wet_phase=None,
        visc_wet_phase=1.0,
        visc_non_wet_phase=1.0,
        sat_wet_inj=1.0,
        sat_wet_init=0.0,
    ):
        """
        Get average saturation along the core
        """
        m1 = lambda s: BuckleyLeverett.mobility_phase(s, kr_wet_phase, visc_wet_phase)
        m2 = lambda s: BuckleyLeverett.mobility_phase(s, kr_non_wet_phase, visc_non_wet_phase)
        mt = lambda s: m1(s) + m2(s)
        f = lambda s: BuckleyLeverett.fractional_flow_function(s, m1, m2)
        dfds = lambda s: np.diff(f(s)) / np.diff(s)
        #
        ds_step = 0.0001
        sat_all = np.concatenate(
            (np.arange(start=s_front, stop=sat_wet_inj, step=ds_step), [sat_wet_inj]), axis=0
        )
        sat_v_all = dfds(sat_all)
        sat_v_all = np.concatenate(([v_front], sat_v_all), axis=0)
        # breakthrough time
        tbt = 1.0 / v_front
        # end saturation
        x_end = 1.0
        s_end = (
            lambda t: s_front
            if t < tbt
            else np.interp(x_end, t * sat_v_all[::-1], sat_all[::-1])
        )
        # s_avg_bt = (1.0-f(s_front))/v_front + s_front
        s_avg_bt = 1.0 / v_front + sat_wet_init
        s_avg = np.zeros(len(td))
        for idx, t in enumerate(td):
            if t < tbt:
                x_front = t * v_front
                # s = s_avg_bt
                s = s_avg_bt * x_front + sat_wet_init * (1.0 - x_front)
            else:
                x_front = t * v_front
                s_end_value = s_end(t)
                s = (1.0 - f(s_end_value)) / v_front + s_end_value
            s_avg[idx] = s
        return s_avg

    # get analytical Buckley-Leverett solution
    @staticmethod
    def solve(
        t,
        kr_wet_phase=None,
        kr_non_wet_phase=None,
        visc_wet_phase=1.0,
        visc_non_wet_phase=1.0,
        sat_wet_inj=1.0,
        sat_wet_init=0.0,
        qt=1.0,
        length=1.0,
        porosity=1.0,
        permeability=1.0,
        area=1.0,
    ):
        """
        Solve Buckley-Leverett problem
        """
        # dimensionless parameters
        x_ref = length
        tau = porosity * length * area / qt
        visc_ref = visc_wet_phase
        visc_wet_phase_d = visc_wet_phase / visc_ref
        visc_non_wet_phase_d = visc_non_wet_phase / visc_ref
        atm2bar = 1.01325
        units_convertion_factor = atm2bar / 3.6  # cm2*cP/mD*h in bars
        dp_ref = (
            units_convertion_factor * length * qt * visc_ref / (area * permeability)
        )
        q_ref = porosity * length * area

        s_front, v_front = BuckleyLeverett.get_front_solution(
            kr_wet_phase=kr_wet_phase,
            kr_non_wet_phase=kr_non_wet_phase,
            visc_wet_phase=visc_wet_phase_d,
            visc_non_wet_phase=visc_non_wet_phase_d,
            sat_wet_init=sat_wet_init,
            sat_wet_inj=sat_wet_inj,
        )
        # scale time
        td = t / tau

        # grid for the analytical solution
        dx_sol = 1 / 2**12
        xd = np.arange(start=0.5 * dx_sol, stop=1 + 0.5 * dx_sol, step=dx_sol)
        # saturation profile
        s = BuckleyLeverett.get_saturation_profiles(
            td,
            xd,
            v_front,
            s_front,
            kr_wet_phase=kr_wet_phase,
            kr_non_wet_phase=kr_non_wet_phase,
            visc_wet_phase=visc_wet_phase_d,
            visc_non_wet_phase=visc_non_wet_phase_d,
            sat_wet_init=sat_wet_init,
            sat_wet_inj=sat_wet_inj,
        )
        # pressure profile
        dpd = BuckleyLeverett.get_pressure_profiles(
            td,
            xd,
            v_front,
            s_front,
            kr_wet_phase=kr_wet_phase,
            kr_non_wet_phase=kr_non_wet_phase,
            visc_wet_phase=visc_wet_phase_d,
            visc_non_wet_phase=visc_non_wet_phase_d,
            sat_wet_init=sat_wet_init,
            sat_wet_inj=sat_wet_inj,
        )
        # average saturation behind the front
        savg = BuckleyLeverett.get_average_saturation(
            td,
            xd,
            v_front,
            s_front,
            kr_wet_phase=kr_wet_phase,
            kr_non_wet_phase=kr_non_wet_phase,
            visc_wet_phase=visc_wet_phase_d,
            visc_non_wet_phase=visc_non_wet_phase_d,
            sat_wet_init=sat_wet_init,
            sat_wet_inj=sat_wet_inj,
        )
        # upscale solution
        x = xd * x_ref
        dp = dpd * dp_ref
        q_phase1_init = sat_wet_init * q_ref
        q_phase1 = qt * t - (savg - sat_wet_init) * q_ref
        q_phase2 = qt * t - q_phase1

        # return x, s, dp, savg, q_phase1, q_phase2
        return BuckleyLeverettSolution(
            x=x,
            sat_wet=s,
            dp=dp,
            sat_wet_avg=savg,
            q_wet_phase=q_phase1,
            q_non_wet_phase=q_phase2,
        )


@dataclass
class BuckleyLeverettSolution:
    x: List
    sat_wet: List
    dp: List
    sat_wet_avg: List
    q_wet_phase: List
    q_non_wet_phase: List
