from typing import Any, List, Dict, Tuple, Union, Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np


class Analytics:

    # unsteady state interpretations
    @staticmethod
    def interpret_relperms(
        t,
        dp,
        q_wet_phase,
        q_non_wet_phase,
        visc_wet_phase,
        visc_non_wet_phase,
        sat_wet_init,
        length,
        area,
        permeability,
        porosity,
        method="jbn",
    ):
        """
        JBN (Johnson-Bossler-Naumann) method for interpreting relative permeabilities from Unsteady State Measurement,
        Johnson, E.F., D.P. Bossler, and V.O. Naumann.
        Calculation of Relative Permeability from Displacement Experiments, 1959.
        Transactions of the American Institute of Mining, Metallurgical, and Petroleum Engineers. Vol. 216, 370-372. <br>
        https://doi.org/10.2118/1023-G
        """

        # 1st order
        # dt = np.diff(dt)
        # dq_dt_phase_inj = np.diff(q_phase_inj)/dt
        # dq_dt_phase_prod = np.diff(q_phase_prod)/dt
        # dp_dt = np.diff(dp)/dt

        # 2nd order
        dt = t[2:] - t[:-2]
        dq_dt_phase_inj = (q_wet_phase[2:] - q_wet_phase[:-2]) / dt
        dq_dt_phase_prod = (q_non_wet_phase[2:] - q_non_wet_phase[:-2]) / dt
        dp_dt = (dp[2:] - dp[:-2]) / dt

        u_phase_inj = (1 / area) * dq_dt_phase_inj
        u_phase_disp = (1 / area) * dq_dt_phase_prod
        PV = area * length * porosity

        sat_end = sat_wet_init + (t[1:-1] * dq_dt_phase_inj - q_wet_phase[1:-1]) / PV
        kr_fact = (permeability / length) * (dp[1:-1] - t[1:-1] * dp_dt)
        atm2bar = 1.01325
        units_convertion_factor = atm2bar / 3.6  # 1cP*1cm2/1mD*h*bar
        kr_phase_inj = units_convertion_factor * visc_wet_phase * u_phase_inj / kr_fact
        kr_phase_disp = units_convertion_factor * visc_non_wet_phase * u_phase_disp / kr_fact
        return RelpermsInterpretationSolution(
            sat_wet=sat_end,
            kr_wet_phase=kr_phase_inj,
            kr_non_wet_phase=kr_phase_disp,
        )


@dataclass
class RelpermsInterpretationSolution:
    sat_wet: List
    kr_wet_phase: List
    kr_non_wet_phase: List