from typing import Tuple
from itertools import chain
import os
import subprocess

import numpy as np
import math

from coreflow import sat_funcs
from coreflow.simulators.docker_client import DockerClient
from coreflow.utils import os_utils

import re

# footbath = True
footbath = False

# centrifuge3D = True
centrifuge3D = False

LGR = False
# LGR = True

# NB   = 100
# clen = 10.

eclipse_precision = int(6)  # ECLIPSE
# eclipse_precision = int(8)  # OPM

outcore_length_factor = np.float64(0.15)

da_out_factor = np.float64(0.1)
dx_out_factor = np.float64(10.0)  # 18.0

oil_phase_name = "OIL"
wat_phase_name = "WATER"
gas_phase_name = "GAS"

phases = [oil_phase_name, wat_phase_name]
well_injectors = ["INJO", "INJW"]
well_injector = "INJ"
well_producer = "PROD"

with_explicit_init = True
# with_explicit_init = False  # use EQUIL keywod


# configure simulation case
class SimCaseConfig:
    pass


class UnitsSystem:
    name: str
    length_units_name: str
    darcy_constant: float
    time_factor: float
    length_factor: float
    area_factor: float
    volume_factor: float

    density_factor: float
    pressure_factor: float
    temperature_factor: Tuple[float, float]

    liquid_surface_volume_factor: float
    gas_surface_volume_factor: float
    reservoir_volume_factor: float

    liquid_surface_volume_rate_factor: float
    gas_surface_volume_rate_factor: float
    reservoir_volume_rate_factor: float

    def __init__(self, name):
        self.name = name
        if name in {"LAB"}:
            self.length_units_name = "LAB"

            self.time_factor = 1.0  # hour
            self.length_factor = 1.0  # cm
            self.area_factor = 1.0  # cm2
            self.volume_factor = 1.0  # cc or cm3

            self.liquid_surface_volume_factor = 1.0  # scc or scm3
            self.gas_surface_volume_factor = 1.0  # scc or scm3
            self.reservoir_volume_factor = 1.0  # rcc or rcm3

            self.liquid_surface_volume_rate_factor = 1.0  # scc/hr or scm3/hr
            self.gas_surface_volume_rate_factor = 1.0  # scc/hr or scm3/hr
            self.reservoir_volume_rate_factor = 1.0  # rcc/hr or rcm3/hr

            self.density_factor = 1.0  # gm/cc
            self.pressure_factor = 1.0  # atm
            self.temperature_factor = (1.0, 0.0)  # ºC

            self.darcy_constant = 3.6  # cP/hr/atm

        elif name in {"FIELD"}:
            self.length_units_name = "FIELD"

            self.time_factor = 1 / 24.0  # day
            self.length_factor = 0.0328084  # ft
            self.area_factor = 0.00107639111056  # ft2
            self.volume_factor = 0.3531466  # ft3

            self.liquid_surface_volume_factor = 6.289811e-6  # stb
            self.gas_surface_volume_factor = 0.035314666721488586  # Mscf
            self.reservoir_volume_factor = 6.289811e-6  # rb

            self.liquid_surface_volume_rate_factor = 0.0001509554584903705  # stb/day
            self.gas_surface_volume_rate_factor = 8.475520013157261e-07  # Mscf/day
            self.reservoir_volume_rate_factor = 0.0001509554584903705  # rb/day

            self.density_factor = 6.242797e-5  # lb/ft3
            self.pressure_factor = 0.0698611253025  # psi
            self.temperature_factor = (9.0 / 5.0, 32)  # ºF

            self.darcy_constant = 0.00112712  # cP/day/psi
        elif name in {"PVT-M"}:
            self.length_units_name = "METRES"

            self.time_factor = 1 / 24.0  # day
            self.length_factor = 0.01  # m
            self.area_factor = 1.0e-4  # m2
            self.volume_factor = 1.0e-6  # m3

            self.liquid_surface_volume_factor = 1.0e-6  # sm3
            self.gas_surface_volume_factor = 1.0e-6  # sm3
            self.reservoir_volume_factor = 1.0e-6  # sm3

            self.liquid_surface_volume_rate_factor = 2.4e-5  # sm3/day
            self.gas_surface_volume_rate_factor = 2.4e-5  # sm3/day
            self.reservoir_volume_rate_factor = 2.4e-5  # sm3/day

            self.density_factor = 1000.0  # kg/m3
            self.pressure_factor = 1.01325  # barsa
            self.temperature_factor = (1.0, 0.0)  # ºC

            self.darcy_constant = 0.00864  # cP/day/bar
        else:
            self.length_units_name = "METRES"

            self.time_factor = 1 / 24.0  # day
            self.length_factor = 0.01  # m
            self.area_factor = 1.0e-4  # m2
            self.volume_factor = 1.0e-6  # m3

            self.liquid_surface_volume_factor = 1.0e-6  # sm3
            self.gas_surface_volume_factor = 1.0e-6  # sm3
            self.reservoir_volume_factor = 1.0e-6  # sm3

            self.liquid_surface_volume_rate_factor = 2.4e-5  # sm3/day
            self.gas_surface_volume_rate_factor = 2.4e-5  # sm3/day
            self.reservoir_volume_rate_factor = 2.4e-5  # sm3/day

            self.density_factor = 1000.0  # kg/m3
            self.pressure_factor = 1.01325  # barsa
            self.temperature_factor = (1.0, 0.0)  # ºC

            self.darcy_constant = 0.00852702  # cP/day/bar

    def convert_time(self, value: float) -> float:
        return value * self.time_factor

    def convert_length(self, value: float) -> float:
        return value * self.length_factor

    def convert_area(self, value: float) -> float:
        return value * self.area_factor

    def convert_volume(self, value: float) -> float:
        return value * self.volume_factor

    def convert_liquid_surface_volume(self, value: float) -> float:
        return value * self.liquid_surface_volume_factor

    def convert_gas_surface_volume(self, value: float) -> float:
        return value * self.gas_surface_volume_factor

    def convert_reservoir_volume(self, value: float) -> float:
        return value * self.reservoir_volume_factor

    def convert_liquid_surface_volume_rate(self, value: float) -> float:
        return value * self.liquid_surface_volume_rate_factor

    def convert_gas_surface_volume_rate(self, value: float) -> float:
        return value * self.gas_surface_volume_rate_factor

    def convert_reservoir_volume_rate(self, value: float) -> float:
        return value * self.reservoir_volume_rate_factor

    def convert_density(self, value: float) -> float:
        return value * self.density_factor

    def convert_pressure(self, value: float) -> float:
        return value * self.pressure_factor

    def convert_compressibility(self, value: float) -> float:
        return value / self.pressure_factor

    def convert_temperature(self, value: float) -> float:
        return value * self.temperature_factor[0] + self.temperature_factor[1]

    def convert_transmissibility(self, value: float) -> float:
        return value * self.darcy_constant


# units_system = UnitsSystem("FIELD")
# units_system = UnitsSystem("PVT-M")
# units_system = UnitsSystem("METRIC")
units_system = UnitsSystem("LAB")


def grid_blocks(experiment_name, flooding, grid_type, num_grid_blocks, length):
    # cells along the core
    dl = np.float64(0.0)
    mult = []
    num_cells = int(num_grid_blocks)
    num_refined_cells = int(0)
    num_first_cells = int(0)
    num_last_cells = int(0)
    dlout_factor = np.float64(1.0)

    is_extended = grid_type in {
        "extended-core",
        "extended-core-refined",
        "centrifuge-core",
        "centrifuge-core-refined",
    }
    is_refined = grid_type in {
        "core-refined",
        "extended-core-refined",
        "centrifuge-core-refined",
    }

    if not is_extended:
        num_first_cells = int(0)
        num_last_cells = int(0)
    elif is_extended:
        num_first_cells = int(1)
        num_last_cells = int(1)

    # grid blocks ( inside )
    if not is_refined:
        dl = np.float64(length) / np.float64(num_grid_blocks)
        num_refined_cells = 0
    elif is_refined:
        # mult = [0.25, 0.25, 0.5]  # n = 3, l = 1.0
        mult = [0.1, 0.2, 0.4, 0.8]  # n = 4, l = 1.5
        # mult = [0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.4, 0.8]  # n = 8, l = 2.0
        # mult = [0.1, 0.1, 0.2, 0.2, 0.4, 0.4, 0.8, 0.8]  # n = 8, l = 3.0
        num_refined_cells = len(mult)
        dl = np.float64(length) / np.float64(
            num_grid_blocks - 2 * num_refined_cells + 2 * sum(mult)
        )

    # grid blocks ( outside )
    if not is_refined:
        dlout_factor = np.float64(1.0)
    elif is_refined:
        dlout_factor = np.float64(mult[0])

    dl_first = np.float64(dl * dlout_factor)
    dl_last = np.float64(dl * dlout_factor)
    dl_in = []
    dl_out = []
    if grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
        # if( footbath == True ):
        #    if( flooding == 'imbibition' ):
        #       num_top_cells += int( 1 )
        #    elif( flooding == 'drainage' ):
        #        num_bot_cells += int( 1 )

        # setup for centrifuge cells outside of the core
        inlet_length = np.float64(
            outcore_length_factor * length
        )  # 1.0 or [ 0.125 - 0.225 ]*length
        outlet_length = np.float64(1.0 * length)  # [ 0.125 - 0.225 ]*length
        # inlet_length  = np.float64( 0.15*length ) # 1.0 or [ 0.125 - 0.225 ]*length
        # outlet_length = np.float64( 0.15*length ) # [ 0.125 - 0.225 ]*length
        if is_refined:
            inlet_length = np.float64(0.1 * length)  # 1.0 or [ 0.125 - 0.225 ]*length
            outlet_length = np.float64(0.25 * length)  # [ 0.125 - 0.225 ]*length

        if flooding == "imbibition":
            top_length = outlet_length
            bot_length = inlet_length
        else:
            top_length = inlet_length
            bot_length = outlet_length

        num_top_cells = int(top_length / (dlout_factor * dl))
        num_bot_cells = int(bot_length / (dlout_factor * dl))
        if num_top_cells == 0:
            num_top_cells = int(1)
        if num_bot_cells == 0:
            num_bot_cells = int(1)

        if is_refined:
            num_total_fracs = np.float64(0.0)
            for i in range(0, num_first_cells):
                num_total_fracs += np.float64(i + 1)
            dl_first = np.float64(top_length / num_total_fracs)
            num_total_fracs = np.float64(0.0)
            for i in range(0, num_last_cells):
                num_total_fracs += np.float64(i + 1)
            dl_last = np.float64(bot_length.num_total_fracs)
            for i in range(0, num_first_cells):
                dl_in.append(np.float64((num_first_cells - i) * dl_first))
            for i in range(0, num_last_cells):
                dl_out.append(np.float64((i + 1) * dl_last))
        else:
            dl_first = np.float64(top_length / num_top_cells)
            dl_last = np.float64(bot_length / num_bot_cells)
            for i in range(0, num_top_cells):
                dl_in.append(np.float64(dl_first))
            for i in range(0, num_bot_cells):
                dl_out.append(np.float64(dl_last))

        num_first_cells = int(num_top_cells)
        num_last_cells = int(num_bot_cells)
    else:
        dl_in.append(round(np.float64(dl_first), eclipse_precision))
        dl_out.append(round(np.float64(dl_last), eclipse_precision))

    dl = round(dl, eclipse_precision)

    # total number of cells
    num_cells = int(num_grid_blocks + num_first_cells + num_last_cells)

    # initialize cells length
    dr = np.repeat(np.float64(dl), num_cells).tolist()

    # outside left/top
    for i in range(0, num_first_cells):
        dr[i] = np.float64(dl_in[i])
    # left/top refined
    for i in range(0, num_refined_cells):
        dr[num_first_cells + i] = np.float64(mult[i] * dl)
    # middle
    for i in range(0, num_grid_blocks - 2 * num_refined_cells):
        dr[num_first_cells + num_refined_cells + i] = np.float64(dl)
    # right/bottom refined
    for i in range(0, num_refined_cells):
        dr[num_first_cells + num_grid_blocks - num_refined_cells + i] = np.float64(
            mult[i] * dl
        )
    # outside right/bottom
    for i in range(0, num_last_cells):
        dr[num_grid_blocks + num_first_cells + i] = np.float64(dl_out[i])

    return num_cells, num_refined_cells, num_first_cells, num_last_cells, dl, dr.copy()


def centres_of_grid_blocks(
    experiment_name, flooding, grid_type, num_grid_blocks, length
):
    num_cells, num_refined_cells, num_first_cells, num_last_cells, dl, dr = grid_blocks(
        experiment_name, flooding, grid_type, num_grid_blocks, length
    )

    dl = np.float64(0.0)
    dxC = np.empty([num_grid_blocks, 1])
    for i in range(0, num_grid_blocks):
        dxC[i] = np.float64(dl + 0.5 * dr[i])
        dl += dr[i]

    return dxC.copy()


def blocked_mesh(NX, NY, NZ, dx, dy, dz, depth):
    # define poin coordinates
    NXY = np.int32((NX + 1) * (NY + 1))
    num_points = np.int32((NX + 1) * (NY + 1) * (NZ + 1))

    # initialize points array
    dim = np.int32(3)
    pxyz = []
    for pid in range(0, num_points):
        pxyz.append([])
        for cid in range(0, dim):
            pxyz[pid].append(np.float64(0.0))

    z = np.float64(-depth)
    for k in range(0, NZ + 1):
        y = np.float64(0.0)
        for j in range(0, NY + 1):
            x = np.float64(0.0)
            for i in range(0, NX + 1):
                pid = np.int32(k * NXY + j * (NX + 1) + i)
                pxyz[pid][0] = x
                pxyz[pid][1] = y
                pxyz[pid][2] = z

                if i != NX:
                    x += np.float64(dx[i])

            if j != NY:
                y += np.float64(dy[j])

        if k != NZ:
            z -= np.float64(dz[k])

    return pxyz.copy()


def get_mesh(
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    diameter,
    distance_to_inlet,
    depth,
    verbose=False,
):
    # grid parameters
    num_cells, num_refined_cells, num_first_cells, num_last_cells, dl, dr = grid_blocks(
        experiment_name, flooding, grid_type, num_grid_blocks, length
    )

    # cross sections cells
    da = np.float64(math.sqrt(math.pi)) * np.float64(diameter) / np.float64(2.0)
    da_out = np.float64(da_out_factor * da)

    nx_cells = (
        int(1)
        if (int(da / (dx_out_factor * dl)) == 0)
        else int(da / (dx_out_factor * dl))
    )
    nx_out_cells = (
        int(1)
        if (int(da_out / (dx_out_factor * dl)) == 0)
        else int(da_out / (dx_out_factor * dl))
    )
    ny_cells = int(1)
    ny_out_cells = int(1)

    dx = np.float64(da / nx_cells)
    dx_out = np.float64(da_out / nx_out_cells)
    dy = np.float64(da / ny_cells)
    dy_out = np.float64(da_out / ny_out_cells)

    dl = round(dl, eclipse_precision)
    da = round(da, eclipse_precision)
    da_out = round(da_out, eclipse_precision)
    dx = round(dx, eclipse_precision)
    dx_out = round(dx_out, eclipse_precision)
    dy = round(dy, eclipse_precision)
    dy_out = round(dy_out, eclipse_precision)

    dx_mesh = []
    dy_mesh = []
    dz_mesh = []

    core_cells = []
    outside_cells = []
    cells = []

    if (experiment_name == "SS") or (experiment_name == "USS"):
        # DX
        if (num_first_cells > 0) and (num_last_cells > 0) and (num_refined_cells > 0):
            for i in range(0, num_cells):
                dx_mesh.append(dr[i])

            # outside cells
            for i in range(0, num_first_cells):
                outside_cells.append(i)
                cells.append(i)

            # core cells
            for i in range(0, num_grid_blocks):
                core_cells.append(num_first_cells + i)
                cells.append(num_first_cells + i)

            # outside cells
            for i in range(0, num_last_cells):
                outside_cells.append(num_first_cells + num_grid_blocks + i)
                cells.append(num_first_cells + num_grid_blocks + i)

        elif num_refined_cells > 0:
            for i in range(0, num_cells):
                dx_mesh.append(dr[i])

            # core cells
            for i in range(0, num_grid_blocks):
                core_cells.append(i)
                cells.append(i)

        elif (num_first_cells > 0) and (num_last_cells > 0):
            for i in range(0, num_cells):
                dx_mesh.append(dr[i])

            # outside cells
            for i in range(0, num_first_cells):
                outside_cells.append(i)
                cells.append(i)

            # core cells
            for i in range(0, num_grid_blocks):
                core_cells.append(num_first_cells + i)
                cells.append(num_first_cells + i)

            # outside cells
            for i in range(0, num_last_cells):
                outside_cells.append(num_first_cells + num_grid_blocks + i)
                cells.append(num_first_cells + num_grid_blocks + i)

        else:
            for i in range(0, num_cells):
                dx_mesh.append(dl)

            # core cells
            for i in range(0, num_grid_blocks):
                core_cells.append(i)
                cells.append(i)

        # DY
        dy_mesh.append(da)

        # DZ
        dz_mesh.append(da)

    elif experiment_name == "CENT":
        if grid_type in {
            "core",
            "core-refined",
            "extended-core",
            "extended-core-refined",
        }:
            # DX
            dx_mesh.append(da)

            # DY
            dy_mesh.append(da)

            if (num_first_cells > 0) and (num_last_cells > 0):
                for i in range(0, num_first_cells):
                    dz_mesh.append(dr[i])
                for i in range(0, num_grid_blocks):
                    j = int(num_first_cells + i)
                    dz_mesh.append(dr[j])
                for i in range(0, num_last_cells):
                    dz_mesh.append(dr[num_first_cells + num_grid_blocks + i])

                # outside cells
                for i in range(0, num_first_cells):
                    outside_cells.append(i)
                    cells.append(i)

                # core cells
                for i in range(0, num_grid_blocks):
                    core_cells.append(num_first_cells + i)
                    cells.append(num_first_cells + i)

                # outside cells
                for i in range(0, num_last_cells):
                    outside_cells.append(num_first_cells + num_grid_blocks + i)
                    cells.append(num_first_cells + num_grid_blocks + i)

            else:
                for i in range(0, num_grid_blocks):
                    dz_mesh.append(dr[i])

                # core cells
                for i in range(0, num_grid_blocks):
                    core_cells.append(i)
                    cells.append(i)

        elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            # pseudo 2D model
            if not centrifuge3D:
                if grid_type in {"centrifuge-core-refined"}:
                    nx_cells_total = nx_cells + 2 * nx_out_cells
                    ny_cells_total = ny_cells
                    nxy_cells = (nx_cells + 2 * nx_out_cells) * ny_cells
                    nxy_left_cells = nx_out_cells * ny_cells
                    nxy_right_cells = nx_out_cells * ny_cells
                    nxy_centre_cells = nx_cells * ny_cells

                    # DX
                    for i in range(0, nx_out_cells):
                        dx_mesh.append(dx_out)
                    for i in range(0, nx_out_cells):
                        dx_mesh.append(dx)
                    for i in range(0, nx_out_cells):
                        dx_mesh.append(dx_out)

                    # DY
                    for i in range(0, ny_cells):
                        dx_mesh.append(dy)

                    # DZ
                    for i in range(0, num_first_cells):
                        dz_mesh.append(dr[i])
                    for i in range(0, num_grid_blocks):
                        j = int(num_first_cells + i)
                        dz_mesh.append(dr[j])
                    for i in range(0, num_last_cells):
                        dz_mesh.append(dr[num_first_cells + num_grid_blocks + i])

                    cid = int(0)
                    # outside cells
                    for i in range(0, num_first_cells):
                        for j in range(0, nxy_cells):
                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                    # core cells
                    for i in range(0, num_grid_blocks):
                        for j in range(0, nxy_cells):
                            core_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                    # outside cells
                    for i in range(0, num_last_cells):
                        for j in range(0, nxy_cells):
                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                else:
                    # DX
                    dx_mesh.append(da_out)
                    dx_mesh.append(da)
                    dx_mesh.append(da_out)

                    # DY
                    dy_mesh.append(da)

                    # DZ
                    for i in range(0, num_first_cells):
                        dz_mesh.append(dr[i])
                    for i in range(0, num_grid_blocks):
                        j = int(num_first_cells + i)
                        dz_mesh.append(dr[j])
                    for i in range(0, num_last_cells):
                        dz_mesh.append(dr[num_first_cells + num_grid_blocks + i])

                    cid = int(0)
                    temp_length = np.float64(0.0)
                    for i in range(0, num_first_cells):
                        temp_length += dr[i]
                        if (temp_length < (1.0 - outcore_length_factor) * length) and (
                            flooding == "imbibition"
                        ):
                            # deactivate cell
                            cid += 1

                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                            # deactivate cell
                            cid += 1

                        else:
                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                    for i in range(0, num_grid_blocks):
                        j = int(num_first_cells + i)

                        outside_cells.append(cid)
                        cells.append(cid)
                        cid += 1

                        core_cells.append(cid)
                        cells.append(cid)
                        cid += 1

                        outside_cells.append(cid)
                        cells.append(cid)
                        cid += 1

                    temp_length = np.float64(0.0)
                    for i in range(0, num_last_cells):
                        temp_length += dr[num_first_cells + num_grid_blocks + i]
                        if (temp_length > outcore_length_factor * length) and (
                            flooding == "drainage"
                        ):
                            # deactivate cell
                            cid += 1

                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                            # deactivate cell
                            cid += 1

                        else:
                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

                            outside_cells.append(cid)
                            cells.append(cid)
                            cid += 1

            else:
                nxy_cells = 9

                # DX
                dx_mesh.append(da_out)
                dx_mesh.append(da)
                dx_mesh.append(da_out)

                # DY
                dy_mesh.append(da_out)
                dy_mesh.append(da)
                dy_mesh.append(da_out)

                # DZ
                for i in range(0, num_first_cells):
                    dz_mesh.append(dr[i])
                for i in range(0, num_grid_blocks):
                    j = int(num_first_cells + i)
                    dz_mesh.append(dr[j])
                for i in range(0, num_last_cells):
                    dz_mesh.append(dr[num_first_cells + num_grid_blocks + i])

                cid = int(0)
                # outside cells
                for i in range(0, num_first_cells):
                    for j in range(0, nxy_cells):
                        outside_cells.append(cid)
                        cells.append(cid)
                        cid += 1

                # core cells
                for i in range(0, num_grid_blocks):
                    for j in range(0, nxy_cells):
                        core_cells.append(cid)
                        cells.append(cid)
                        cid += 1

                # outside cells
                for i in range(0, num_last_cells):
                    for j in range(0, nxy_cells):
                        outside_cells.append(cid)
                        cells.append(cid)
                        cid += 1

    NX = len(dx_mesh)
    NY = len(dy_mesh)
    NZ = len(dz_mesh)

    return (
        NX,
        NY,
        NZ,
        dx_mesh.copy(),
        dy_mesh.copy(),
        dz_mesh.copy(),
        cells.copy(),
        core_cells.copy(),
        outside_cells.copy(),
    )


def cell_points(NX, NY, NZ):
    NXYZ = np.int32(NX * NY * NZ)
    NXY = np.int32(NX * NY)
    cell_points = []
    for cid in range(0, NXYZ):
        cell_points.append([])
        for pid in range(0, 8):
            cell_points[cid].append(np.float64(0.0))

    for k in range(0, NZ):
        kOffset = np.int32((NX + 1) * (NY + 1) * k)

        for j in range(0, NY):
            jOffset = np.int32((NX + 1) * j)

            for i in range(0, NX):
                cid = np.int32(NXY * k + NX * j + i)

                # assign points to corresponding hexahedron
                cell_points[cid][0] = np.int32(kOffset + jOffset + i)
                cell_points[cid][1] = cell_points[cid][0] + 1
                cell_points[cid][2] = cell_points[cid][0] + (NX + 1)
                cell_points[cid][3] = cell_points[cid][2] + 1
                cell_points[cid][4] = cell_points[cid][0] + (NX + 1) * (NY + 1)
                cell_points[cid][5] = cell_points[cid][4] + 1
                cell_points[cid][6] = cell_points[cid][4] + (NX + 1)
                cell_points[cid][7] = cell_points[cid][6] + 1

    return cell_points.copy()


def cell_gravity_multipliers(
    sameGrav, num_cells, num_first_cells, num_last_cells, length, distance_to_inlet, dl
):
    # gravity multipliers
    gmult = [np.float64(1.0)] * num_cells

    if not sameGrav:
        # reference_distance = np.float64( distance_to_inlet + 0.5*length )
        reference_distance = np.float64(distance_to_inlet)

        if (num_first_cells > 0) and (num_last_cells > 0):
            depth = np.float64(distance_to_inlet)
            for i in range(0, num_first_cells):
                gmult[num_first_cells - i - 1] = np.float64(
                    (depth - 0.5 * dl[num_first_cells - i - 1]) / reference_distance
                )
                depth -= np.float64(dl[num_first_cells - i - 1])
            depth = np.float64(distance_to_inlet)
            for i in range(num_first_cells, num_cells - num_first_cells):
                gmult[i] = np.float64((depth + 0.5 * dl[i]) / reference_distance)
                depth += np.float64(dl[i])
            for i in range(num_cells - num_last_cells, num_cells):
                gmult[i] = np.float64((depth + 0.5 * dl[i]) / reference_distance)
                depth += np.float64(dl[i])
        else:
            depth = np.float64(distance_to_inlet)
            for i in range(0, num_cells):
                gmult = np.float64((depth + 0.5 * dl[i]) / reference_distance)
                depth += np.float64(dl[i])

    return gmult.copy()


def calculate_hydrostatic_pressure(
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    distance_to_inlet,
    pressure_init,
    gravcons,
    density_core,
    density_outside,
    sameGrav,
):
    # grid parameters
    num_cells, num_refined_cells, num_first_cells, num_last_cells, dl, dr = grid_blocks(
        experiment_name, flooding, grid_type, num_grid_blocks, length
    )
    gmult = cell_gravity_multipliers(
        sameGrav,
        num_cells,
        num_first_cells,
        num_last_cells,
        length,
        distance_to_inlet,
        dr,
    )

    press_inj = np.float64(pressure_init)
    press_prod = np.float64(pressure_init)

    if grid_type in {"core", "core-refined"}:
        press_core = [np.float64(0.0)] * num_grid_blocks
        press_outside = [np.float64(0.0)] * num_grid_blocks
        press_core[0] = np.float64(0.0)
        press_outside[0] = np.float64(0.0)
        for i in range(0, num_grid_blocks):
            press_in = density_core * gmult[i] * gravcons * np.float64(0.5 * dr[i])
            press_out = density_outside * gmult[i] * gravcons * np.float64(0.5 * dr[i])
            press_core[i] += press_in
            press_outside[i] += press_out
            if i != num_grid_blocks - 1:
                press_core[i + 1] = press_core[i] + press_in
                press_outside[i + 1] = press_outside[i] + press_out
        if flooding == "drainage":
            press_prod = press_core[num_cells - 1]
            # press_prod = press_outside[ num_cells - 1 ]
        elif flooding == "imbibition":
            press_inj = press_core[num_cells - 1]
            # press_inj  = press_outside[ num_cells - 1 ]

    elif grid_type in {
        "extended-core",
        "extended-core-refined",
        "centrifuge-core",
        "centrifuge-core-refined",
    }:
        press_core = [np.float64(0.0)] * num_grid_blocks
        press_outside = [np.float64(0.0)] * num_cells

        press_outside[0] = pressure_init
        for i in range(0, num_first_cells):
            j = int(i)
            press_out = np.float64(
                density_outside * gmult[j] * gravcons * np.float64(0.5 * dr[j])
            )
            press_outside[j] += press_out
            press_outside[j + 1] = press_outside[j] + press_out
            if i == num_first_cells - 1:
                press_core[0] = press_outside[j + 1]

        for i in range(0, num_grid_blocks):
            j = int(i + num_first_cells)
            press_in = np.float64(
                density_core * gmult[j] * gravcons * np.float64(0.5 * dr[j])
            )
            press_out = np.float64(
                density_outside * gmult[j] * gravcons * np.float64(0.5 * dr[j])
            )
            press_core[i] += press_in
            press_outside[j] += press_out
            if i != num_grid_blocks - 1:
                press_core[i + 1] = press_core[i] + press_in
            press_outside[j + 1] = press_outside[j] + press_out

        for i in range(0, num_last_cells):
            j = int(num_cells - num_last_cells + i)
            press_out = np.float64(
                density_outside * gmult[j] * gravcons * np.float64(0.5 * dr[j])
            )
            press_outside[j] += press_out
            if i != num_last_cells - 1:
                press_outside[j + 1] = press_outside[j] + press_out

        if flooding == "drainage":
            press_prod = press_outside[num_cells - 1]
        elif flooding == "imbibition":
            press_inj = press_outside[num_cells - 1]

    return press_inj, press_prod, press_core.copy(), press_outside.copy()


# run opm flow simulator
def run_opm_simulator(wdir, sim_dir, data_file, verbose=False, **kwargs):
    # get opm docker image
    image_name = "openporousmedia/opmreleases"
    # version = "latest"
    version = "2023.10"
    # version = "2023.04"
    # version = "2022.10"
    # version = "2021.10"
    # version = "2020.10"
    # version = "2019.10"
    # version = "2018.10"
    # version = "2018.04"
    # version = "2017.10"
    # version = "2017.04"
    image = f"{image_name}:{version}"
    client = DockerClient()
    client.pull_image(image_name, version=version)
    # define directories
    shared_host_dir = client.SharedHostDir
    sim_data_file = os.path.join(shared_host_dir, sim_dir, data_file)
    output_dir = os.path.join(shared_host_dir, sim_dir)
    if verbose:
        print(f"wdir={wdir}")
        print(f"sim_dir={sim_dir}")
        print(f"data_file={data_file}")

    # run simulator
    project_name = os_utils.get_filename(data_file)
    if verbose:
        print(f"Start 'opm-flow' simulation: '{project_name}' ...")
    cmd = f'flow --output-dir="{output_dir}" {sim_data_file}'

    # parameters
    params = {
        #'enable-tuning': True, # default False
        #'enable-terminal-output': False, # default True
        #'output-extra-convergence-info': "'steps'",
        #'solver-continue-on-convergence-failure': 1, # default: False
        # "linear-solver-max-iter": 200,  # default: 200
        "linear-solver-verbosity": 3,  # default: 0
        "solver-max-restarts": 15,  # default 10
        "solver-min-time-step": 1.0e-15,  # default 1.0e-12
        "use-gmres": True,  # default: False
        # "newton-max-iterations": 12,  # default: 20, too many iteration is also harmful
        # "newton-min-iterations": 2,  # default: 1
        #'tolerance-mb': 1.0e-7, # default: 1.0e-6
        #'tolerance-cnv': 0.001, # default 0.01
        #'linear-solver': "cpr", # # not always performs better. In 2022.10 alias for cpr_trueimpes, in 2023.04 alias for cprw
        #'linear-solver': "cpr_quasiimpes",
        #'linear-solver': "cpr_trueimpes",
        #'linear-solver': "cprw",
        #'linear-solver': "amg", # throws: Preconditioner type amg is not registered in the factory. Available types are: GS ILU0 ILUn Jac ParOverILU0 SOR SSOR cpr cprt cprw
        #'scale-linear-system': 1,
        #'max-welleq-iter': 50, # default: 30,
        #'max-newton-iterations-with-inner-well-iterations': 20, # default 8
        #'solve-welleq-initially': False, # default True
        #'matrix-add-well-contributions': True, # default False
        #'max-residual-allowed': 1e+03, # default 1.0e7
        #'tolerance-well-control': 1.0e-6, # default 1e-7
        #'tolerance-wells': 1.0e-3, # default 1.0e-4
    }

    def add_parameters(d):
        s = ""
        for k, v in d.items():
            s += f" --{k}={v}"
        return s

    cmd += add_parameters(params)

    client.run_container(image, cmd, host_dir=wdir, stream_logs=True, remove=True)

    if verbose:
        print(f"Finished 'opm-flow' simulation: '{project_name}'!")


# run 'Eclipse' simulator
def run_eclipse_simulator(wdir, sim_dir, data_file, verbose=False, **kwargs):
    # run simulator
    project_name = os_utils.get_filename(data_file)
    if verbose:
        print(f"Start 'Eclipse' simulation: '{project_name}' ...")
    # eclipse data file path
    sim_data_file = os.path.join(wdir, sim_dir, data_file)
    subprocess.call(["eclrun", "eclipse", sim_data_file], shell=True)
    if verbose:
        print(f"Finished 'Eclipse' simulation: '{project_name}'!")


# run 'tNavigator' simulator
def run_tnav_simulator(wdir, sim_dir, data_file, verbose=False, **kwargs):
    # run simulator
    project_name = os_utils.get_filename(data_file)
    if verbose:
        print(f"Start 'tNavigator' simulation: '{project_name}' ...")
    # eclipse data file path
    sim_data_file = os.path.join(wdir, sim_dir, data_file)
    subprocess.call(
        [
            "tNavigator-con.exe",
            "--ecl-root",
            "--ecl-egrid",
            "--ecl-init",
            "--ecl-unrst",
            "--touch-after",
            "eclend",
            "--no-gui",
            sim_data_file,
        ],
        shell=True,
    )
    if verbose:
        print(f"Finished 'tNavigator' simulation: '{project_name}'!")


def run_simulator(wdir, sim_dirname, project_name, verbose, **kwargs):
    # data file name
    data_file_name = project_name + ".data"

    # run simulator
    if "simulator" in kwargs:
        if isinstance(kwargs["simulator"], str):
            simulator_name = kwargs["simulator"].lower()
            if simulator_name in {"opm", "opm-flow", "flow"}:
                return run_opm_simulator(
                    wdir, sim_dirname, data_file_name, verbose=verbose
                )
            elif simulator_name in {"tnavigator", "tnav"}:
                return run_tnav_simulator(
                    wdir, sim_dirname, data_file_name, verbose=verbose
                )
            elif simulator_name in {"eclipse", "e100", "e300"}:
                return run_eclipse_simulator(
                    wdir, sim_dirname, data_file_name, verbose=verbose
                )
            else:
                raise RuntimeError(
                    f"run_simulator(): Unknown simulator name '{simulator_name}'!"
                )
        else:
            return kwargs["simulator"](
                wdir, sim_dirname, data_file_name, verbose=verbose
            )
    return run_eclipse_simulator(wdir, sim_dirname, data_file_name, verbose=verbose)


def simulator_solution_files(wdir, project_name):
    # input eclipse SPEC files
    specs = os.path.join(wdir, project_name + ".FSMSPEC")
    summary = os.path.join(wdir, project_name + ".FUNSMRY")
    return specs, summary


def read_solution(
    wdir,
    project_name,
    num_wgnames,
    num_nums,
    obsdata_keywords,
    obsdata_type,
    obsdata_wgnames,
    obsdata_nums,
    obsdata_convfactors,
    verbose,
):
    # input eclipse SPEC files
    input_efname_specs, input_efname_summary = simulator_solution_files(
        wdir, project_name
    )

    data = []
    if not os_utils.check_file(input_efname_specs) or not os_utils.check_file(
        input_efname_summary
    ):
        return data

    # read line
    def __read_line(line):
        legacy_versions = False
        if legacy_versions:
            columns = line.strip().replace("'", "").replace(",", ".").split()
        reg_exp = "'[^']+'|[\w.,+-]+"
        columns = [
            c.replace("'", "").replace(",", ".").strip()
            for c in re.findall(reg_exp, line.strip())
        ]
        return columns

    # 1. read positions of simulated data
    if verbose:
        print(f"Start reading simulation data: '{project_name}' ...")
    # open input file
    with open(input_efname_specs, "r") as fin:
        # loop over lines to extract variables of interest
        # keywords
        keywords = []
        keywords_offset = 0
        num_obskeywords = len(obsdata_keywords)
        num_data_cols = int(num_obskeywords + 1)

        keywords_line = False
        wgnames_line = False
        nums_line = False

        are_keys_saved = False
        are_wgnames_saved = False
        are_nums_saved = False

        num_keywords = int(0)
        processed_wgnames = int(0)
        processed_nums = int(0)

        data_index = [-1 for _ in range(num_data_cols)]
        for line in fin:
            # read line
            columns = __read_line(line)
            clen = len(columns)
            if clen > 0:
                if columns[0] == "KEYWORDS":
                    keywords_line = True
                    num_keywords = int(columns[1])
                    keywords_offset = 0
                elif columns[0] == "WGNAMES":
                    wgnames_line = True
                    keywords_line = False
                    num_keywords = int(columns[1])
                    keywords_offset = 0
                elif columns[0] == "NUMS":
                    nums_line = True
                    wgnames_line = False
                    keywords_line = False
                    num_keywords = int(columns[1])
                    keywords_offset = 0
                elif keywords_line:
                    for i in range(0, clen):
                        keywords.append(columns[i])
                        if columns[i] == "TIME":
                            data_index[0] = int(i)
                    keywords_offset += clen
                elif wgnames_line and (not are_wgnames_saved):
                    for i in range(0, clen):
                        ki = keywords_offset + i
                        for j in range(0, num_obskeywords):
                            if (
                                (obsdata_type[j] == "WGNAMES")
                                and (columns[i] == obsdata_wgnames[j])
                                and (keywords[ki] == obsdata_keywords[j])
                            ):
                                data_index[j + 1] = int(ki)
                                processed_wgnames += 1
                                if processed_wgnames == num_wgnames:
                                    are_wgnames_saved = True
                                    break
                    keywords_offset += clen
                elif nums_line and (not are_nums_saved):
                    for i in range(0, clen):
                        ki = keywords_offset + i
                        for j in range(0, num_obskeywords):
                            if (
                                (obsdata_type[j] == "NUMS")
                                and (int(columns[i]) == obsdata_nums[j])
                                and (keywords[ki] == obsdata_keywords[j])
                            ):
                                data_index[j + 1] = int(ki)
                                processed_nums += 1
                                if processed_nums == num_nums:
                                    are_nums_saved = True
                                    break
                    keywords_offset += clen
            if keywords_line and (keywords_offset == num_keywords):
                keywords_line = False
                are_keys_saved = True
            if wgnames_line and (keywords_offset == num_keywords):
                wgnames_line = False
                are_wgnames_saved = True
            if nums_line and (keywords_offset == num_keywords):
                nums_line = False
                are_nums_saved = True
            # check whether all data has been read
            if are_keys_saved and are_wgnames_saved and are_nums_saved:
                break

    # save number of parameters
    num_keywords = len(keywords)
    # clear unused array
    del keywords
    if num_keywords == 0:
        return data

    # 2. read simulated data
    # open input file
    with open(input_efname_summary, "r") as fin:
        # Loop over lines to extract variables of interest
        parameters_line = False
        parameters = []
        for line in fin:
            # read line
            columns = __read_line(line)
            clen = len(columns)
            if clen > 0:
                if columns[0] == "PARAMS":
                    parameters_line = True
                elif parameters_line:
                    for i in range(0, clen):
                        parameters.append(columns[i])

                # check whether all data has been read
                if len(parameters) == num_keywords:
                    parameters_line = False
                    data_row = []
                    for i in range(0, num_data_cols):
                        data_row.append(np.float64(parameters[data_index[i]]))
                    for i in range(1, num_data_cols):
                        data_row[i] *= obsdata_convfactors[i - 1]
                    data.append(data_row)
                    del data_row
                    parameters = []
        del parameters
        if verbose:
            print(f"Finished reading simulation data: '{project_name}'!")
    return data


# ============================================================================
# DATA FILE: 'RUNSPEC' SECTION
# ============================================================================


def write_simulator_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    diameter,
    stage,
    simcontrol_data,
    num_reports,
    num_sw_points,
    sameGrav,
    verbose=False,
):
    """
    Unsupported keywords: NOECHO
    """
    # @TODO: create universal approach
    # legacy version
    # the code is kept for potential use in future
    legacy_versions = False

    filename = os.path.join(wdir, project_name)

    if experiment_name == "CENT":
        filename += str(stage) + ".data"
    elif experiment_name in {"SS", "USS"}:
        filename += ".data"

    # open file
    fout = open(filename, "w")

    # grid parameters
    num_cells, num_refined_cells, num_first_cells, num_last_cells, dl, dr = grid_blocks(
        experiment_name, flooding, grid_type, num_grid_blocks, length
    )

    # cross sections cells
    da = np.float64(math.sqrt(math.pi)) * np.float64(diameter) / np.float64(2.0)
    da_out = np.float64(da_out_factor * da)

    nx_cells = (
        int(1)
        if (int(da / (dx_out_factor * dl)) == 0)
        else int(da / (dx_out_factor * dl))
    )
    nx_out_cells = (
        int(1)
        if (int(da_out / (dx_out_factor * dl)) == 0)
        else int(da_out / (dx_out_factor * dl))
    )
    ny_cells = int(1)
    ny_out_cells = int(1)

    # runspec section
    fout.writelines(["RUNSPEC\n"])

    fout.writelines(["\nTITLE"])
    fout.writelines(["\n", project_name, "\n"])

    fout.writelines(["\nSTART"])
    fout.writelines(["\n\t1 'JAN' 2023\t/\n"])

    fout.writelines([f"\n{units_system.name}\n"])

    for phase in phases:
        fout.writelines([f"\n{phase}\n"])

    # @TODO: create universal approach
    # ECLIPSE:
    # fout.writelines(['\n-- this keyword requests that information required for the run-time monitoring option should be written to the Summary Specification file'])
    # fout.writelines(['\nMONITOR\n'])
    # OPM:

    # @TODO: create universal approach
    # ECLIPSE:
    # fout.writelines(['\n-- requests that a Restart Index file should be written at the end of the run'])
    # fout.writelines(['\nRSSPEC\n'])
    # OPM:

    # output settings
    # @TODO: create universal approach
    # ECLIPSE:
    # fout.writelines(['\n-- The message file feature is provided primarily for use by post-processors'])
    # fout.writelines(['\nMSGFILE'])
    # fout.writelines(['\n\t', str( 0 ), '\t/\n'])
    # OPM:

    fout.writelines(["\n-- this indicates that output files will be formatted"])
    fout.writelines(
        ["\n-- this includes SMSPEC, SUMMARY, GRID, INIT and RESTART files"]
    )
    fout.writelines(["\nFMTOUT\n"])

    fout.writelines(["\n-- this indicates that output files will be unified"])
    fout.writelines(
        ["\n-- this includes SMSPEC, SUMMARY, GRID, INIT and RESTART files"]
    )
    fout.writelines(["\nUNIFOUT\n"])

    if (experiment_name == "CENT") and (stage != 0):
        fout.writelines(
            [
                "\n-- This indicates that input files which may be either formatted or unformatted, such as restart files, are to be formatted"
            ]
        )
        fout.writelines(["\nFMTIN\n"])

        fout.writelines(
            [
                "\n-- This indicates that input files (for example Restart files), which may be either multiple or unified, are unified"
            ]
        )
        fout.writelines(["\nUNIFIN\n"])

        fout.writelines(["\n--SAVE"])
        fout.writelines(["\n-- save data to unified formatted file"])
        fout.writelines(["\n--\tFORMATTED\t/\n"])

    fout.writelines(
        [
            "\n-- this indicates that the saturation table end-point scaling option is to be used"
        ]
    )
    fout.writelines(["\n--ENDSCALE"])
    fout.writelines(["\n--'NODIR'\t'REVERS'\t1\t20\t/\n"])

    # old type of specs output
    # fout.writelines(['\nOPTIONS'])
    # fout.writelines(['\n\t258*\t1\t/\n'])

    # no limit for warnings about grid
    if experiment_name == "CENT":
        fout.writelines(["\nOPTIONS"])
        fout.writelines(["\n\t22*\t", str(10 * len(dr)), "\t196*\t", str(1), "\t/\n"])

    if grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
        fout.writelines(
            ["\n-- to allow transmissibility multipliers in negative direction"]
        )
        fout.writelines(["\nGRIDOPTS"])
        fout.writelines(["\n\tYES\t/\n"])

    # solver and convergence settings
    if experiment_name == "CENT":
        if grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            max_problems = int(10000)
            fout.writelines(
                ["\n-- incease critical number of problems: 100( default )"]
            )
            fout.writelines(["\nMESSAGES"])
            fout.writelines(
                [
                    "\n\t",
                    "3*\t",
                    str(max_problems),
                    "\t5*\t",
                    str(max_problems),
                    "\t/\n",
                ]
            )

            fout.writelines(["\n-- number of search directions for linear solver"])
            fout.writelines(["\nNSTACK"])
            fout.writelines(["\n\t", str(20), "\t/\n"])

            # fout.writelines(['\n-- CPR linear solver'])
            # fout.writelines(['\nCPR'])
            # fout.writelines(['\n\t', 'ORIGINAL', '\t/\n'])

    # dimensions

    # if grid_type in {"extended-core", "extended-core-refined"}:
    #     fout.writelines(['\nEQLDIMS'])
    #     fout.writelines(['\n-- number of equilibration regions'])
    #     fout.writelines(['\n\t', str(3),'\t/\n'])

    # elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
    #     fout.writelines(['\nEQLDIMS'])
    #     fout.writelines(['\n-- number of equilibration regions'])
    #     fout.writelines(['\n\t', str(2),'\t/\n'])

    #     fout.writelines(['\nFAULTDIM'])
    #     fout.writelines(['\n\t', str(4), '\t/\n'])

    if not with_explicit_init:
        fout.writelines(["\nEQLDIMS"])
        fout.writelines(["\n/\n"])

    fout.writelines(["\nWELLDIMS"])
    fout.writelines(
        [
            "\n-- max. number of wells\tnumber of layers( grid blocks ) connected to the well\t max number of groups\t max. number of wells in one group\t default values"
        ]
    )
    fout.writelines(
        [
            "\n\t",
            str(3),
            "\t",
            str(1),
            "\t",
            str(1),
            "\t",
            str(3),
            "\t/\n",
        ]
    )

    fout.writelines(["\n-- max number of related fluid model quantities"])
    fout.writelines(["\nTABDIMS"])
    fout.writelines(
        [
            "\n-- num of saturation tables\tnum of pvt tables\tnum of saturation nodes\tnum of pressure points in PVT table\tnum of FIP regions "
        ]
    )
    if experiment_name == "CENT":
        if not sameGrav:
            fout.writelines(
                [
                    "\n\t",
                    str(2),
                    "\t",
                    str(len(dr)),
                    "\t",
                    str(num_sw_points),
                    "\t1*\t",
                    str(2),
                    "\t/\n",
                ]
            )
        else:
            fout.writelines(
                [
                    "\n\t",
                    str(2),
                    "\t",
                    str(1),
                    "\t",
                    str(num_sw_points),
                    "\t1*\t",
                    str(2),
                    "\t/\n",
                ]
            )
    else:
        fout.writelines(
            [
                "\n\t",
                str(2),
                "\t",
                str(1),
                "\t",
                str(num_sw_points),
                "\t1*\t",
                str(2),
                "\t/\n",
            ]
        )

    fout.writelines(["\nDIMENS"])
    fout.writelines(["\n-- specifies the dimensions of the grid [ nx ny nz ]"])
    if (experiment_name == "SS") or (experiment_name == "USS"):
        if grid_type in {"core", "core-refined"}:
            fout.writelines(
                ["\n\t", str(num_grid_blocks), "\t", str(1), "\t", str(1), "\t/\n"]
            )
        elif grid_type in {"extended-core", "extended-core-refined"}:
            fout.writelines(
                ["\n\t", str(num_grid_blocks + 2), "\t", str(1), "\t", str(1), "\t/\n"]
            )
    elif experiment_name == "CENT":
        if grid_type in {"core", "core-refined"}:
            fout.writelines(
                ["\n\t", str(1), "\t", str(1), "\t", str(num_grid_blocks), "\t/\n"]
            )
        elif grid_type in {"extended-core", "extended-core-refined"}:
            fout.writelines(
                ["\n\t", str(1), "\t", str(1), "\t", str(num_grid_blocks + 2), "\t/\n"]
            )
        elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            if not centrifuge3D:
                if grid_type in {"centrifuge-core-refined"}:
                    fout.writelines(
                        [
                            "\n\t",
                            str(nx_cells + 2 * nx_out_cells),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(num_cells),
                            "\t/\n",
                        ]
                    )
                else:
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(num_cells), "\t/\n"]
                    )
            else:
                if grid_type in {"centrifuge-core-refined"}:
                    fout.writelines(
                        [
                            "\n\t",
                            str(nx_cells + 2 * nx_out_cells),
                            "\t",
                            str(ny_cells + 2 * ny_out_cells),
                            "\t",
                            str(num_cells),
                            "\t/\n",
                        ]
                    )
                else:
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(3), "\t", str(num_cells), "\t/\n"]
                    )

    if experiment_name == "CENT":
        if grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            if LGR:
                last_block = len(dr) - 1
                if not centrifuge3D:
                    nxy_max = max(int(da / dl), int(da_out / dl))
                    nz_max = max(int(dr[0] / dl), int(dr[last_block] / dl))
                    nz_max = num_cells

                    maxlgr = int(9)
                    maxcls = int(nxy_max * nxy_max * nz_max)
                    mcoars = int(3 * num_cells)
                    mamalg = int(1)
                    mxlalg = int(9)
                    lstack = int(10)
                    nchcor = int(0)

                    fout.writelines(["\n-- local grid refinement specs"])
                    fout.writelines(["\nLGR"])
                    fout.writelines(
                        [
                            "\n-- MAXLGR( max number of local grids in model )\tMAXCLS( max. number of cells in each LGR )\tMCOARS( max. number of amalgamated coarse cells )\tMAMALG(max number of LGR amalgations)\tMXLALG(max number of LGRs in any amalgations)\tLSTACK( length of the stack of previous search directions used by the linear solver for LGR simulations )\tINTERP(NOINTERP)(pressure interpolation)\tNCHCOR(num of grid cells )"
                        ]
                    )
                    # fout.writelines(['\n\t', str( maxlgr ), '\t', str( maxcls ), '\t', str( mcoars ), '\t', str( mamalg ), '\t', str( mxlalg ), '\t', str( lstack ), '\t', '\'INTERP\'', '\t', str( nchcor ), '\t/\n'])
                    fout.writelines(
                        [
                            "\n\t",
                            str(maxlgr),
                            "\t",
                            str(maxcls),
                            "\t",
                            str(mcoars),
                            "\t",
                            str(mamalg),
                            "\t",
                            str(mxlalg),
                            "\t/\n",
                        ]
                    )
                else:
                    nxy_max = max(int(da / dl), int(da_out / dl))
                    nz_max = num_cells

                    maxlgr = int(27)
                    maxcls = int(nxy_max * nxy_max * num_cells)
                    mcoars = int(9 * num_cells)
                    mamalg = int(1)
                    mxlalg = int(27)

                    lstack = int(10)
                    nchcor = int(0)

                    fout.writelines(["\n-- local grid refinement specs"])
                    fout.writelines(["\nLGR"])
                    fout.writelines(
                        [
                            "\n-- MAXLGR( max number of local grids in model )\tMAXCLS( max. number of cells in each LGR )\tMCOARS( max. number of amalgamated coarse cells )\tMAMALG(max number of LGR amalgations)\tMXLALG(max number of LGRs in any amalgations)\tLSTACK( length of the stack of previous search directions used by the linear solver for LGR simulations )\tINTERP(NOINTERP)(pressure interpolation)\tNCHCOR(num of grid cells )"
                        ]
                    )
                    # fout.writelines(['\n\t', str( maxlgr ), '\t', str( maxcls ), '\t', str( mcoars ), '\t', str( mamalg ), '\t', str( mxlalg ), '\t', str( lstack ), '\t', '\'INTERP\'', '\t', str( nchcor ), '\t/\n'])
                    fout.writelines(
                        [
                            "\n\t",
                            str(maxlgr),
                            "\t",
                            str(maxcls),
                            "\t",
                            str(mcoars),
                            "\t",
                            str(mamalg),
                            "\t",
                            str(mxlalg),
                            "\t/\n",
                        ]
                    )
    # grid section
    fout.writelines(["\nGRID\n"])

    if legacy_versions:
        fout.writelines(["\nNOECHO\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_GOPP.INC'\t/\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_GGO.INC'\t/\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_GPRO.INC'\t/\n"])

    # properties section
    fout.writelines(["\nPROPS\n"])

    if legacy_versions:
        fout.writelines(["\nNOECHO\n"])

    if experiment_name == "CENT":
        if flooding == "imbibition":
            fout.writelines(["\nGRAVCONS"])
            fout.writelines(
                ["\n-- gravity acceleration [cm2atm/gm], default value: 0.000968"]
            )
            fout.writelines(["\n\t", str(simcontrol_data[stage][0][0]), "\t/\n"])
        elif flooding == "drainage":
            fout.writelines(["\nGRAVCONS"])
            fout.writelines(
                ["\n-- gravity acceleration [cm2atm/gm], default value: 0.000968"]
            )
            fout.writelines(["\n\t", str(simcontrol_data[stage][0][0]), "\t/\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_PVT.INC'\t/\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_SCAL.INC'\t/\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_SWOF.INC'\t/\n"])

    # regions section
    fout.writelines(["\nREGIONS\n"])

    if legacy_versions:
        fout.writelines(["\nNOECHO\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_REG.INC'\t/\n"])

    # solution section
    fout.writelines(["\nSOLUTION\n"])

    if legacy_versions:
        fout.writelines(["\nNOECHO\n"])

    if experiment_name == "CENT":
        fout.writelines(["\nRPTRST"])
        fout.writelines(["\n\tBASIC=2\t/\n"])
        if stage != 0:
            fout.writelines(["\nRESTART"])
            fout.writelines(
                ["\n\t", project_name + str(stage - 1), "\t", str(num_reports), "\t/\n"]
            )

            filename = project_name + "_INIT" + str(stage) + ".INC"
            fout.writelines(["\nINCLUDE"])
            fout.writelines(["\n'./include/", filename, "'\t/\n"])
        else:
            # fout.writelines(['\nINCLUDE'])
            # fout.writelines(['\n\'./include/', project_name, '_INIT.INC\'\t/\n'])

            filename = project_name + "_INIT" + str(stage) + ".INC"
            fout.writelines(["\nINCLUDE"])
            fout.writelines(["\n'./include/", filename, "'\t/\n"])
    elif experiment_name in {"SS", "USS"}:
        fout.writelines(["\nINCLUDE"])
        fout.writelines(["\n'./include/", project_name, "_INIT.INC'\t/\n"])

    # summary section
    fout.writelines(["\nSUMMARY\n"])

    if legacy_versions:
        fout.writelines(["\nNOECHO\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_SUM.INC'\t/\n"])

    # schedule section
    fout.writelines(["\nSCHEDULE\n"])

    if legacy_versions:
        fout.writelines(["\nNOECHO\n"])

    if experiment_name == "CENT":
        fout.writelines(["\nRPTSCHED"])
        fout.writelines(["\n\tRESTART\t'NEWTON=2'\t/\n"])

    fout.writelines(["\nINCLUDE"])
    fout.writelines(["\n'./include/", project_name, "_SCH.INC'\t/\n"])

    if experiment_name == "CENT":
        if stage != 0:
            fout.writelines(["\nSKIPREST\n"])

    fout.writelines(["\nINCLUDE"])

    if experiment_name == "CENT":
        filename = project_name + "_WELLSCH" + str(stage) + ".INC"
        fout.writelines(["\n'./include/", filename, "'\t/\n"])
    elif experiment_name in {"SS", "USS"}:
        fout.writelines(["\n'./include/", project_name, "_WELLSCH.INC'\t/\n"])

    if experiment_name == "CENT":
        fout.writelines(["\nSAVE\n"])

    # end of file
    fout.writelines(["\nEND\n"])

    # close file
    fout.close()


# ============================================================================
# DATA FILE: 'GRID' SECTION
# ============================================================================


def write_grid_operations_datafile(
    wdir, project_name, experiment_name, flooding, verbose=False
):
    """
    Unsupported keywords: RPTINIT
    """
    # @TODO: create universal approach
    # legacy version
    # the code is kept for potential use in future
    legacy_versions = False

    filename = os.path.join(wdir, "include", project_name + "_GOPP.INC")

    # open file
    fout = open(filename, "w")

    fout.writelines(["-- control output of the grid geometry file ( 2 numbers )"])
    fout.writelines(["\nGRIDFILE"])
    fout.writelines(
        [
            "\n --1st number: 0 - no GRID file output, 1 - standard GRID file, 2 - extended GRID file"
        ]
    )
    fout.writelines(
        ["\n --2nd number: 0 - no EGRID file output, 1 - EGRID file output"]
    )
    # @TODO: create universal approach
    # ECLIPSE:
    # fout.writelines(['\n\t', str(2) ,' \t', str( 1 ), '\t/\n'])
    fout.writelines(["\n\t", str(0), " \t", str(1), "\t/\n"])

    fout.writelines(["\n-- requests output of an INIT file"])
    fout.writelines(["\nINIT\n"])

    fout.writelines(
        ["\n-- Controls on output from GRID and EDIT sections to INIT file"]
    )

    if legacy_versions:
        fout.writelines(["\nRPTINIT"])
        fout.writelines(["\n\tDX\tDY\tDZ\tPERMX\tPERMY\tPERMZ\tPORO\t/\n"])

    # close file
    fout.close()


def write_grid_geometry_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    diameter,
    distance_to_inlet,
    depth,
    verbose=False,
):
    """
    Unsupported keywords: GRIDUNIT
    """
    # @TODO: create universal approach
    # legacy version
    # the code is kept for potential use in future
    legacy_versions = False

    filename = os.path.join(wdir, "include", project_name + "_GGO.INC")

    # open file
    fout = open(filename, "w")

    if legacy_versions:
        fout.writelines(["-- specifies the grid data units"])
        fout.writelines(["\nGRIDUNIT"])
        fout.writelines(["\n\tCM\t/\n"])

        fout.writelines(["\n-- specifies units used for MAPAXES data"])
        fout.writelines(["\nMAPUNITS"])
        fout.writelines(["\n\tLAB\t/\n"])

        fout.writelines(
            [
                "\n-- specifies grid axes and the grid origin relative to the map coordinates"
            ]
        )
        fout.writelines(["\nMAPAXES"])
        fout.writelines(["\n\t0\t1\t0\t0\t1\t0\t/\n"])

    # grid parameters
    num_cells, num_refined_cells, num_first_cells, num_last_cells, dl, dr = grid_blocks(
        experiment_name, flooding, grid_type, num_grid_blocks, length
    )

    # cross sections cells
    da = np.float64(math.sqrt(math.pi)) * np.float64(diameter) / np.float64(2.0)
    da_out = np.float64(da_out_factor * da)

    nx_cells = (
        int(1)
        if (int(da / (dx_out_factor * dl)) == 0)
        else int(da / (dx_out_factor * dl))
    )
    nx_out_cells = (
        int(1)
        if (int(da_out / (dx_out_factor * dl)) == 0)
        else int(da_out / (dx_out_factor * dl))
    )
    ny_cells = int(1)
    ny_out_cells = int(1)

    dx = np.float64(da / nx_cells)
    dx_out = np.float64(da_out / nx_out_cells)
    dy = np.float64(da / ny_cells)
    dy_out = np.float64(da_out / ny_out_cells)

    dl = round(dl, eclipse_precision)
    da = round(da, eclipse_precision)
    da_out = round(da_out, eclipse_precision)
    dx = round(dx, eclipse_precision)
    dx_out = round(dx_out, eclipse_precision)
    dy = round(dy, eclipse_precision)
    dy_out = round(dy_out, eclipse_precision)

    if verbose:
        print("nx(in)  cells = ", nx_cells)
        print("nx(out) cells = ", nx_out_cells)
        print("ny cells = ", ny_cells)

        print("dz = ", dl)
        print("dx = ", dx_out_factor * dl)
        print("dy = ", dy)

    if experiment_name in {"SS", "USS"}:
        fout.writelines(["\nDX\n"])
        if (num_first_cells > 0) and (num_last_cells > 0) and (num_refined_cells > 0):
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(dr[i])])
            fout.writelines(["\n"])
            for i in range(num_first_cells, num_first_cells + num_refined_cells):
                fout.writelines(["\t", str(dr[i])])
            fout.writelines(["\n"])
            fout.writelines(
                [
                    "\n\t",
                    str(
                        num_cells
                        - num_first_cells
                        - num_last_cells
                        - 2 * num_refined_cells
                    ),
                    "*",
                    str(dl),
                    "\n",
                ]
            )
            for i in range(
                num_cells - num_refined_cells - num_last_cells,
                num_cells - num_last_cells,
            ):
                fout.writelines(["\t", str(dr[i])])
            fout.writelines(["\n"])
            for i in range(num_cells - num_last_cells, num_cells):
                fout.writelines(["\t", str(dr[i])])
        elif num_refined_cells > 0:
            for i in range(0, num_refined_cells):
                fout.writelines(["\t", str(dr[i])])
            fout.writelines(
                ["\n\t", str(num_cells - 2 * num_refined_cells), "*", str(dl), "\n"]
            )
            for i in range(num_cells - num_refined_cells, num_cells):
                fout.writelines(["\t", str(dr[i])])
        elif (num_first_cells > 0) and (num_last_cells > 0):
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(dr[i])])
            fout.writelines(
                [
                    "\n\t",
                    str(num_cells - num_first_cells - num_last_cells),
                    "*",
                    str(dl),
                    "\n",
                ]
            )
            for i in range(num_cells - num_last_cells, num_cells):
                fout.writelines(["\t", str(dr[i])])
        else:
            fout.writelines(["\t", str(num_cells), "*", str(dl)])
        fout.writelines(["\n/\n"])

        fout.writelines(["\nDY"])
        fout.writelines(["\n\t", str(num_cells), "*", str(da), "\n/\n"])

        fout.writelines(["\nDZ"])
        fout.writelines(["\n\t", str(num_cells), "*", str(da), "\n/\n"])

        fout.writelines(["\nTOPS"])
        fout.writelines(["\n\t", str(num_cells), "*", str(depth), "\n/\n"])

    elif experiment_name == "CENT":
        if grid_type in {
            "core",
            "core-refined",
            "extended-core",
            "extended-core-refined",
        }:
            fout.writelines(["\nDX"])
            fout.writelines(["\n\t", str(num_cells), "*", str(da), "\n/\n"])

            fout.writelines(["\nDY"])
            fout.writelines(["\n\t", str(num_cells), "*", str(da), "\n/\n"])

            fout.writelines(["\nDZ\n"])
            if (num_first_cells > 0) and (num_last_cells > 0):
                for i in range(0, num_first_cells):
                    fout.writelines(["\t", str(dr[i])])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_first_cells % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_grid_blocks):
                    j = int(num_first_cells + i)
                    fout.writelines(["\t", str(dr[j])])
                    if (i + 1) % 5 == 0:
                        fout.writelines(["\n"])
                if num_grid_blocks % 5 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_last_cells):
                    fout.writelines(
                        ["\t", str(dr[num_first_cells + num_grid_blocks + i])]
                    )
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_last_cells % 2 != 0:
                    fout.writelines(["\n"])
                fout.writelines(["/\n"])
            else:
                for i in range(0, num_grid_blocks):
                    fout.writelines(["\t", str(dr[i])])
                    if (i + 1) % 5 == 0:
                        fout.writelines(["\n"])
                if num_grid_blocks % 5 != 0:
                    fout.writelines(["\n"])
                fout.writelines(["/\n"])

            fout.writelines(["\nTOPS"])
            fout.writelines(["\n\t", str(depth), "\n/\n"])

            # fout.writelines( ['\nTOPS\n'] )
            # dh = np.float64( depth )
            # for i in range( 0, num_cells ):
            #     fout.writelines( [ '\t', str( dh ) ] )
            #     dh    += np.float64( dr[i] )
            #     if( (i+1)%5 == 0 ):
            #         fout.writelines( [ '\n' ] )
            # if( num_cells%5 != 0 ):
            #     fout.writelines( [ '\n' ] )
            # fout.writelines( [ '/\n' ] )

        elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            # pseudo 2D model
            if not centrifuge3D:
                if grid_type in {"centrifuge-core-refined"}:
                    nx_cells_total = nx_cells + 2 * nx_out_cells
                    ny_cells_total = ny_cells
                    nxy_cells = (nx_cells + 2 * nx_out_cells) * ny_cells
                    nxy_left_cells = nx_out_cells * ny_cells
                    nxy_right_cells = nx_out_cells * ny_cells
                    nxy_centre_cells = nx_cells * ny_cells

                    fout.writelines(["\nDX"])
                    for i in range(0, num_cells):
                        for j in range(0, ny_cells):
                            fout.writelines(
                                [
                                    "\n\t",
                                    str(nx_out_cells),
                                    "*",
                                    str(dx_out),
                                    "\t",
                                    str(nx_cells),
                                    "*",
                                    str(dx),
                                    "\t",
                                    str(nx_out_cells),
                                    "*",
                                    str(dx_out),
                                ]
                            )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nDY"])
                    for i in range(0, num_cells):
                        fout.writelines(["\n\t", str(nxy_cells), "*", str(dy)])
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nDZ\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(["\t", str(nxy_cells), "*", str(dr[i])])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        j = int(num_first_cells + i)
                        fout.writelines(["\t", str(nxy_cells), "*", str(dr[j])])
                        if (i + 1) % 5 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 5 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(
                            [
                                "\t",
                                str(nxy_cells),
                                "*",
                                str(dr[num_first_cells + num_grid_blocks + i]),
                            ]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nTOPS"])
                    fout.writelines(["\n\t", str(nxy_cells), "*", str(depth), "\n/\n"])

                    # fout.writelines( ['\nTOPS\n'] )
                    # dh = np.float64( depth )
                    # for i in range( 0, num_cells ):
                    #     fout.writelines( [ '\t', str( nxy_cells ), '*', str( dh ) ] )
                    #     dh    += np.float64( dr[i] )
                    #     if( (i+1)%5 == 0 ):
                    #         fout.writelines( [ '\n' ] )
                    # if(num_cells%5 != 0):
                    #     fout.writelines( [ '\n' ] )
                    # fout.writelines( [ '/\n' ] )

                    fout.writelines(["\nEQUALS"])
                    fout.writelines(
                        ["\n--\tarray name\t\tvalue\tix1\tix2\tjy1\tjy2\tkz1\tkz2"]
                    )
                    # sleeve
                    # left
                    fout.writelines(
                        [
                            "\n\tMULTX\t",
                            str(0.0),
                            "\t",
                            str(nx_out_cells),
                            "\t",
                            str(nx_out_cells),
                            "\t",
                            str(1),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                            "\t/",
                        ]
                    )
                    # right
                    fout.writelines(
                        [
                            "\n\tMULTX-\t",
                            str(0.0),
                            "\t",
                            str(nx_out_cells + nx_cells + 1),
                            "\t",
                            str(nx_out_cells + nx_cells + 1),
                            "\t",
                            str(1),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                            "\t/",
                        ]
                    )
                    # fout.writelines( ['\n\tMULTX\t', str( 0.0 ), '\t', str( nx_out_cells + nx_cells ), '\t', str( nx_out_cells + nx_cells ), '\t', str( 1 ), '\t', str( ny_cells ), '\t', str( num_first_cells + 1 ), '\t', str( num_grid_blocks + num_first_cells ), '\t/'] )
                    # footbath
                    if footbath:
                        if flooding == "imbibition":
                            fout.writelines(
                                [
                                    "\n\tMULTZ-\t",
                                    str(0.0),
                                    "\t",
                                    str(nx_out_cells + 1),
                                    "\t",
                                    str(nx_out_cells + nx_cells),
                                    "\t",
                                    str(1),
                                    "\t",
                                    str(ny_cells),
                                    "\t",
                                    str(num_first_cells),
                                    "\t",
                                    str(num_first_cells),
                                    "\t/",
                                ]
                            )
                        elif flooding == "drainage":
                            fout.writelines(
                                [
                                    "\n\tMULTZ\t",
                                    str(0.0),
                                    "\t",
                                    str(nx_out_cells + 1),
                                    "\t",
                                    str(nx_out_cells + nx_cells),
                                    "\t",
                                    str(1),
                                    "\t",
                                    str(ny_cells),
                                    "\t",
                                    str(num_grid_blocks + num_first_cells + 1),
                                    "\t",
                                    str(num_grid_blocks + num_first_cells + 1),
                                    "\t/",
                                ]
                            )
                    fout.writelines(["\n/\n"])

                else:
                    fout.writelines(["\nDX"])
                    for i in range(0, num_cells):
                        fout.writelines(
                            ["\n\t", str(da_out), "\t", str(da), "\t", str(da_out)]
                        )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nDY"])
                    for i in range(0, num_cells):
                        fout.writelines(["\n\t", str(3), "*", str(da)])
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nDZ\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(["\t", str(3), "*", str(dr[i])])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        j = int(num_first_cells + i)
                        fout.writelines(["\t", str(3), "*", str(dr[j])])
                        if (i + 1) % 5 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 5 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(
                            [
                                "\t",
                                str(3),
                                "*",
                                str(dr[num_first_cells + num_grid_blocks + i]),
                            ]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nTOPS"])
                    fout.writelines(["\n\t", str(3), "*", str(depth), "\n/\n"])

                    # fout.writelines( ['\nTOPS\n'] )
                    # dh = np.float64( depth )
                    # for i in range( 0, num_cells ):
                    #     fout.writelines( [ '\t', str( 3 ), '*', str( dh ) ] )
                    #     dh    += np.float64( dr[i] )
                    #     if( (i+1)%5 == 0 ):
                    #         fout.writelines( [ '\n' ] )
                    # if( num_cells%5 != 0 ):
                    #     fout.writelines( [ '\n' ] )
                    # fout.writelines( [ '/\n' ] )

                    fout.writelines(["\nEQUALS"])
                    fout.writelines(
                        ["\n--\tarray name\t\tvalue\tix1\tix2\tjy1\tjy2\tkz1\tkz2"]
                    )
                    # sleeve
                    # left
                    fout.writelines(
                        [
                            "\n\tMULTX\t",
                            str(0.0),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                            "\t/",
                        ]
                    )
                    # right
                    fout.writelines(
                        [
                            "\n\tMULTX-\t",
                            str(0.0),
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                            "\t/",
                        ]
                    )
                    # fout.writelines( ['\n\tMULTX\t', str( 0.0 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_first_cells + 1 ), '\t', str( num_grid_blocks + num_first_cells ), '\t/'] )
                    # footbath
                    if footbath:
                        if flooding == "imbibition":
                            fout.writelines(
                                [
                                    "\n\tMULTZ-\t",
                                    str(0.0),
                                    "\t",
                                    str(2),
                                    "\t",
                                    str(2),
                                    "\t",
                                    str(1),
                                    "\t",
                                    str(1),
                                    "\t",
                                    str(num_first_cells),
                                    "\t",
                                    str(num_first_cells),
                                    "\t/",
                                ]
                            )
                        elif flooding == "drainage":
                            fout.writelines(
                                [
                                    "\n\tMULTZ\t",
                                    str(0.0),
                                    "\t",
                                    str(2),
                                    "\t",
                                    str(2),
                                    "\t",
                                    str(1),
                                    "\t",
                                    str(1),
                                    "\t",
                                    str(num_grid_blocks + num_first_cells + 1),
                                    "\t",
                                    str(num_grid_blocks + num_first_cells + 1),
                                    "\t/",
                                ]
                            )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nACTNUM\n"])
                    temp_length = np.float64(0.0)
                    for i in range(0, num_first_cells):
                        temp_length += dr[i]
                        if (temp_length < (1.0 - outcore_length_factor) * length) and (
                            flooding == "imbibition"
                        ):
                            fout.writelines(["\t", str(0), "\t", str(1), "\t", str(0)])
                        else:
                            fout.writelines(["\t", str(3), "*", str(1)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        j = int(num_first_cells + i)
                        fout.writelines(["\t", str(3), "*", str(1)])
                        if (i + 1) % 5 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 5 != 0:
                        fout.writelines(["\n"])
                    temp_length = np.float64(0.0)
                    for i in range(0, num_last_cells):
                        temp_length += dr[num_first_cells + num_grid_blocks + i]
                        if (temp_length > outcore_length_factor * length) and (
                            flooding == "drainage"
                        ):
                            fout.writelines(["\t", str(0), "\t", str(1), "\t", str(0)])
                        else:
                            fout.writelines(["\t", str(3), "*", str(1)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

            else:
                fout.writelines(["\nDX"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(da_out), "\t", str(da), "\t", str(da_out)]
                    )
                    fout.writelines(
                        ["\n\t", str(da_out), "\t", str(da), "\t", str(da_out)]
                    )
                    fout.writelines(
                        ["\n\t", str(da_out), "\t", str(da), "\t", str(da_out)]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\nDY"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(da_out), "\t", str(da_out), "\t", str(da_out)]
                    )
                    fout.writelines(["\n\t", str(da), "\t", str(da), "\t", str(da)])
                    fout.writelines(
                        ["\n\t", str(da_out), "\t", str(da_out), "\t", str(da_out)]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\nDZ\n"])
                for i in range(0, num_first_cells):
                    fout.writelines(["\t", str(9), "*", str(dr[i])])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_first_cells % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_grid_blocks):
                    j = int(num_first_cells + i)
                    fout.writelines(["\t", str(9), "*", str(dr[j])])
                    if (i + 1) % 5 == 0:
                        fout.writelines(["\n"])
                if num_grid_blocks % 5 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_last_cells):
                    fout.writelines(
                        [
                            "\t",
                            str(9),
                            "*",
                            str(dr[num_first_cells + num_grid_blocks + i]),
                        ]
                    )
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_last_cells % 2 != 0:
                    fout.writelines(["\n"])
                fout.writelines(["/\n"])

                fout.writelines(["\nTOPS"])
                fout.writelines(["\n\t", str(9), "*", str(depth), "\n/\n"])

                # fout.writelines( ['\nTOPS\n'] )
                # dh = np.float64( depth )
                # for i in range( 0, num_cells ):
                #     fout.writelines( [ '\t', str( 9 ), '*', str( dh ) ] )
                #     dh    += np.float64( dr[i] )
                #     if( (i+1)%5 == 0 ):
                #         fout.writelines( [ '\n' ] )
                # if( num_cells%5 != 0 ):
                #     fout.writelines( [ '\n' ] )
                # fout.writelines( [ '/\n' ] )

                fout.writelines(["\nEQUALS"])
                fout.writelines(
                    ["\n--\tarray name\t\tvalue\tix1\tix2\tjy1\tjy2\tkz1\tkz2"]
                )
                # sleeve
                # left
                fout.writelines(
                    [
                        "\n\tMULTX\t",
                        str(0.0),
                        "\t",
                        str(1),
                        "\t",
                        str(1),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                        "\t/",
                    ]
                )
                # right
                fout.writelines(
                    [
                        "\n\tMULTX-\t",
                        str(0.0),
                        "\t",
                        str(3),
                        "\t",
                        str(3),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                        "\t/",
                    ]
                )
                # fout.writelines( ['\n\tMULTX\t', str( 0.0 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( num_first_cells + 1 ), '\t', str( num_grid_blocks + num_first_cells ), '\t/'] )
                # back
                fout.writelines(
                    [
                        "\n\tMULTY\t",
                        str(0.0),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(1),
                        "\t",
                        str(1),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                        "\t/",
                    ]
                )
                # front
                fout.writelines(
                    [
                        "\n\tMULTY-\t",
                        str(0.0),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(3),
                        "\t",
                        str(3),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                        "\t/",
                    ]
                )
                # fout.writelines( ['\n\tMULTY\t', str( 0.0 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( num_first_cells + 1 ), '\t', str( num_grid_blocks + num_first_cells ), '\t/'] )
                # footbath
                if footbath:
                    if flooding == "imbibition":
                        fout.writelines(
                            [
                                "\n\tMULTZ-\t",
                                str(0.0),
                                "\t",
                                str(2),
                                "\t",
                                str(2),
                                "\t",
                                str(2),
                                "\t",
                                str(2),
                                "\t",
                                str(num_first_cells),
                                "\t",
                                str(num_first_cells),
                                "\t/",
                            ]
                        )
                    elif flooding == "drainage":
                        fout.writelines(
                            [
                                "\n\tMULTZ\t",
                                str(0.0),
                                "\t",
                                str(2),
                                "\t",
                                str(2),
                                "\t",
                                str(2),
                                "\t",
                                str(2),
                                "\t",
                                str(num_grid_blocks + num_first_cells + 1),
                                "\t",
                                str(num_grid_blocks + num_first_cells + 1),
                                "\t/",
                            ]
                        )
                fout.writelines(["\n/\n"])

    # Close file
    fout.close()


def write_grid_properties_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    diameter,
    distance_to_inlet,
    porosity,
    permeability,
    verbose,
):
    filename = os.path.join(wdir, "include", project_name + "_GPRO.INC")

    # Open file
    fout = open(filename, "w")

    if experiment_name in {"SS", "USS"}:
        if grid_type in {"core", "core-refined"}:
            fout.writelines(["PORO"])
            fout.writelines(["\n\t", str(num_grid_blocks), "*", str(porosity)])
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMX"])
            fout.writelines(["\n\t", str(num_grid_blocks), "*", str(permeability)])
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMY"])
            fout.writelines(["\n\t", str(num_grid_blocks), "*", str(permeability)])
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMZ"])
            fout.writelines(["\n\t", str(num_grid_blocks), "*", str(permeability)])
            fout.writelines(["\n/\n"])

        elif grid_type in {"extended-core", "extended-core-refined"}:
            # @TODO: find universal setup
            # porosity_outside = np.float64(1.0)
            porosity_outside = np.float64(porosity)
            permeability_outside = np.float64(1.0 * permeability)

            fout.writelines(["PORO"])
            fout.writelines(
                [
                    "\n\t",
                    str(porosity_outside),
                    "\t",
                    str(num_grid_blocks),
                    "*",
                    str(porosity),
                    "\t",
                    str(porosity_outside),
                ]
            )
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMX"])
            fout.writelines(
                [
                    "\n\t",
                    str(permeability_outside),
                    "\t",
                    str(num_grid_blocks),
                    "*",
                    str(permeability),
                    "\t",
                    str(permeability_outside),
                ]
            )
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMY"])
            fout.writelines(
                [
                    "\n\t",
                    str(permeability_outside),
                    "\t",
                    str(num_grid_blocks),
                    "*",
                    str(permeability),
                    "\t",
                    str(permeability_outside),
                ]
            )
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMZ"])
            fout.writelines(
                [
                    "\n\t",
                    str(permeability_outside),
                    "\t",
                    str(num_grid_blocks),
                    "*",
                    str(permeability),
                    "\t",
                    str(permeability_outside),
                ]
            )
            fout.writelines(["\n/\n"])

    elif experiment_name == "CENT":
        # grid parameters
        (
            num_cells,
            num_refined_cells,
            num_first_cells,
            num_last_cells,
            dl,
            dr,
        ) = grid_blocks(experiment_name, flooding, grid_type, num_grid_blocks, length)

        # cross sections cells
        da = np.float64(math.sqrt(math.pi)) * np.float64(diameter) / np.float64(2.0)
        da_out = np.float64(da_out_factor * da)

        nx_cells = (
            int(1)
            if (int(da / (dx_out_factor * dl)) == 0)
            else int(da / (dx_out_factor * dl))
        )
        nx_out_cells = (
            int(1)
            if (int(da_out / (dx_out_factor * dl)) == 0)
            else int(da_out / (dx_out_factor * dl))
        )
        ny_cells = int(1)
        ny_out_cells = int(1)

        porosity_outside = np.float64(1.0)
        permeability_outside = np.float64(100.0 * permeability)
        zero_permeability = np.float64(0.0)

        if grid_type in {"core", "core-refined"}:
            fout.writelines(["PORO\n"])
            for i in range(0, num_cells):
                fout.writelines(["\t", str(porosity)])
                if (i + 1) % 5 == 0:
                    fout.writelines(["\n"])
            if num_grid_blocks % 5 != 0:
                fout.writelines(["\n"])
            fout.writelines(["/\n"])

            fout.writelines(["\nPERMX"])
            fout.writelines(["\n\t", str(num_cells), "*", str(permeability)])
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMY"])
            fout.writelines(["\n\t", str(num_cells), "*", str(permeability)])
            fout.writelines(["\n/\n"])

            fout.writelines(["\nPERMZ"])
            fout.writelines(["\n\t", str(num_cells), "*", str(permeability)])
            fout.writelines(["\n/\n"])

        elif grid_type in {"extended-core", "extended-core-refined"}:
            fout.writelines(["PORO\n"])
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(porosity_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_first_cells % 2 != 0:
                fout.writelines(["\n"])
            for i in range(0, num_grid_blocks):
                fout.writelines(["\t", str(porosity)])
                if (i + 1) % 5 == 0:
                    fout.writelines(["\n"])
            if num_grid_blocks % 5 != 0:
                fout.writelines(["\n"])
            for i in range(0, num_last_cells):
                fout.writelines(["\t", str(porosity_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_last_cells % 2 != 0:
                fout.writelines(["\n"])
            fout.writelines(["/\n"])

            fout.writelines(["\nPERMX\n"])
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(permeability_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_first_cells % 2 != 0:
                fout.writelines(["\n"])
            fout.writelines(["\t", str(num_grid_blocks), "*", str(permeability), "\n"])
            for i in range(0, num_last_cells):
                fout.writelines(["\t", str(permeability_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_last_cells % 2 != 0:
                fout.writelines(["\n"])
            fout.writelines(["/\n"])

            fout.writelines(["\nPERMY\n"])
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(permeability_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_first_cells % 2 != 0:
                fout.writelines(["\n"])
            fout.writelines(["\t", str(num_grid_blocks), "*", str(permeability), "\n"])
            for i in range(0, num_last_cells):
                fout.writelines(["\t", str(permeability_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_last_cells % 2 != 0:
                fout.writelines(["\n"])
            fout.writelines(["/\n"])

            fout.writelines(["\nPERMZ\n"])
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(permeability_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_first_cells % 2 != 0:
                fout.writelines(["\n"])
            fout.writelines(["\t", str(num_grid_blocks), "*", str(permeability), "\n"])
            for i in range(0, num_last_cells):
                fout.writelines(["\t", str(permeability_outside)])
                if (i + 1) % 2 == 0:
                    fout.writelines(["\n"])
            if num_last_cells % 2 != 0:
                fout.writelines(["\n"])
            fout.writelines(["/\n"])

        elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            if not centrifuge3D:
                if grid_type in {"centrifuge-core-refined"}:
                    nx_cells_total = nx_cells + 2 * nx_out_cells
                    ny_cells_total = ny_cells
                    nxy_cells = (nx_cells + 2 * nx_out_cells) * ny_cells
                    nxy_left_cells = nx_out_cells * ny_cells
                    nxy_right_cells = nx_out_cells * ny_cells
                    nxy_centre_cells = nx_cells * ny_cells

                    fout.writelines(["PORO\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(porosity_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(nxy_left_cells),
                                "*",
                                str(porosity_outside),
                                "\t",
                                str(nxy_centre_cells),
                                "*",
                                str(porosity),
                                "\t",
                                str(nxy_right_cells),
                                "*",
                                str(porosity_outside),
                            ]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(porosity_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nPERMX\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(permeability_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(nxy_left_cells),
                                "*",
                                str(permeability_outside),
                                "\t",
                                str(nxy_centre_cells),
                                "*",
                                str(permeability),
                                "\t",
                                str(nxy_right_cells),
                                "*",
                                str(permeability_outside),
                            ]
                        )
                        # fout.writelines( [ '\t', str( nxy_cells ) , '*', str( zero_permeability ) ] )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(permeability_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nPERMY\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(permeability_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(nxy_left_cells),
                                "*",
                                str(permeability_outside),
                                "\t",
                                str(nxy_centre_cells),
                                "*",
                                str(permeability),
                                "\t",
                                str(nxy_right_cells),
                                "*",
                                str(permeability_outside),
                            ]
                        )
                        # fout.writelines( [ '\t', str( nxy_cells ) , '*', str( zero_permeability ) ] )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(permeability_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nPERMZ\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(permeability_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(nxy_left_cells),
                                "*",
                                str(permeability_outside),
                                "\t",
                                str(nxy_centre_cells),
                                "*",
                                str(permeability),
                                "\t",
                                str(nxy_right_cells),
                                "*",
                                str(permeability_outside),
                            ]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(permeability_outside)]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                else:
                    fout.writelines(["PORO\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(["\t", str(3), "*", str(porosity_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(porosity_outside),
                                "\t",
                                str(porosity),
                                "\t",
                                str(porosity_outside),
                            ]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(["\t", str(3), "*", str(porosity_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nPERMX\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(["\t", str(3), "*", str(permeability_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(permeability_outside),
                                "\t",
                                str(permeability),
                                "\t",
                                str(permeability_outside),
                            ]
                        )
                        # fout.writelines( [ '\t', str( 3 ) , '*', str( zero_permeability ) ] )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(["\t", str(3), "*", str(permeability_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nPERMY\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(["\t", str(3), "*", str(permeability_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(permeability_outside),
                                "\t",
                                str(permeability),
                                "\t",
                                str(permeability_outside),
                            ]
                        )
                        # fout.writelines( [ '\t', str( 3 ) , '*', str( zero_permeability ) ] )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(["\t", str(3), "*", str(permeability_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    fout.writelines(["\nPERMZ\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(["\t", str(3), "*", str(permeability_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(
                            [
                                "\t",
                                str(permeability_outside),
                                "\t",
                                str(permeability),
                                "\t",
                                str(permeability_outside),
                            ]
                        )
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(["\t", str(3), "*", str(permeability_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                    # local grid refinement

                    if LGR:
                        # last_block = len( dr ) - 1

                        # (1,1)
                        # nx = int( da_out/dl )
                        # ny = int( da/dl )
                        # nz = int( num_cells )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 1 ), '\'', '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_cells ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        # nx = int( da_out/dl )
                        # ny = int( da/dl )
                        # nz = int( num_grid_blocks )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 2 ), '\'', '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_first_cells ), '\t', str( num_first_cells + num_grid_blocks ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        nx = int(da_out / dl)
                        ny = int(da / dl)
                        nz = int(num_first_cells)
                        fout.writelines(["\nCARFIN"])
                        fout.writelines(
                            ["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"]
                        )
                        fout.writelines(
                            [
                                "\n\t",
                                "'LGR",
                                str(3),
                                "'",
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(num_first_cells),
                                "\t",
                                str(nx),
                                "\t",
                                str(ny),
                                "\t",
                                str(nz),
                                "\t/",
                            ]
                        )
                        fout.writelines(["\nLGRCOPY"])
                        fout.writelines(["\nENDFIN\n"])

                        nx = int(da_out / dl)
                        ny = int(da / dl)
                        nz = int(num_last_cells)
                        fout.writelines(["\nCARFIN"])
                        fout.writelines(
                            ["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"]
                        )
                        fout.writelines(
                            [
                                "\n\t",
                                "'LGR",
                                str(4),
                                "'",
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(num_first_cells + num_grid_blocks + 1),
                                "\t",
                                str(num_cells),
                                "\t",
                                str(nx),
                                "\t",
                                str(ny),
                                "\t",
                                str(nz),
                                "\t/",
                            ]
                        )
                        fout.writelines(["\nLGRCOPY"])
                        fout.writelines(["\nENDFIN\n"])

                        # (2,1)
                        # nx = int( da/dl )
                        # ny = int( da/dl )
                        # nz = int( num_cells )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 5 ), '\'', '\t', str( 2 ), '\t', str( 2 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_cells ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        # nx = int( da/dl )
                        # ny = int( da/dl )
                        # nz = int( num_grid_blocks )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 6 ), '\'', '\t', str( 2 ), '\t', str( 2 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_first_cells ), '\t', str( num_first_cells + num_grid_blocks ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        # nx = int( da/dl )
                        # ny = int( da/dl )
                        # nz = int( num_first_cells )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 7 ), '\'', '\t', str( 2 ), '\t', str( 2 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_first_cells ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        # nx = nx_cells
                        # ny = ny_cells
                        # nz = int( num_last_cells )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 8 ), '\'', '\t', str( 2 ), '\t', str( 2 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_first_cells + num_grid_blocks + 1 ), '\t', str( num_cells ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        # (3,1)
                        # nx = int( da_out/dl )
                        # ny = int( da/dl )
                        # nz = int( num_cells )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 9 ), '\'', '\t', str( 3 ), '\t', str( 3 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_cells ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        # nx = int( da_out/dl )
                        # ny = int( da/dl )
                        # nz = int( num_grid_blocks )
                        # fout.writelines( ['\nCARFIN'] )
                        # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                        # fout.writelines( ['\n\t', '\'LGR', str( 10 ), '\'', '\t', str( 3 ), '\t', str( 3 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_first_cells ), '\t', str( num_first_cells + num_grid_blocks ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                        # fout.writelines( ['\nLGRCOPY'])
                        # fout.writelines( ['\nENDFIN\n'] )

                        nx = int(da_out / dl)
                        ny = int(da / dl)
                        nz = int(num_first_cells)
                        fout.writelines(["\nCARFIN"])
                        fout.writelines(
                            ["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"]
                        )
                        fout.writelines(
                            [
                                "\n\t",
                                "'LGR",
                                str(11),
                                "'",
                                "\t",
                                str(3),
                                "\t",
                                str(3),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(num_first_cells),
                                "\t",
                                str(nx),
                                "\t",
                                str(ny),
                                "\t",
                                str(nz),
                                "\t/",
                            ]
                        )
                        fout.writelines(["\nLGRCOPY"])
                        fout.writelines(["\nENDFIN\n"])

                        nx = int(da_out / dl)
                        ny = int(da / dl)
                        nz = int(num_last_cells)
                        fout.writelines(["\nCARFIN"])
                        fout.writelines(
                            ["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"]
                        )
                        fout.writelines(
                            [
                                "\n\t",
                                "'LGR",
                                str(12),
                                "'",
                                "\t",
                                str(3),
                                "\t",
                                str(3),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(num_first_cells + num_grid_blocks + 1),
                                "\t",
                                str(num_cells),
                                "\t",
                                str(nx),
                                "\t",
                                str(ny),
                                "\t",
                                str(nz),
                                "\t/",
                            ]
                        )
                        fout.writelines(["\nLGRCOPY"])
                        fout.writelines(["\nENDFIN\n"])

                        fout.writelines(["\nAMALGAM"])
                        fout.writelines(["\n'LGR*'\t/\n"])
                        fout.writelines(["/\n"])

            else:
                # [3x3xN]
                fout.writelines(["PORO\n"])
                for i in range(0, num_first_cells):
                    fout.writelines(["\t", str(9), "*", str(porosity_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_first_cells % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_grid_blocks):
                    fout.writelines(["\t", str(4), "*", str(porosity_outside)])
                    fout.writelines(["\t", str(porosity)])
                    fout.writelines(["\t", str(4), "*", str(porosity_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_grid_blocks % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_last_cells):
                    fout.writelines(["\t", str(9), "*", str(porosity_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_last_cells % 2 != 0:
                    fout.writelines(["\n"])
                fout.writelines(["/\n"])

                fout.writelines(["\nPERMX\n"])
                for i in range(0, num_first_cells):
                    fout.writelines(["\t", str(9), "*", str(permeability_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_first_cells % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_grid_blocks):
                    fout.writelines(["\t", str(4), "*", str(permeability_outside)])
                    fout.writelines(["\t", str(permeability)])
                    fout.writelines(["\t", str(4), "*", str(permeability_outside)])
                    # fout.writelines( [ '\t', str( 9 ) , '*', str( zero_permeability ) ] )
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_grid_blocks % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_last_cells):
                    fout.writelines(["\t", str(9), "*", str(permeability_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_last_cells % 2 != 0:
                    fout.writelines(["\n"])
                fout.writelines(["/\n"])

                fout.writelines(["\nPERMY\n"])
                for i in range(0, num_first_cells):
                    fout.writelines(["\t", str(9), "*", str(permeability_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_first_cells % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_grid_blocks):
                    fout.writelines(["\t", str(4), "*", str(permeability_outside)])
                    fout.writelines(["\t", str(permeability)])
                    fout.writelines(["\t", str(4), "*", str(permeability_outside)])
                    # fout.writelines( [ '\t', str( 9 ) , '*', str( zero_permeability ) ] )
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_grid_blocks % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_last_cells):
                    fout.writelines(["\t", str(9), "*", str(permeability_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_last_cells % 2 != 0:
                    fout.writelines(["\n"])
                fout.writelines(["/\n"])

                fout.writelines(["\nPERMZ\n"])
                for i in range(0, num_first_cells):
                    fout.writelines(["\t", str(9), "*", str(permeability_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_first_cells % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_grid_blocks):
                    fout.writelines(["\t", str(4), "*", str(permeability_outside)])
                    fout.writelines(["\t", str(permeability)])
                    fout.writelines(["\t", str(4), "*", str(permeability_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_grid_blocks % 2 != 0:
                    fout.writelines(["\n"])
                for i in range(0, num_last_cells):
                    fout.writelines(["\t", str(9), "*", str(permeability_outside)])
                    if (i + 1) % 2 == 0:
                        fout.writelines(["\n"])
                if num_last_cells % 2 != 0:
                    fout.writelines(["\n"])
                fout.writelines(["/\n"])

                if LGR:
                    # local grid refinement

                    # (1,1)
                    # nx = int( da_out/dl )
                    # ny = int( da_out/dl )
                    nx = nx_out_cells
                    ny = ny_out_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(1),
                            "'",
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # (3,1)
                    # nx = int( da_out/dl )
                    # ny = int( da_out/dl )
                    nx = nx_out_cells
                    ny = ny_out_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(3),
                            "'",
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # (1,2)
                    # nx = int( da_out/dl )
                    # ny = int( da/dl )
                    nx = nx_out_cells
                    ny = ny_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(4),
                            "'",
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # (3,2)
                    # nx = int( da_out/dl )
                    # ny = int( da/dl )
                    nx = nx_out_cells
                    ny = ny_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(5),
                            "'",
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # (1,3)
                    # nx = int( da_out/dl )
                    # ny = int( da_out/dl )
                    nx = nx_out_cells
                    ny = ny_out_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(6),
                            "'",
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # (3,3)
                    # nx = int( da_out/dl )
                    # ny = int( da_out/dl )
                    nx = nx_out_cells
                    ny = ny_out_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(8),
                            "'",
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY\n"])
                    fout.writelines(["\nENDFIN\n"])

                    # (2,1)
                    # nx = int( da/dl )
                    # ny = int( da_out/dl )
                    nx = nx_cells
                    ny = ny_out_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(2),
                            "'",
                            "\t",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # (2,3)
                    # nx = int( da/dl )
                    # ny = int( da_out/dl )
                    nx = nx_cells
                    ny = ny_out_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(7),
                            "'",
                            "\t",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # (2,2)
                    # nx = int( da/dl )
                    # ny = int( da/dl )
                    nx = nx_cells
                    ny = ny_cells
                    nz = int(num_cells)
                    fout.writelines(["\nCARFIN"])
                    fout.writelines(["\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY"])
                    fout.writelines(
                        [
                            "\n\t",
                            "'LGR",
                            str(9),
                            "'",
                            "\t",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(1),
                            "\t",
                            str(num_cells),
                            "\t",
                            str(nx),
                            "\t",
                            str(ny),
                            "\t",
                            str(nz),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\nLGRCOPY"])
                    fout.writelines(["\nENDFIN\n"])

                    # nx = int( da/dl )
                    # ny = int( da/dl )
                    # nz = int( num_grid_blocks )
                    # fout.writelines( ['\nCARFIN'] )
                    # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                    # fout.writelines( ['\n\t', '\'LGR', str( 9 ), '\'', '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( num_first_cells ), '\t', str( num_first_cells + num_grid_blocks ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                    # fout.writelines( ['\nLGRCOPY'])
                    # fout.writelines( ['\nENDFIN\n'] )

                    # nx = int( da/dl )
                    # ny = int( da/dl )
                    # nz = int( num_first_cells )
                    # fout.writelines( ['\nCARFIN'] )
                    # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                    # fout.writelines( ['\n\t', '\'LGR', str( 10 ), '\'', '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 1 ), '\t', str( num_first_cells ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                    # fout.writelines( ['\nLGRCOPY'])
                    # fout.writelines( ['\nENDFIN\n'] )

                    # nx = int( da/dl )
                    # ny = int( da/dl )
                    # nx = nx_cells
                    # ny = ny_cells
                    # nz = int( num_last_cells )
                    # fout.writelines( ['\nCARFIN'] )
                    # fout.writelines( ['\n--\tName\tI1\tI2\tJ1\tJ2\K1\tK2\tNX\tNY\tNY'] )
                    # fout.writelines( ['\n\t', '\'LGR', str( 11 ), '\'', '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( 2 ), '\t', str( num_first_cells + num_grid_blocks + 1 ), '\t', str( num_cells ), '\t', str( nx ), '\t', str( ny ), '\t', str( nz ), '\t/'] )
                    # fout.writelines( ['\nLGRCOPY'])
                    # fout.writelines( ['\nENDFIN\n'] )

                    fout.writelines(["\nAMALGAM"])
                    fout.writelines(["\n'LGR*'\t/\n"])
                    fout.writelines(["/\n"])

    # Close file
    fout.close()


# ============================================================================
# DATA FILE: 'PROPS' SECTION
# ============================================================================


def write_scal_datafile(
    wdir, project_name, experiment_name, flooding, grid_type, num_grid_blocks, verbose
):
    filename = os.path.join(wdir, "include", project_name + "_SCAL.INC")

    SWL = 0.08
    SWCR = 0.08
    SOWCR = 0.15
    SWU = 0.9
    KRW = 0.7
    KRO = 0.9

    # Open file
    fout = open(filename, "w")

    if grid_type in {"core", "core-refined"}:
        fout.writelines(["\n--SWL"])
        fout.writelines(["\n-- connate water saturation"])
        fout.writelines(["\n--", str(num_grid_blocks), "*", str(SWL)])
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--SWCR"])
        fout.writelines(["\n-- critical water saturation"])
        fout.writelines(["\n--", str(num_grid_blocks), "*", str(SWCR)])
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--SOWCR"])
        fout.writelines(["\n-- critical oil-in-water saturation"])
        fout.writelines(["\n--", str(num_grid_blocks), "*", str(SOWCR)])
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--SWU"])
        fout.writelines(["\n-- maximum water saturation"])
        fout.writelines(["\n--", str(num_grid_blocks), "*", str(SWU)])
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--KRW"])
        fout.writelines(["\n-- water relative permeability scaling factor"])
        fout.writelines(["\n--", str(num_grid_blocks), "*", str(KRW)])
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--KRO"])
        fout.writelines(["\n-- oil relative permeability scaling factor"])
        fout.writelines(["\n--", str(num_grid_blocks), "*", str(KRO)])
        fout.writelines(["\n--/\n"])

    elif grid_type in {"extended-core", "extended-core-refined"}:
        fout.writelines(["\n--SWL"])
        fout.writelines(["\n-- connate water saturation"])
        fout.writelines(
            [
                "\n--",
                str(0.0),
                "\t",
                str(num_grid_blocks),
                "*",
                str(SWL),
                "\t",
                str(0.0),
            ]
        )
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--SWCR"])
        fout.writelines(["\n-- critical water saturation"])
        fout.writelines(
            [
                "\n--",
                str(0.0),
                "\t",
                str(num_grid_blocks),
                "*",
                str(SWCR),
                "\t",
                str(0.0),
            ]
        )
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--SOWCR"])
        fout.writelines(["\n-- critical oil-in-water saturation"])
        fout.writelines(
            [
                "\n--",
                str(0.0),
                "\t",
                str(num_grid_blocks),
                "*",
                str(SOWCR),
                "\t",
                str(0.0),
            ]
        )
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--SWU"])
        fout.writelines(["\n-- maximum water saturation"])
        fout.writelines(
            [
                "\n--",
                str(1.0),
                "\t",
                str(num_grid_blocks),
                "*",
                str(SWU),
                "\t",
                str(1.0),
            ]
        )
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--KRW"])
        fout.writelines(["\n-- water relative permeability scaling factor"])
        fout.writelines(
            [
                "\n--",
                str(1.0),
                "\t",
                str(num_grid_blocks),
                "*",
                str(KRW),
                "\t",
                str(1.0),
            ]
        )
        fout.writelines(["\n--/\n"])

        fout.writelines(["\n--KRO"])
        fout.writelines(["\n-- oil relative permeability scaling factor"])
        fout.writelines(
            [
                "\n--",
                str(1.0),
                "\t",
                str(num_grid_blocks),
                "*",
                str(KRO),
                "\t",
                str(1.0),
            ]
        )
        fout.writelines(["\n--/\n"])

    # Close file
    fout.close()


def write_saturation_functions_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    relperms,
    cappress,
    num_sw_points,
    parameters,
    verbose,
):
    filename = os.path.join(wdir, "include", project_name + "_SWOF.INC")

    # Open file
    fout = open(filename, "w")
    is_new_file = False

    # header
    fout.writelines(["SWOF"])
    fout.writelines(["\n-- Sw\tkrw\tkro\tpcow"])

    # relperm parameters
    relperms2 = "Corey"
    cappress2 = "Corey"
    parameters2 = {
        "CO": float(1.0),
        "CW": float(1.0),
        "CP": float(1.0),
        "KRO": float(1.0),
        "KRW": float(1.0),
        "PD": float(0.0),
        "SWL": float(0.0),
        "SOWCR": float(0.0),
        "SWI": float(0.0),
    }

    # custom table
    fout.writelines(["\n-- table 1: krw, kro = ", relperms, ", pcow = ", cappress])
    # Close file
    fout.close()
    sat_funcs.write_SWOF(
        filename, is_new_file, relperms, cappress, num_sw_points, parameters, verbose
    )

    # linear permability table
    # Open file
    fout = open(filename, "a")
    fout.writelines(["\n/"])
    fout.writelines(["\n-- table 2: krw, kro = linear, pcow = 0"])
    # Close file
    fout.close()
    sat_funcs.write_SWOF(
        filename, is_new_file, relperms2, cappress2, num_sw_points, parameters2, verbose
    )
    # Open file
    fout = open(filename, "a")
    fout.writelines(["\n/"])
    # Close file
    fout.close()

    del parameters2


def write_pvt_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    distance_to_inlet,
    density_oil,
    viscosity_oil,
    viscosibility_oil,
    density_water,
    viscosity_water,
    viscosibility_water,
    rock_compressibility,
    sameGrav,
    verbose,
):
    filename = os.path.join(wdir, "include", project_name + "_PVT.INC")

    Pref = float(1.0)

    Bwater = float(1.0)
    Cwater = float(0.0)

    Boil = float(1.0)
    Coil = float(0.0)

    # Open file
    fout = open(filename, "w")

    if (experiment_name == "CENT") and (not sameGrav):
        # grid parameters
        (
            num_cells,
            num_refined_cells,
            num_first_cells,
            num_last_cells,
            dl,
            dr,
        ) = grid_blocks(experiment_name, flooding, grid_type, num_grid_blocks, length)
        gmult = cell_gravity_multipliers(
            sameGrav,
            num_cells,
            num_first_cells,
            num_last_cells,
            length,
            distance_to_inlet,
            dr,
        )

        fout.writelines(["ROCK"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--Rock Properties"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--\treference pressure[atma]\trock compressibility[1/atm]"])
        for i in range(0, num_cells):
            fout.writelines(
                ["\n\t", str(Pref), "\t", str(rock_compressibility), "\t/\n"]
            )
        fout.writelines(["\n"])

        fout.writelines(["\nPVTW"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--Water PVT properties->INCOMP"])
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--\treference pressure[atma]\tformation volume factor\tcompressibility[1/atm]\tviscosity[cP]\tviscosibility(1/mu*d(mu)/dp)[1/atm]"
            ]
        )
        for i in range(0, num_cells):
            fout.writelines(
                [
                    "\n\t",
                    str(Pref),
                    "\t",
                    str(Bwater),
                    "\t",
                    str(Cwater),
                    "\t",
                    str(viscosity_water),
                    "\t",
                    str(viscosibility_water),
                    "\t/\n",
                ]
            )
        fout.writelines(["\n"])

        fout.writelines(["\nPVCDO"])
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--Dead oil PVT properties with const. compressibility & dead oil (no gas)-> INCOMP"
            ]
        )
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--\treference pressure[atma]\tformation volume factor\tcompressibility[1/atm]\tviscosity[cP]\tviscosibility(1/mu*d(mu)/dp)[1/atm]"
            ]
        )
        for i in range(0, num_cells):
            fout.writelines(
                [
                    "\n\t",
                    str(Pref),
                    "\t",
                    str(Boil),
                    "\t",
                    str(Coil),
                    "\t",
                    str(viscosity_oil),
                    "\t",
                    str(viscosibility_oil),
                    "\t/\n",
                ]
            )
        fout.writelines(["\n"])

        fout.writelines(["\nDENSITY"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--Fluid Densities at Surface Conditions"])
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--\tdensity of oil at surf. cond. [gm/cc]\tdensity of water at surf. cond. [gm/cc]\tdensity of gas at surf. cond. [gm/cc]"
            ]
        )
        for i in range(0, num_cells):
            fout.writelines(
                [
                    "\n\t",
                    str(gmult[i] * density_oil),
                    "\t",
                    str(gmult[i] * density_water),
                    "\t1*",
                    "\t/\n",
                ]
            )
        fout.writelines(["\n"])

    else:
        fout.writelines(["ROCK"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--Rock Properties"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--\treference pressure[atma]\trock compressibility[1/atm]"])
        fout.writelines(["\n\t", str(Pref), "\t", str(rock_compressibility)])
        fout.writelines(["\n/\n"])

        fout.writelines(["\nPVTW"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--Water PVT properties->INCOMP"])
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--\treference pressure[atma]\tformation volume factor\tcompressibility[1/atm]\tviscosity[cP]\tviscosibility(1/mu*d(mu)/dp)[1/atm]"
            ]
        )
        fout.writelines(
            [
                "\n\t",
                str(Pref),
                "\t",
                str(Bwater),
                "\t",
                str(Cwater),
                "\t",
                str(viscosity_water),
                "\t",
                str(viscosibility_water),
            ]
        )
        fout.writelines(["\n/\n"])

        fout.writelines(["\nPVCDO"])
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--Dead oil PVT properties with const. compressibility & dead oil (no gas)-> INCOMP"
            ]
        )
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--\treference pressure[atma]\tformation volume factor\tcompressibility[1/atm]\tviscosity[cP]\tviscosibility(1/mu*d(mu)/dp)[1/atm]"
            ]
        )
        fout.writelines(
            [
                "\n\t",
                str(Pref),
                "\t",
                str(Boil),
                "\t",
                str(Coil),
                "\t",
                str(viscosity_oil),
                "\t",
                str(viscosibility_oil),
            ]
        )
        fout.writelines(["\n/\n"])

        fout.writelines(["\nDENSITY"])
        fout.writelines(["\n--"])
        fout.writelines(["\n--Fluid Densities at Surface Conditions"])
        fout.writelines(["\n--"])
        fout.writelines(
            [
                "\n--\tdensity of oil at surf. cond. [gm/cc]\tdensity of water at surf. cond. [gm/cc]\tdensity of gas at surf. cond. [gm/cc]"
            ]
        )
        fout.writelines(
            [
                "\n\t",
                str(density_oil),
                "\t",
                str(density_water),
                "\t1*",
            ]
        )
        fout.writelines(["\n/\n"])

    # Close file
    fout.close()


# ============================================================================
# DATA FILE: 'REGIONS' SECTION
# ============================================================================


def write_regions_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    diameter,
    sameGrav,
    verbose,
):
    filename = os.path.join(wdir, "include", project_name + "_REG.INC")

    # Open file
    fout = open(filename, "w")

    if grid_type in {"core", "core-refined"}:
        fout.writelines(["SATNUM"])
        fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1)])
        fout.writelines(["\n/\n"])

        fout.writelines(["\nFIPNUM"])
        fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1)])
        fout.writelines(["\n/\n"])

    elif (experiment_name == "SS") or (experiment_name == "USS"):
        if grid_type in {"extended-core", "extended-core-refined"}:
            fout.writelines(["SATNUM"])
            fout.writelines(
                ["\n\t", str(2), "\t", str(num_grid_blocks), "*", str(1), "\t", str(2)]
            )
            fout.writelines(["\n/\n"])

            fout.writelines(["\nFIPNUM"])
            fout.writelines(
                ["\n\t", str(2), "\t", str(num_grid_blocks), "*", str(1), "\t", str(2)]
            )
            fout.writelines(["\n/\n"])

            # fout.writelines(['\nEQLNUM'])
            # fout.writelines(['\n\t', str( 1 ), '\t', str( num_grid_blocks ),'*', str( 2 ), '\t', str( 3 ) ])
            # fout.writelines(['\n/\n'])

    elif experiment_name == "CENT":
        # grid parameters
        (
            num_cells,
            num_refined_cells,
            num_first_cells,
            num_last_cells,
            dl,
            dr,
        ) = grid_blocks(experiment_name, flooding, grid_type, num_grid_blocks, length)

        # cross sections cells
        da = np.float64(math.sqrt(math.pi)) * np.float64(diameter) / np.float64(2.0)
        da_out = np.float64(da_out_factor * da)

        nx_cells = (
            int(1)
            if (int(da / (dx_out_factor * dl)) == 0)
            else int(da / (dx_out_factor * dl))
        )
        nx_out_cells = (
            int(1)
            if (int(da_out / (dx_out_factor * dl)) == 0)
            else int(da_out / (dx_out_factor * dl))
        )
        ny_cells = int(1)
        ny_out_cells = int(1)

        if grid_type in {"core", "core-refined"}:
            fout.writelines(["PVTNUM\n"])
            for i in range(0, num_cells):
                fout.writelines(["\t", str(i + 1)])
                if (i + 1) % 5 == 0:
                    fout.writelines(["\n"])
            if num_cells % 5 != 0:
                fout.writelines(["\n"])
            fout.writelines(["\t/\n"])

        elif grid_type in {"extended-core", "extended-core-refined"}:
            fout.writelines(["PVTNUM\n"])
            for i in range(0, num_cells):
                fout.writelines(["\t", str(i + 1)])
                if (i + 1) % 5 == 0:
                    fout.writelines(["\n"])
            if num_cells % 5 != 0:
                fout.writelines(["\n"])
            fout.writelines(["\t/\n"])

            fout.writelines(["\nSATNUM\n"])
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(2)])
            fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1), "\n"])
            for i in range(0, num_last_cells):
                fout.writelines(["\t", str(2)])
            fout.writelines(["\n/\n"])

            fout.writelines(["\nFIPNUM\n"])
            for i in range(0, num_first_cells):
                fout.writelines(["\t", str(2)])
            fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1), "\n"])
            for i in range(0, num_last_cells):
                fout.writelines(["\t", str(2)])
            fout.writelines(["\n/\n"])

            # fout.writelines(['\nEQLNUM\n'])
            # for i in range( 0 , num_first_cells ):
            #     fout.writelines( [ '\t', str( 2 ) ] )
            # fout.writelines( [ '\n\t', str( num_grid_blocks ), '*', str( 1 ), '\n' ] )
            # for i in range( 0 , num_last_cells ):
            #     fout.writelines( [ '\t', str( 2 ) ] )
            # fout.writelines( ['\n/\n'])

        elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            if not centrifuge3D:
                if grid_type in {"centrifuge-core-refined"}:
                    nx_cells_total = nx_cells + 2 * nx_out_cells
                    ny_cells_total = ny_cells
                    nxy_cells = (nx_cells + 2 * nx_out_cells) * ny_cells
                    nxy_left_cells = nx_out_cells * ny_cells
                    nxy_right_cells = nx_out_cells * ny_cells
                    nxy_centre_cells = nx_cells * ny_cells

                    if not sameGrav:
                        fout.writelines(["PVTNUM\n"])
                        for i in range(0, num_cells):
                            fout.writelines(["\t", str(nxy_cells), "*", str(i + 1)])
                            if (i + 1) % 5 == 0:
                                fout.writelines(["\n"])
                        if num_cells % 5 != 0:
                            fout.writelines(["\n"])
                        fout.writelines(["\t/\n"])

                    # top
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(1),
                            "\t",
                            str(nx_cells_total),
                            "\t",
                            str(1),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(1),
                            "\t",
                            str(num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_cells * num_first_cells), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_cells * num_first_cells), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( nxy_cells*num_first_cells ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # bottom
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(1),
                            "\t",
                            str(nx_cells_total),
                            "\t",
                            str(1),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(num_grid_blocks + num_first_cells + 1),
                            "\t",
                            str(num_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_cells * num_last_cells), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_cells * num_last_cells), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( nxy_cells*num_last_cells ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # left
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(1),
                            "\t",
                            str(nx_out_cells),
                            "\t",
                            str(1),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_left_cells * num_grid_blocks), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_left_cells * num_grid_blocks), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( nxy_left_cells*num_grid_blocks ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # right
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(nx_out_cells + nx_cells + 1),
                            "\t",
                            str(nx_cells_total),
                            "\t",
                            str(1),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_right_cells * num_grid_blocks), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_right_cells * num_grid_blocks), "*", str(2)]
                    )
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( nxy_right_cells*num_grid_blocks ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # centre
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(nx_out_cells + 1),
                            "\t",
                            str(nx_out_cells + nx_cells),
                            "\t",
                            str(1),
                            "\t",
                            str(ny_cells),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_centre_cells * num_grid_blocks), "*", str(1)]
                    )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(
                        ["\n\t", str(nxy_centre_cells * num_grid_blocks), "*", str(1)]
                    )
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( nxy_centre_cells*num_grid_blocks ),'*',str( 1 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])
                else:
                    if not sameGrav:
                        fout.writelines(["PVTNUM\n"])
                        for i in range(0, num_cells):
                            fout.writelines(["\t", str(3), "*", str(i + 1)])
                            if (i + 1) % 5 == 0:
                                fout.writelines(["\n"])
                        if num_cells % 5 != 0:
                            fout.writelines(["\n"])
                        fout.writelines(["\t/\n"])

                    # fout.writelines(['\nCOPY'])
                    # fout.writelines(['\n\t', '\'PVTNUM\'','\t', '\'EQLNUM\'', '\t/' ])
                    # sfout.writelines(['\n/\n'])

                    # top
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(1),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(["\n\t", str(3 * num_first_cells), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(["\n\t", str(3 * num_first_cells), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( 3*num_first_cells ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # bottom
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(1),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_grid_blocks + num_first_cells + 1),
                            "\t",
                            str(num_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(["\n\t", str(3 * num_last_cells), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(["\n\t", str(3 * num_last_cells), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( 3*num_last_cells ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # left
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( num_grid_blocks ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # right
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(3),
                            "\t",
                            str(3),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( num_grid_blocks ),'*',str( 2 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])

                    # centre
                    fout.writelines(["\nBOX"])
                    fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                    fout.writelines(
                        [
                            "\n",
                            str(2),
                            "\t",
                            str(2),
                            "\t",
                            str(1),
                            "\t",
                            str(1),
                            "\t",
                            str(num_first_cells + 1),
                            "\t",
                            str(num_grid_blocks + num_first_cells),
                        ]
                    )
                    fout.writelines(["\t/\n"])

                    fout.writelines(["\nSATNUM"])
                    fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1)])
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nFIPNUM"])
                    fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1)])
                    fout.writelines(["\n/\n"])

                    # fout.writelines(['\nEQLNUM'])
                    # fout.writelines(['\n\t', str( num_grid_blocks ),'*',str( 1 ) ])
                    # fout.writelines(['\n/\n'])

                    fout.writelines(["\nENDBOX\n"])
            else:
                if not sameGrav:
                    fout.writelines(["PVTNUM\n"])
                    for i in range(0, num_cells):
                        fout.writelines(["\t", str(9), "*", str(i + 1)])
                        if (i + 1) % 5 == 0:
                            fout.writelines(["\n"])
                    if num_cells % 5 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["\t/\n"])

                # top
                fout.writelines(["\nBOX"])
                fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                fout.writelines(
                    [
                        "\n",
                        str(1),
                        "\t",
                        str(3),
                        "\t",
                        str(1),
                        "\t",
                        str(3),
                        "\t",
                        str(1),
                        "\t",
                        str(num_first_cells),
                    ]
                )
                fout.writelines(["\t/\n"])

                fout.writelines(["\nSATNUM"])
                fout.writelines(["\n\t", str(9 * num_first_cells), "*", str(2)])
                fout.writelines(["\n/\n"])

                fout.writelines(["\nFIPNUM"])
                fout.writelines(["\n\t", str(9 * num_first_cells), "*", str(2)])
                fout.writelines(["\n/\n"])

                # fout.writelines(['\nEQLNUM'])
                # fout.writelines(['\n\t', str( 9*num_first_cells ),'*',str( 2 ) ])
                # fout.writelines(['\n/\n'])

                fout.writelines(["\nENDBOX\n"])

                # bottom
                fout.writelines(["\nBOX"])
                fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                fout.writelines(
                    [
                        "\n",
                        str(1),
                        "\t",
                        str(3),
                        "\t",
                        str(1),
                        "\t",
                        str(3),
                        "\t",
                        str(num_grid_blocks + num_first_cells + 1),
                        "\t",
                        str(num_cells),
                    ]
                )
                fout.writelines(["\t/\n"])

                fout.writelines(["\nSATNUM"])
                fout.writelines(["\n\t", str(9 * num_last_cells), "*", str(2)])
                fout.writelines(["\n/\n"])

                fout.writelines(["\nFIPNUM"])
                fout.writelines(["\n\t", str(9 * num_last_cells), "*", str(2)])
                fout.writelines(["\n/\n"])

                # fout.writelines(['\nEQLNUM'])
                # fout.writelines(['\n\t', str( 9*num_last_cells ),'*',str( 2 ) ])
                # fout.writelines(['\n/\n'])

                fout.writelines(["\nENDBOX\n"])

                # left
                fout.writelines(["\nBOX"])
                fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                fout.writelines(
                    [
                        "\n",
                        str(1),
                        "\t",
                        str(1),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                    ]
                )
                fout.writelines(["\t/\n"])

                fout.writelines(["\nSATNUM"])
                fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                fout.writelines(["\nFIPNUM"])
                fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                # fout.writelines(['\nEQLNUM'])
                # fout.writelines(['\n\t', str( num_grid_blocks ),'*',str( 2 ) ])
                # fout.writelines(['\n/\n'])

                fout.writelines(["\nENDBOX\n"])

                # right
                fout.writelines(["\nBOX"])
                fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                fout.writelines(
                    [
                        "\n",
                        str(3),
                        "\t",
                        str(3),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                    ]
                )
                fout.writelines(["\t/\n"])

                fout.writelines(["\nSATNUM"])
                fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                fout.writelines(["\nFIPNUM"])
                fout.writelines(["\n\t", str(num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                # fout.writelines(['\nEQLNUM'])
                # fout.writelines(['\n\t', str( num_grid_blocks ),'*',str( 2 ) ])
                # fout.writelines(['\n/\n'])

                fout.writelines(["\nENDBOX\n"])

                # back
                fout.writelines(["\nBOX"])
                fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                fout.writelines(
                    [
                        "\n",
                        str(1),
                        "\t",
                        str(3),
                        "\t",
                        str(1),
                        "\t",
                        str(1),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                    ]
                )
                fout.writelines(["\t/\n"])

                fout.writelines(["\nSATNUM"])
                fout.writelines(["\n\t", str(3 * num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                fout.writelines(["\nFIPNUM"])
                fout.writelines(["\n\t", str(3 * num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                # fout.writelines(['\nEQLNUM'])
                # fout.writelines(['\n\t', str( 3*num_grid_blocks ),'*',str( 2 ) ])
                # fout.writelines(['\n/\n'])

                fout.writelines(["\nENDBOX\n"])

                # front
                fout.writelines(["\nBOX"])
                fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                fout.writelines(
                    [
                        "\n",
                        str(1),
                        "\t",
                        str(3),
                        "\t",
                        str(3),
                        "\t",
                        str(3),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                    ]
                )
                fout.writelines(["\t/\n"])

                fout.writelines(["\nSATNUM"])
                fout.writelines(["\n\t", str(3 * num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                fout.writelines(["\nFIPNUM"])
                fout.writelines(["\n\t", str(3 * num_grid_blocks), "*", str(2)])
                fout.writelines(["\n/\n"])

                # fout.writelines(['\nEQLNUM'])
                # fout.writelines(['\n\t', str( 3*num_grid_blocks ),'*',str( 2 ) ])
                # fout.writelines(['\n/\n'])

                fout.writelines(["\nENDBOX\n"])

                # centre
                fout.writelines(["\nBOX"])
                fout.writelines(["\n-- ix1\tix2\tjy1\tjy2\tkz1\tkz2"])
                fout.writelines(
                    [
                        "\n",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(2),
                        "\t",
                        str(num_first_cells + 1),
                        "\t",
                        str(num_grid_blocks + num_first_cells),
                    ]
                )
                fout.writelines(["\t/\n"])

                fout.writelines(["\nSATNUM"])
                fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1)])
                fout.writelines(["\n/\n"])

                fout.writelines(["\nFIPNUM"])
                fout.writelines(["\n\t", str(num_grid_blocks), "*", str(1)])
                fout.writelines(["\n/\n"])

                # fout.writelines(['\nEQLNUM'])
                # fout.writelines(['\n\t', str( num_grid_blocks ),'*',str( 1 ) ])
                # fout.writelines(['\n/\n'])

                fout.writelines(["\nENDBOX\n"])

    # Close file
    fout.close()


# ============================================================================
# DATA FILE: 'SOLUTION' SECTION
# ============================================================================


def write_initial_conditions_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    stage,
    simcontrol_data,
    length,
    diameter,
    distance_to_inlet,
    sw_init,
    pressure_init,
    gravcons0,
    gravcons1,
    density_core,
    density_outside,
    sameGrav,
    verbose,
):
    # grid parameters
    (
        num_cells,
        num_refined_cells,
        num_first_cells,
        num_last_cells,
        dl,
        dr,
    ) = grid_blocks(experiment_name, flooding, grid_type, num_grid_blocks, length)

    # cross sections cells
    area = np.float64(math.pi * diameter**2 / 4.0)
    da = math.sqrt(area)
    dz = da

    filename = os.path.join(wdir, "include", project_name + "_INIT")

    if experiment_name == "CENT":
        filename += str(stage) + ".INC"

    elif (experiment_name == "SS") or (experiment_name == "USS"):
        filename += ".INC"

    # Open file
    fout = open(filename, "w")

    if experiment_name in {"SS", "USS"}:
        # initial pressure distribution
        permeability = 100.0  # mD
        total_rate = 100.0
        TR_per_unit_length = units_system.convert_transmissibility(permeability * area)
        kr = [1.0, 1.0]
        visc = [5.0, 1.0]
        M = min(kr[0] / visc[0], kr[1] / visc[1])  # mobility
        dp_dx = total_rate / M / TR_per_unit_length
        press = np.repeat(pressure_init, num_cells)
        # middle, from one before the last core cell to the first core cell backwards
        # 0      ...    N-1
        # p0
        #        pi
        #               pN-1
        for i in range(num_cells - num_last_cells - 2, num_first_cells - 1, -1):
            press[i] = press[i + 1] + dr[i] * dp_dx
        # outside left/top
        for i in range(num_first_cells - 1, -1, -1):
            press[i] = press[i + 1]  # + dr[i] * dp_dx
        # outside right/bottom
        for i in range(num_cells-num_last_cells, num_cells):
            press[i] = press[i - 1]  # - dr[i] * dp_dx

        if grid_type in {"core", "core-refined"}:
            fout.writelines(["SWAT"])
            fout.writelines(["\n\t", str(num_grid_blocks), "*", str(sw_init)])
            fout.writelines(["\n\t/\n"])

            fout.writelines(["\nPRESSURE"])
            # fout.writelines(["\n\t", str(num_grid_blocks), "*", str(pressure_init)])
            fout.writelines(["\n\t", *format_string(press.tolist())])
            fout.writelines(["\n\t/\n"])

            if not with_explicit_init:
                fout.writelines(["\nEQUIL"])
                datum_depth = 0.0
                press_datum_depth = da / 2.0
                owc = da  # core height
                pc_owc = 0.0
                fout.writelines(
                    [
                        "\n",
                        f"\t{str(datum_depth)}",
                        f"\t{str(press_datum_depth)}",
                        f"\t{str(owc)}",
                        f"\t{str(pc_owc)}",
                        f"\t8*",
                        "\t/\n",
                    ]
                )
                fout.writelines(["\n"])

        elif grid_type in {"extended-core", "extended-core-refined"}:
            sw_left = np.float64(1.0) if (sw_init > 0.5) else np.float64(0.0)
            sw_right = np.float64(1.0) if (sw_init > 0.5) else np.float64(0.0)
            if flooding == "drainage":
                sw_left = np.float64(1.0)
                sw_right = np.float64(1.0)
            elif flooding == "imbibition":
                sw_left = np.float64(0.0)
                sw_right = np.float64(0.0)

            fout.writelines(["SWAT"])
            fout.writelines(
                [
                    "\n\t",
                    str(sw_left),
                    "\t",
                    str(num_grid_blocks),
                    "*",
                    str(sw_init),
                    "\t",
                    str(sw_right),
                ]
            )
            fout.writelines(["\n\t/\n"])

            fout.writelines(["\nPRESSURE"])
            # fout.writelines(
            #     ["\n\t", str(num_grid_blocks + 2), "*", str(pressure_init)]
            # )
            fout.writelines(
                ["\n\t", *format_string(press.tolist())]
            )
            fout.writelines(["\n\t/\n"])

            if not with_explicit_init:
                fout.writelines(["EQUIL"])
                datum_depth = 0.0
                press_datum_depth = dz / 2.0
                owc = dz  # core height
                pc_owc = 0.0
                fout.writelines(
                    [
                        "\n",
                        f"\t{str(datum_depth)}",
                        f"\t{str(press_datum_depth)}",
                        f"\t{str(owc)}",
                        f"\t{str(pc_owc)}",
                        f"\t8*",
                        "\t/\n",
                    ]
                )
                fout.writelines(["\n"])

    elif experiment_name == "CENT":
        # grid parameters
        (
            num_cells,
            num_refined_cells,
            num_first_cells,
            num_last_cells,
            dl,
            dr,
        ) = grid_blocks(experiment_name, flooding, grid_type, num_grid_blocks, length)
        # cross sections cells
        da = np.float64(math.sqrt(math.pi) * diameter / 2.0)
        da_out = np.float64(da_out_factor * da)

        nx_cells = (
            int(1)
            if (int(da / (dx_out_factor * dl)) == 0)
            else int(da / (dx_out_factor * dl))
        )
        nx_out_cells = (
            int(1)
            if (int(da_out / (dx_out_factor * dl)) == 0)
            else int(da_out / (dx_out_factor * dl))
        )
        ny_cells = int(1)
        ny_out_cells = int(1)

        sw_outside = np.float64(0.0) if (sw_init > 0.5) else np.float64(1.0)
        sw_in = np.float64(0.0) if (sw_init > 0.5) else np.float64(1.0)
        sw_out = np.float64(0.0) if (sw_init > 0.5) else np.float64(1.0)
        if flooding == "drainage":
            sw_outside = np.float64(0.0)
            sw_in = np.float64(0.0)
            sw_out = np.float64(0.0) if (footbath == False) else np.float64(1.0)
        elif flooding == "imbibition":
            sw_outside = np.float64(1.0)
            sw_in = np.float64(1.0) if (footbath == False) else np.float64(0.0)
            sw_out = np.float64(1.0)

        if grid_type in {"core", "core-refined"}:
            if stage == 0:
                fout.writelines(["SWAT"])
                fout.writelines(["\n", str(num_grid_blocks), "*", str(sw_init)])
                fout.writelines(["\n/\n"])

            # fout.writelines( ['\nPRESSURE'] )
            # fout.writelines( ['\n\t', str( num_grid_blocks ), '*', str( pressure_init ) ] )
            # fout.writelines( ['\n/\n'])

            (
                press_inlet,
                press_outlet,
                press_core,
                press_outside,
            ) = calculate_hydrostatic_pressure(
                experiment_name,
                flooding,
                grid_type,
                num_grid_blocks,
                length,
                distance_to_inlet,
                pressure_init,
                gravcons0,
                density_core,
                density_outside,
                sameGrav,
            )
            fout.writelines(["\nPRESSURE\n"])
            for i in range(0, num_grid_blocks):
                fout.writelines(["\t", str(press_core[i])])
                if i % 5 == 0:
                    fout.writelines(["\n"])
            if num_grid_blocks % 5 != 0:
                fout.writelines(["\n"])
            fout.writelines(["/\n"])
        elif grid_type in {"extended-core", "extended-core-refined"}:
            if stage == 0:
                fout.writelines(["SWAT\n"])
                for i in range(0, num_first_cells):
                    fout.writelines(["\t", str(sw_outside)])
                fout.writelines(["\n\t", str(num_grid_blocks), "*", str(sw_init), "\n"])
                for i in range(0, num_last_cells):
                    fout.writelines(["\t", str(sw_outside)])
                fout.writelines(["\n/\n"])

            # fout.writelines( ['\nPRESSURE'] )
            # fout.writelines( [ '\n\t', str( num_cells ) , '*', str( pressure_init ) ] )
            # fout.writelines( ['\n/\n'])

            (
                press_inlet,
                press_outlet,
                press_core,
                press_outside,
            ) = calculate_hydrostatic_pressure(
                experiment_name,
                flooding,
                grid_type,
                num_grid_blocks,
                length,
                distance_to_inlet,
                pressure_init,
                gravcons0,
                density_core,
                density_outside,
                sameGrav,
            )
            fout.writelines(["\nPRESSURE\n"])
            for i in range(0, num_cells):
                fout.writelines(["\t", str(press_outside[i])])
                if i % 5 == 0:
                    fout.writelines(["\n"])
            if num_cells % 5 != 0:
                fout.writelines(["\n"])
            fout.writelines(["/\n"])
        elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            if not centrifuge3D:
                if grid_type in {"centrifuge-core-refined"}:
                    nx_cells_total = nx_cells + 2 * nx_out_cells
                    ny_cells_total = ny_cells
                    nxy_cells = (nx_cells + 2 * nx_out_cells) * ny_cells
                    nxy_left_cells = nx_out_cells * ny_cells
                    nxy_right_cells = nx_out_cells * ny_cells
                    nxy_centre_cells = nx_cells * ny_cells

                    if stage == 0:
                        fout.writelines(["SWAT\n"])
                        for i in range(0, num_first_cells):
                            fout.writelines(
                                ["\t", str(nxy_left_cells), "*", str(sw_outside)]
                            )
                            if i == num_first_cells - 1:
                                fout.writelines(
                                    ["\t", str(nxy_centre_cells), "*", str(sw_in)]
                                )
                            else:
                                fout.writelines(
                                    ["\t", str(nxy_centre_cells), "*", str(sw_outside)]
                                )
                            fout.writelines(
                                ["\t", str(nxy_right_cells), "*", str(sw_outside)]
                            )
                            if (i + 1) % 2 == 0:
                                fout.writelines(["\n"])
                        if num_first_cells % 2 != 0:
                            fout.writelines(["\n"])
                        for i in range(0, num_grid_blocks):
                            fout.writelines(
                                [
                                    "\t",
                                    str(nxy_left_cells),
                                    "*",
                                    str(sw_outside),
                                    "\t",
                                    str(nxy_centre_cells),
                                    "*",
                                    str(sw_init),
                                    "\t",
                                    str(nxy_right_cells),
                                    "*",
                                    str(sw_outside),
                                ]
                            )
                            if (i + 1) % 2 == 0:
                                fout.writelines(["\n"])
                        if num_grid_blocks % 2 != 0:
                            fout.writelines(["\n"])
                        for i in range(0, num_last_cells):
                            fout.writelines(
                                ["\t", str(nxy_left_cells), "*", str(sw_outside)]
                            )
                            if i == 0:
                                fout.writelines(
                                    ["\t", str(nxy_centre_cells), "*", str(sw_out)]
                                )
                            else:
                                fout.writelines(
                                    ["\t", str(nxy_centre_cells), "*", str(sw_outside)]
                                )
                            fout.writelines(
                                ["\t", str(nxy_right_cells), "*", str(sw_outside)]
                            )
                            if (i + 1) % 2 == 0:
                                fout.writelines(["\n"])
                        if num_last_cells % 2 != 0:
                            fout.writelines(["\n"])
                        fout.writelines(["/\n"])

                    # fout.writelines( ['\nPRESSURE'] )
                    # fout.writelines( [ '\n\t', str( nxy_cells*num_cells ) , '*', str( pressure_init ) ] )
                    # fout.writelines( ['\n/\n'])

                    (
                        press_inlet,
                        press_outlet,
                        press_core,
                        press_outside,
                    ) = calculate_hydrostatic_pressure(
                        experiment_name,
                        flooding,
                        grid_type,
                        num_grid_blocks,
                        length,
                        distance_to_inlet,
                        pressure_init,
                        gravcons0,
                        density_core,
                        density_outside,
                        sameGrav,
                    )
                    fout.writelines(["\nPRESSURE\n"])
                    for i in range(0, num_cells):
                        fout.writelines(
                            ["\t", str(nxy_cells), "*", str(press_outside[i])]
                        )
                        if i % 5 == 0:
                            fout.writelines(["\n"])
                    if num_cells % 5 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                else:
                    if stage == 0:
                        fout.writelines(["SWAT\n"])
                        for i in range(0, num_first_cells):
                            fout.writelines(["\t", str(sw_outside)])
                            if i == num_first_cells - 1:
                                fout.writelines(["\t", str(sw_in)])
                            else:
                                fout.writelines(["\t", str(sw_outside)])
                            fout.writelines(["\t", str(sw_outside)])
                            if (i + 1) % 2 == 0:
                                fout.writelines(["\n"])
                        if num_first_cells % 2 != 0:
                            fout.writelines(["\n"])
                        for i in range(0, num_grid_blocks):
                            fout.writelines(
                                [
                                    "\t",
                                    str(sw_outside),
                                    "\t",
                                    str(sw_init),
                                    "\t",
                                    str(sw_outside),
                                ]
                            )
                            if (i + 1) % 2 == 0:
                                fout.writelines(["\n"])
                        if num_grid_blocks % 2 != 0:
                            fout.writelines(["\n"])
                        for i in range(0, num_last_cells):
                            fout.writelines(["\t", str(sw_outside)])
                            if i == 0:
                                fout.writelines(["\t", str(sw_out)])
                            else:
                                fout.writelines(["\t", str(sw_outside)])
                            fout.writelines(["\t", str(sw_outside)])
                            if (i + 1) % 2 == 0:
                                fout.writelines(["\n"])
                        if num_last_cells % 2 != 0:
                            fout.writelines(["\n"])
                        fout.writelines(["/\n"])

                        fout.writelines(["\nPRESSURE"])
                        fout.writelines(
                            ["\n\t", str(3 * num_cells), "*", str(pressure_init)]
                        )
                        fout.writelines(["\n/\n"])
                        if verbose:
                            print(
                                "\nstage = ",
                                stage,
                                ", initial pressure = ",
                                pressure_init,
                            )

                        # press_inlet, press_outlet, press_core, press_outside = \
                        #     calculate_hydrostatic_pressure( experiment_name, flooding, grid_type, num_grid_blocks, length, distance_to_inlet, pressure_init, gravcons0, density_core, density_outside, sameGrav )

                        # fout.writelines( ['\nPRESSURE\n'] )
                        # for i in range( 0, num_cells ):
                        #    fout.writelines( [ '\t', str( 3 ), '*', str( press_outside[ i ] ) ] )
                        #    if( i%5 == 0 ):
                        #        fout.writelines( [ '\n' ] )
                        # if( num_cells%5 != 0 ):
                        #    fout.writelines( [ '\n' ] )
                        # fout.writelines( ['/\n'])
                        # if(verbose)
                        #    print('\ncycle[', stage, '] initial pressure:\n', press_outside )

                    else:
                        (
                            press_inlet0,
                            press_outlet0,
                            press_core0,
                            press_outside0,
                        ) = calculate_hydrostatic_pressure(
                            experiment_name,
                            flooding,
                            grid_type,
                            num_grid_blocks,
                            length,
                            distance_to_inlet,
                            pressure_init,
                            gravcons0,
                            density_core,
                            density_outside,
                            sameGrav,
                        )
                        (
                            press_inlet1,
                            press_outlet1,
                            press_core1,
                            press_outside1,
                        ) = calculate_hydrostatic_pressure(
                            experiment_name,
                            flooding,
                            grid_type,
                            num_grid_blocks,
                            length,
                            distance_to_inlet,
                            pressure_init,
                            gravcons1,
                            density_core,
                            density_outside,
                            sameGrav,
                        )

                        # fout.writelines( ['\nPRESSURE\n'] )
                        # for i in range( 0, num_cells ):
                        #    fout.writelines( [ '\t', str( 3 ), '*', str( press_outside[ i ] ) ] )
                        #    if( i%5 == 0 ):
                        #        fout.writelines( [ '\n' ] )
                        # if( num_cells%5 != 0 ):
                        #    fout.writelines( [ '\n' ] )
                        # fout.writelines( ['/\n'])
                        # if(verbose):
                        #    print('\ncycle[', stage, '] initial pressure:\n', press_outside )

                        fout.writelines(["\nADD"])

                        # for i in range( 0 , num_cells ):
                        #    j = int( i+1 )
                        #    fout.writelines( ['\n\tPRESSURE\t', str( press_outside[num_cells-1] ), '\t', str( 1 ), '\t', str( 3 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( j ), '\t', str( j ), '\t/'] )
                        #    fout.writelines( ['\n\tPRESSURE\t', str( press_outside1[i]-press_outside0[i] ), '\t', str( 1 ), '\t', str( 3 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( j ), '\t', str( j ), '\t/'] )

                        # fout.writelines( ['\n\tPRESSURE\t', str( press_outside1[num_cells-1] ), '\t', str( 1 ), '\t', str( 3 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_cells ), '\t/'] )
                        # fout.writelines( ['\n\tPRESSURE\t', str( press_outside1[num_cells-1]-press_outside0[num_cells-1] ), '\t', str( 1 ), '\t', str( 3 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( num_cells ), '\t/'] )

                        fout.writelines(
                            [
                                "\n\tPRESSURE\t",
                                str(
                                    press_outside1[num_first_cells - 1]
                                    - press_outside0[num_first_cells - 1]
                                ),
                                "\t",
                                str(1),
                                "\t",
                                str(3),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(num_first_cells),
                                "\t/",
                            ]
                        )
                        fout.writelines(
                            [
                                "\n\tPRESSURE\t",
                                str(
                                    press_outside1[
                                        num_first_cells + num_grid_blocks - 1
                                    ]
                                    - press_outside0[
                                        num_first_cells + num_grid_blocks - 1
                                    ]
                                ),
                                "\t",
                                str(1),
                                "\t",
                                str(3),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(num_first_cells + 1),
                                "\t",
                                str(num_first_cells + num_grid_blocks),
                                "\t/",
                            ]
                        )
                        fout.writelines(
                            [
                                "\n\tPRESSURE\t",
                                str(
                                    press_outside1[num_cells - 1]
                                    - press_outside0[num_cells - 1]
                                ),
                                "\t",
                                str(1),
                                "\t",
                                str(3),
                                "\t",
                                str(1),
                                "\t",
                                str(1),
                                "\t",
                                str(num_first_cells + num_grid_blocks + 1),
                                "\t",
                                str(num_cells),
                                "\t/",
                            ]
                        )

                        fout.writelines(["\n/\n"])

            else:
                if stage == 0:
                    fout.writelines(["SWAT\n"])
                    for i in range(0, num_first_cells):
                        fout.writelines(["\t", str(4), "*", str(sw_outside)])
                        if i == num_first_cells - 1:
                            fout.writelines(["\t", str(sw_in)])
                        else:
                            fout.writelines(["\t", str(sw_outside)])
                        fout.writelines(["\t", str(4), "*", str(sw_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_first_cells % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_grid_blocks):
                        fout.writelines(["\t", str(4), "*", str(sw_outside)])
                        fout.writelines(["\t", str(sw_init)])
                        fout.writelines(["\t", str(4), "*", str(sw_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_grid_blocks % 2 != 0:
                        fout.writelines(["\n"])
                    for i in range(0, num_last_cells):
                        fout.writelines(["\t", str(4), "*", str(sw_outside)])
                        if i == 0:
                            fout.writelines(["\t", str(sw_out)])
                        else:
                            fout.writelines(["\t", str(sw_outside)])
                        fout.writelines(["\t", str(4), "*", str(sw_outside)])
                        if (i + 1) % 2 == 0:
                            fout.writelines(["\n"])
                    if num_last_cells % 2 != 0:
                        fout.writelines(["\n"])
                    fout.writelines(["/\n"])

                fout.writelines(["\nPRESSURE"])
                fout.writelines(["\n\t", str(9 * num_cells), "*", str(pressure_init)])
                fout.writelines(["\n/\n"])

                # press_inlet, press_outlet, press_core, press_outside = \
                #     calculate_hydrostatic_pressure( experiment_name, flooding, grid_type, num_grid_blocks, length, distance_to_inlet, pressure_init, gravcons0, density_core, density_outside, sameGrav )
                # fout.writelines( ['\nPRESSURE\n'] )
                # for i in range( 0, num_cells ):
                #    fout.writelines( [ '\t', str( 9 ), '*', str( press_outside[ i ] ) ] )
                #    if( i%5 == 0 ):
                #        fout.writelines( [ '\n' ] )
                # if( num_cells%5 != 0 ):
                #    fout.writelines( [ '\n' ] )
                # fout.writelines( ['/\n'])

    # close file
    fout.close()


# ============================================================================
# DATA FILE: 'SUMMARY' SECTION
# ============================================================================


def write_summary_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    diameter,
    verbose,
):
    """
    Unsupported keywords:
        RPTSMRY, EXCEL,
        ROFTL,
        FOPV, ROPV, FWPV, RWPV, FOSAT, ROSAT, FWSAT, RWSAT
    """
    filename = os.path.join(wdir, "include", project_name + "_SUM.INC")

    # Open file
    fout = open(filename, "w")

    fout.writelines(["\n--- tabulated output in separate RSM file"])
    fout.writelines(["\nRUNSUM\n"])

    # @TODO: create universal approach
    # legacy version
    # the code is kept for potential use in future
    legacy_versions = False

    if legacy_versions:
        # ECLIPSE:
        fout.writelines(["RPTSMRY"])
        fout.writelines(["\n\t1\t/\n"])
        # OPM:

        # @TODO: create universal approach
        # ECLIPSE:
        fout.writelines(
            [
                "\n--- identifies that run summary output, generated by using the RUNSUM keyword"
            ]
        )
        fout.writelines(
            ["\n--- will be written in a format that can be easily imported into Excel"]
        )
        fout.writelines(["\nEXCEL\n"])
        # OPM:

    fout.writelines(["\n--- well bottom hole pressure"])
    fout.writelines(["\nWBHP"])
    fout.writelines(["\n\t/\n"])

    fout.writelines(["\n--- well bottom hole pressure ( history )"])
    fout.writelines(["\n--WBHPH"])
    fout.writelines(["\n--\t/\n"])

    fout.writelines(["\n-- Average pressure for field"])
    fout.writelines(["\nFPR\n"])
    fout.writelines(["\n-- Average pressure for all regions"])
    fout.writelines(["\nRPR"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n----------"])

    if grid_type in {
        "extended-core",
        "extended-core-refined",
        "centrifuge-core",
        "centrifuge-core-refined",
    }:
        fout.writelines(["\n----------"])
        if legacy_versions:
            # @TODO: create universal approach
            # ECLIPSE:
            # ROFTL( interregion oil flow total - liquid phase)
            fout.writelines(["\n-- inter region oil flow total"])
            fout.writelines(["\nROFTL"])
            fout.writelines(["\n\t", str(1), "\t", str(2), "\t/\n"])
            fout.writelines(["\n/\n"])

        # OPM:
        # ROFT( interregion oil flow total - liquid and wet gas phase)
        fout.writelines(["\nROFT"])  # liquid + wet gas phase
        fout.writelines(["\n\t", str(1), "\t", str(2), "\t/"])
        fout.writelines(["\n/\n"])

        # RWFT( interregion water flow total - liquid and wet gas phase)
        fout.writelines(["\n-- inter region water flow total"])
        fout.writelines(["\nRWFT"])
        fout.writelines(["\n\t", str(1), "\t", str(2), "\t/"])
        fout.writelines(["\n/\n"])

    fout.writelines(["\n-- Oil in place for field"])
    fout.writelines(["\nFOIP\n"])
    fout.writelines(["\n-- Oil in place for all regions"])
    fout.writelines(["\nROIP"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n-- Water in place for field"])
    fout.writelines(["\nFWIP\n"])
    fout.writelines(["\n-- Water in place for all regions"])
    fout.writelines(["\nRWIP"])
    fout.writelines(["\n/\n"])

    if legacy_versions:
        fout.writelines(["\n-- Oil pore volume for field"])
        fout.writelines(["\nFOPV\n"])
        fout.writelines(["\n-- Oil pore volume for all regions"])
        fout.writelines(["\nROPV"])
        fout.writelines(["\n/\n"])

    if legacy_versions:
        fout.writelines(["\n-- Water pore volume for field"])
        fout.writelines(["\nFWPV\n"])
        fout.writelines(["\n-- Water pore volume for all regions"])
        fout.writelines(["\nRWPV"])
        fout.writelines(["\n/\n"])

    if legacy_versions:
        fout.writelines(["\n-- Average oil saturation for field"])
        fout.writelines(["\nFOSAT\n"])
        fout.writelines(["\n-- Average oil saturation for all regions"])
        fout.writelines(["\nROSAT"])
        fout.writelines(["\n/\n"])
        fout.writelines(["\n-- Average water saturation for field"])
        fout.writelines(["\nFWSAT\n"])
        fout.writelines(["\n-- Average water saturation for all regions"])
        fout.writelines(["\nRWSAT"])
        fout.writelines(["\n/\n"])

    fout.writelines(["\n----------"])
    fout.writelines(
        [
            "\n-- Water/oil/liquid inj. rate and cumulative wat inj. for field and for every well"
        ]
    )

    fout.writelines(["\n-- field water injection rate"])
    fout.writelines(["\nFWIR\n"])
    fout.writelines(["\n-- well water injection rate"])
    fout.writelines(["\nWWIR"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n-- field water injection total"])
    fout.writelines(["\nFWIT\n"])
    fout.writelines(["\n-- region water injection total"])
    fout.writelines(["\nRWIT"])
    fout.writelines(["\n/\n"])
    fout.writelines(["\n-- well water injection total"])
    fout.writelines(["\nWWIT"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n-- field oil injection rate"])
    fout.writelines(["\nFOIR\n"])
    fout.writelines(["\n-- well water injection rate"])
    fout.writelines(["\nWOIR"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n-- field oil injection total"])
    fout.writelines(["\nFOIT\n"])
    fout.writelines(["\n-- region oil injection total"])
    fout.writelines(["\nROIT"])
    fout.writelines(["\n/\n"])
    fout.writelines(["\n-- well oil injection total"])
    fout.writelines(["\nWOIT"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n---------"])
    fout.writelines(
        [
            "\n-- Water/oil/liquid prod rate and cumulative oil prod for field and for every well"
        ]
    )

    fout.writelines(["\n-- field water production total"])
    fout.writelines(["\nFWPT\n"])
    fout.writelines(["\n-- region water production total"])
    fout.writelines(["\nRWPT"])
    fout.writelines(["\n/\n"])
    fout.writelines(["\n-- well water production total"])
    fout.writelines(["\nWWPT"])
    fout.writelines(["\n/\n"])
    fout.writelines(["\n-- field water production rate"])
    fout.writelines(["\nFWPR"])
    fout.writelines(["\n-- well water production rate"])
    fout.writelines(["\nWWPR"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n-- field oil production total"])
    fout.writelines(["\nFOPT\n"])
    fout.writelines(["\n-- region oil production total"])
    fout.writelines(["\nROPT"])
    fout.writelines(["\n/\n"])
    fout.writelines(["\n-- well oil production total"])
    fout.writelines(["\nWOPT"])
    fout.writelines(["\n/\n"])
    fout.writelines(["\n-- field oil production rate"])
    fout.writelines(["\nFOPR"])
    fout.writelines(["\n-- well oil production rate"])
    fout.writelines(["\nWOPR"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n-- field liquid production rate"])
    fout.writelines(["\nFLPR\n"])
    fout.writelines(["\n-- well liquid production rate"])
    fout.writelines(["\nWLPR"])
    fout.writelines(["\n/\n"])

    fout.writelines(["\n-- field liquid production total"])
    fout.writelines(["\nFLPT"])
    fout.writelines(["\n-- well liquid production total"])
    fout.writelines(["\nWLPT"])
    fout.writelines(["\n/\n"])

    # grid parameters
    num_cells, num_refined_cells, num_first_cells, num_last_cells, dl, dr = grid_blocks(
        experiment_name, flooding, grid_type, num_grid_blocks, length
    )
    # cross sections cells
    da = np.float64(math.sqrt(math.pi)) * np.float64(diameter) / np.float64(2.0)
    da_out = np.float64(da_out_factor * da)
    nx_cells = int(da / dl)
    ny_cells = int(da / dl)
    nx_out_cells = int(da_out / dl)
    ny_out_cells = int(da_out / dl)

    if (experiment_name == "SS") or (experiment_name == "USS"):
        fout.writelines(["\n--- Block water-oil capillary pressure"])
        fout.writelines(["\nBWPC"])
        for i in range(0, num_cells):
            fout.writelines(["\n\t", str(i + 1), "\t", str(1), "\t", str(1), "\t/"])
        fout.writelines(["\n/\n"])

        fout.writelines(["\n--- Block oil phase pressure"])
        fout.writelines(["\nBPR"])
        for i in range(0, num_cells):
            fout.writelines(["\n\t", str(i + 1), "\t", str(1), "\t", str(1), "\t/"])
        fout.writelines(["\n/\n"])

        fout.writelines(["\n--- Block water phase pressure"])
        fout.writelines(["\nBWPR"])
        for i in range(0, num_cells):
            fout.writelines(["\n\t", str(i + 1), "\t", str(1), "\t", str(1), "\t/"])
        fout.writelines(["\n/\n"])

        fout.writelines(["\n--- Block oil saturation"])
        fout.writelines(["\nBOSAT"])
        for i in range(0, num_cells):
            fout.writelines(["\n\t", str(i + 1), "\t", str(1), "\t", str(1), "\t/"])
        fout.writelines(["\n/\n"])

        fout.writelines(["\n--- Block water saturation"])
        fout.writelines(["\nBWSAT"])
        for i in range(0, num_cells):
            fout.writelines(["\n\t", str(i + 1), "\t", str(1), "\t", str(1), "\t/"])
        fout.writelines(["\n/\n"])

    elif experiment_name == "CENT":
        if grid_type not in {"centrifuge-core", "centrifuge-core-refined"}:
            fout.writelines(["\n--- Block water-oil capillary pressure"])
            fout.writelines(["\nBWPC"])
            for i in range(0, num_cells):
                fout.writelines(["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"])
            fout.writelines(["\n/\n"])

            fout.writelines(["\n--- Block oil phase pressure"])
            fout.writelines(["\nBPR"])
            for i in range(0, num_cells):
                fout.writelines(["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"])
            fout.writelines(["\n/\n"])

            fout.writelines(["\n--- Block water phase pressure"])
            fout.writelines(["\nBWPR"])
            for i in range(0, num_cells):
                fout.writelines(["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"])
            fout.writelines(["\n/\n"])

            fout.writelines(["\n--- Block oil saturation"])
            fout.writelines(["\nBOSAT"])
            for i in range(0, num_cells):
                fout.writelines(["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"])
            fout.writelines(["\n/\n"])

            fout.writelines(["\n--- Block water saturation"])
            fout.writelines(["\nBWSAT"])
            for i in range(0, num_cells):
                fout.writelines(["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"])
            fout.writelines(["\n/\n"])

        elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            if not centrifuge3D:
                fout.writelines(["\n--- Block water-oil capillary pressure"])
                fout.writelines(["\nBWPC"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block oil phase pressure"])
                fout.writelines(["\nBPR"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block water phase pressure"])
                fout.writelines(["\nBWPR"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block oil saturation"])
                fout.writelines(["\nBOSAT"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block water saturation"])
                fout.writelines(["\nBWSAT"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

            else:
                fout.writelines(["\n--- Block water-oil capillary pressure"])
                fout.writelines(["\nBWPC"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block oil phase pressure"])
                fout.writelines(["\nBPR"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block water phase pressure"])
                fout.writelines(["\nBWPR"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block oil saturation"])
                fout.writelines(["\nBOSAT"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

                fout.writelines(["\n--- Block water saturation"])
                fout.writelines(["\nBWSAT"])
                for i in range(0, num_cells):
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(1), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(2), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(1), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(2), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                    fout.writelines(
                        ["\n\t", str(3), "\t", str(3), "\t", str(i + 1), "\t/"]
                    )
                fout.writelines(["\n/\n"])

    # convergence and cpu use
    fout.writelines(["\n--- Number of Newton iterations for each timestep"])
    fout.writelines(["\nNEWTON\n"])

    fout.writelines(["\n--- Number of linear iterations for each timestep"])
    fout.writelines(["\nMLINEARS\n"])

    fout.writelines(["\n--- Time step lengths"])
    fout.writelines(["\nTIMESTEP\n"])

    # close file
    fout.close()


# ============================================================================
# DATA FILE: 'SCHEDULE' SECTION
# ============================================================================


def format_value(value, default=None):
    return str(value) if value is not None else str(default) if default else "1*"


def format_string(x, width=10, indent=0, left=True):
    if left:
        formatted_str = (
            lambda s: f'{" ":<{indent}}{s:<{width}}' if indent else f"{s:<{width}}"
        )
        return (
            formatted_str(x)
            if (isinstance(x, str))
            else [
                (" " if idx > 0 else "") + formatted_str(s) for idx, s in enumerate(x)
            ]
        )
    else:
        formatted_str = (
            lambda s: f'{" ":>{indent}}{s:>{width}}' if indent else f"{s:>{width}}"
        )
        return (
            formatted_str(x)
            if (isinstance(x, str))
            else [
                (" " if idx > 0 else "") + formatted_str(s) for idx, s in enumerate(x)
            ]
        )


def write_schedule_specs_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    length,
    simcontrol_data,
    wbhp_inj,
    wbhp_prod,
    timestep,
    newtmx,
    verbose,
):
    """
    Unsupported keywords: MESSOPTS
    """
    # @TODO: create universal approach
    # legacy version
    # the code is kept for potential use in future
    legacy_versions = False

    # @TODO: find universal setup
    # dx = 0.08
    # re = 0.2 * dx
    # well_diameter = 0.2 * np.float64(dx) # original
    # connection_factor = 1.0e8 (good)
    permeability = 100.0  # mD
    diameter = 4.0
    area = math.pi * (diameter**2) / 4.0
    dx = length / num_grid_blocks
    transmissibility_multiplier = 1.0
    connection_factor = units_system.convert_transmissibility(
        permeability * (area / dx) * transmissibility_multiplier
    )

    def write_compdat_header(fout):
        fout.writelines(["\n", "--\n", "--\t\tWELL CONNECTION DATA\n", "--\n"])
        fout.writelines(
            [
                *format_string(
                    [
                        "-- WELL",
                        "--",
                        "LOCATION",
                        "",
                        "--",
                        "OPEN",
                        "SAT",
                        "CONN",
                        "WELL",
                        "KH",
                        "SKIN",
                        "D",
                        "DIR",
                    ]
                ),
                "\n",
                *format_string(
                    [
                        "-- NAME",
                        "II",
                        "JJ",
                        "K1",
                        "K2",
                        "SHUT",
                        "TAB",
                        "FACT",
                        "DIA",
                        "FACT",
                        "FACT",
                        "FACT",
                        "PEN",
                    ]
                ),
            ]
        )

    filename = os.path.join(wdir, "include", project_name + "_SCH.INC")

    # Open file
    fout = open(filename, "w")

    fout.writelines(["\n-------------------------------"])
    fout.writelines(["\n-- simulator control parameters"])
    fout.writelines(["\n-------------------------------\n"])

    first_cell = 1
    last_cell = num_grid_blocks

    # reporting
    fout.writelines(["\n", "RPTSCHED", "\n"])
    fout.writelines(["\n", "\t'PRESS'", "\t/", "\n"])

    fout.writelines(["\n", "RPTRST", "\n"])
    fout.writelines(["\n", "\t'BASIC=1'", "\t/", "\n"])

    if grid_type in {"extended-core", "extended-core-refined"}:
        last_cell += 2
    elif grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
        (
            num_cells,
            num_refined_cells,
            num_first_cells,
            num_last_cells,
            dl,
            dr,
        ) = grid_blocks(experiment_name, flooding, grid_type, num_grid_blocks, length)
        last_cell = num_cells

    if (experiment_name == "SS") or (experiment_name == "USS"):
        # @TODO: create universal approach
        # # ECLIPSE:
        # fout.writelines(['GRUPTREE'])
        # fout.writelines(['\n\t','\'INJ\'','\t\'LAB\'\t/'])
        # fout.writelines(['\n\t','\'PROD\'','\t\'LAB\'\t/'])
        # fout.writelines(['\n/\n'])
        # OPM:
        # fout.writelines(["GRUPTREE"])
        # fout.writelines(["\n\t", "'INJW'", "\t'LAB'\t/"])
        # fout.writelines(["\n\t", "'INJO'", "\t'LAB'\t/"])
        # fout.writelines(["\n\t", "'PROD'", "\t'LAB'\t/"])
        # fout.writelines(["\n/\n"])
        pass

    trglcv = np.float64(0.00001)
    xxxlcv = np.float64(0.0001)
    trgddp = np.float64(1.0)
    trgdds = np.float64(0.01)

    newtmn = math.floor(1)
    litmax = int(25)
    litmin = math.floor(1)

    # tsinit = np.float64( timestep )
    # tsmax  = np.float64( 5.0*timestep )
    # tsmin  = np.float64( 0.5*timestep )
    # tsmchp = np.float64( 0.5*timestep )
    # tsfmax = np.float64( 2.0 )
    # tsfmin = np.float64( 0.5 )

    # tsinit = np.float64( timestep )
    # tsmax  = np.float64( 2.0*timestep )
    # tsmin  = np.float64( 0.1*timestep )
    # tsmchp = np.float64( 0.1*timestep )
    # tsfmax = np.float64( 2.0 )
    # tsfmin = np.float64( 0.1 )

    tsinit = np.float64(0.1 * timestep)
    tsmax = np.float64(2.0 * timestep)
    tsmin = np.float64(0.001 * timestep)
    tsmchp = np.float64(0.01 * timestep)
    tsfmax = np.float64(3.0)
    tsfmin = np.float64(0.01)
    tsfcnv = np.float64(0.1)
    tfdiff = np.float64(1.25)

    new_line = "\n"
    if timestep <= 0.0:
        new_line += "--"

    with_tuning = False
    # with_tuning = True

    if with_tuning:
        fout.writelines([new_line, "TUNING"])
        fout.writelines(["\n-- time step control"])
        fout.writelines(
            [
                "\n-- TSINIT(max init tstep)\tTSMAXZ(max tstep)\tTSMINZ(min tstep)\tTSMCHP( min chopable tstep)\tTSFMAX(max increase factor)\tTSFMIN(min cutback factor)"
            ]
        )
        fout.writelines(
            [
                "\n-- default:TSINIT(1)\tTSMAXZ(365)\tTSMINZ(0.1)\tTSMCHP(0.15)\tTSFMAX(3.0)\tTSFMIN(0.3)"
            ]
        )
        fout.writelines(
            [
                new_line,
                "\t",
                str(tsinit),
                "\t",
                str(tsmax),
                "\t",
                str(tsmin),
                "\t",
                str(tsmchp),
                "\t",
                str(tsfmax),
                "\t",
                str(tsfmin),
                "\t/",
            ]
        )
        fout.writelines(["\n-- convergence tolerance parameters"])
        fout.writelines([new_line, "\t/"])
        fout.writelines(["\n-- control of Newton and linear iterations"])
        fout.writelines(["\n-- newtnmx\tnewtmn\tlitmax\tlitmin\tmxwsit\tmxwpit"])
        fout.writelines(
            [
                "\n-- default: newtnmx(12)\tnewtmn(1)\tlitmax(25)\tlitmin(1)\tmxwsit(8)\tmxwpit(8)"
            ]
        )
        fout.writelines(
            [
                new_line,
                "\t",
                str(newtmx),
                "\t",
                str(newtmn),
                "\t",
                str(litmax),
                "\t",
                str(litmin),
                "\t",
                str(newtmx),
                "\t",
                str(newtmx),
                "\t/\n",
            ]
        )

    # fout.writelines([new_line,'TUNINGDP'])
    # fout.writelines(['\n-- solution change control'])
    # fout.writelines(['\n--Essentially, convergence is assumed when either the residual is small or the solution change is small'])
    # fout.writelines(['\n--TRGLCV(target linear convergence error)\tXXXLCV(maximum linear convergence error)\tTRGDDP(maximum pressure change during a Newton iteration)\tTRGDDS(maximum saturation change during a Newton iteration)'])
    # fout.writelines(['\n-- default:TRGLCV(0.00001)\tXXXLCV(365)\tTRGDDP(1.0)\tTRGDDS(0.01)'])
    # fout.writelines([new_line,'\t', str( trglcv ), '\t', str( xxxlcv ), '\t', str( trgddp ), '\t', str( trgdds ), '\t/\n'])

    if legacy_versions:
        fout.writelines(["\nMESSOPTS"])
        fout.writelines(["\n---reports forced timestep as message"])
        fout.writelines(["\n\tACCPTIME\t1\t/\n"])

    if (experiment_name == "SS") or (experiment_name == "USS"):
        fout.writelines(["\nWELSPECS"])
        fout.writelines(["\n--introduce the wells: prod and inj"])
        fout.writelines(["\n--wellname\tgroup\tI\tJ\tRefDepthForBHP\tPreferredPhase"])
        # @TODO: create universal approach
        # # ECLIPSE:
        # if( flooding == 'imbibition' ):
        #     fout.writelines(['\n\t','\'INJ\'','\tG\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'WATER\'','\t/'])
        # elif( flooding == 'drainage'):
        #     fout.writelines(['\n\t','\'INJ\'','\tG\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'OIL\'','\t/'])
        # production well
        # fout.writelines(['\n\t','\'PROD\'','\tG\t', str( last_cell ), '\t', str( 1 ),'\t1*\t','\'LIQ\'','\t/'])
        # # OPM:
        # if( flooding == 'imbibition' ):
        #     fout.writelines(['\n\t','\'INJW\'','\tG\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'WATER\'','\t/'])
        # elif( flooding == 'drainage'):
        #     fout.writelines(['\n\t','\'INJO\'','\tG\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'OIL\'','\t/'])
        # production well
        # fout.writelines(['\n\t','\'PROD\'','\tG\t', str( last_cell ), '\t', str( 1 ),'\t1*\t','\'OIL\'','\t/'])
        for phase, well_name in zip(phases, well_injectors):
            fout.writelines(
                [
                    "\n\t",
                    f"'{well_name}'",
                    "\tG\t",
                    str(first_cell),
                    "\t",
                    str(1),
                    "\t1*\t",
                    f"'{phase}'",
                    "\t/",
                ]
            )
        # production well
        if flooding == "imbibition":
            preferred_prod_phase = oil_phase_name
        else:  # if flooding == "drainage":
            preferred_prod_phase = wat_phase_name
        fout.writelines(
            [
                "\n\t",
                f"'{well_producer}'",
                "\tG\t",
                str(last_cell),
                "\t",
                str(1),
                "\t1*\t",
                f"'{preferred_prod_phase}'",
                "\t/",
            ]
        )
        fout.writelines(["\n/\n"])

        write_compdat_header(fout)
        fout.writelines(["\nCOMPDAT"])
        # @TODO: create universal approach
        # # ECLIPSE:
        # fout.writelines(['\n\t','\'INJ\'',  '\t', str( first_cell ), '\t', str( 1 ), '\t', str( 1 ), '\t', str( 1 ), '\t\'OPEN\'\t', '2*\t', str( 0.004 ), '\t/'])
        # OPM:
        for well_name in well_injectors:
            fout.writelines(
                [
                    "\n",
                    *format_string(
                        [
                            f"'{well_name}'",
                            str(first_cell),
                            str(1),
                            str(1),
                            str(1),
                            "'OPEN'",
                            "1*",
                            str(connection_factor),
                            "1*",
                            "1*",
                            str(0.0),
                            "1*",
                            "'Z'",
                        ]
                    ),
                    "\t/",
                ]
            )
        # production well
        fout.writelines(
            [
                "\n",
                *format_string(
                    [
                        f"'{well_producer}'",
                        str(last_cell),
                        str(1),
                        str(1),
                        str(1),
                        "'OPEN'",
                        "1*",
                        str(connection_factor),
                        "1*",
                        "1*",
                        str(0.0),
                        "1*",
                        "'X'",
                    ]
                ),
                "\t/",
            ]
        )
        fout.writelines(["\n/\n"])

        # fout.writelines(['\nWCONPROD'])
        # fout.writelines(['\n--wellname\tpFlag\tControlMode\tQo\tQw\tQg\tQl\tQr\tBHP'])
        # fout.writelines(['\n','\'PROD\'','\t','\'OPEN\'','\t','\'BHP\'','\t', '5*\t',str( wbhp_prod ), '\t/'])
        # fout.writelines(['\n/\n'])

    elif (
        (experiment_name == "CENT")
        and (grid_type != "centrifuge-core")
        and (grid_type != "centrifuge-core-refined")
    ):
        fout.writelines(["\nWELSPECS"])
        fout.writelines(["\n--introduce the wells: prod and inj"])
        fout.writelines(["\n--wellname\tgroup\tI\tJ\tRefDepthForBHP\tPreferredPhase"])
        if flooding == "imbibition":
            preferred_inj_phase = wat_phase_name
            preferred_prod_phase = wat_phase_name
        else:  # if flooding == "drainage":
            preferred_inj_phase = oil_phase_name
            preferred_prod_phase = oil_phase_name
        fout.writelines(
            [
                "\n\t",
                f"'{well_injector}'",
                "\tG1\t",
                str(1),
                "\t",
                str(1),
                "\t1*\t",
                f"'{preferred_inj_phase}'",
                "\t/",
            ]
        )
        preferred_prod_phase = "LIQ"
        fout.writelines(
            [
                "\n\t",
                f"'{well_producer}'",
                "\tG1\t",
                str(1),
                "\t",
                str(1),
                "\t1*\t",
                "'LIQ'",
                "\t/",
            ]
        )
        fout.writelines(["\n/\n"])

        write_compdat_header(fout)
        fout.writelines(["\nCOMPDAT"])
        if flooding == "imbibition":
            well_inj_cell = last_cell
            well_prod_cell = first_cell
        else:  # if flooding == "drainage":
            well_inj_cell = first_cell
            well_prod_cell = last_cell
        fout.writelines(
            [
                "\n",
                *format_string(
                    [
                        f"'{well_injector}'",
                        str(1),
                        str(1),
                        str(1),
                        str(well_inj_cell),
                        "'OPEN'",
                        "1*",
                        str(connection_factor),
                        "1*",
                        "1*",
                        str(0.0),
                        "1*",
                        "'X'",
                    ]
                ),
                "\t/",
            ]
        )
        fout.writelines(
            [
                "\n",
                *format_string(
                    [
                        f"'{well_producer}'",
                        str(1),
                        str(1),
                        str(1),
                        str(well_prod_cell),
                        "'OPEN'",
                        "1*",
                        str(connection_factor),
                        "1*",
                        "1*",
                        str(0.0),
                        "1*",
                        "'X'",
                    ]
                ),
                "\t/",
            ]
        )
        fout.writelines(["\n/\n"])

    # Close file
    fout.close()


def write_schedule_datafile(
    wdir,
    project_name,
    experiment_name,
    flooding,
    grid_type,
    num_grid_blocks,
    stage,
    simcontrol_data,
    wbhp_inj,
    wbhp_prod,
    time_data,
    timestep,
    newtmx,
    detailed_results_output,
    verbose,
):
    """
    Unsupported keywords: TIME
    """
    # @TODO: create universal approach
    # legacy version
    # the code is kept for potential use in future
    legacy_versions = False

    # @TODO: find universal setup
    # dx = 0.08
    # re = 0.2 * dx
    # well_diameter = 0.2 * np.float64(dx) # original
    # connection_factor = 1.0e8 (good)
    permeability = 100.0  # mD
    diameter = 4.0
    length = 8.0
    visc = [5.0, 1.0]
    M = min(1 / visc[0], 1 / visc[1])
    area = math.pi * (diameter**2) / 4.0
    # dx = length / num_grid_blocks
    TR = M * units_system.convert_transmissibility(permeability * (area / length))

    def write_wconinje_header(fout):
        # fout.writelines(['\n--wellname\tInjType\tOpenShutFlag\tSurfFlowRate'])
        fout.writelines(
            [
                "\n",
                *format_string(
                    [
                        "-- WELL",
                        "FLUID",
                        "OPEN/",
                        "CNTL",
                        "SURF",
                        "RESV",
                        "BHP",
                        "THP",
                        "VFP",
                    ]
                ),
                "\n",
                *format_string(
                    [
                        "-- NAME",
                        "TYPE",
                        "SHUT",
                        "MODE",
                        "RATE",
                        "RATE",
                        "PRSES",
                        "PRES",
                        "TABLE",
                    ]
                ),
            ]
        )

    def write_wconprod_header(fout):
        # fout.writelines(['\n--wellname\tpFlag\tControlMode\tQo\tQw\tQg\tQl\tQr\tBHP'])
        fout.writelines(
            [
                "\n",
                *format_string(
                    [
                        "-- WELL",
                        "OPEN",
                        "CNTL",
                        "OIL",
                        "WAT",
                        "GAS",
                        "LIQ",
                        "RES",
                        "BHP",
                        "THP",
                        "VFP",
                        "VFP",
                    ]
                ),
                "\n",
                *format_string(
                    [
                        "-- NAME",
                        "SHUT",
                        "MODE",
                        "RATE",
                        "RATE",
                        "RATE",
                        "RATE",
                        "RATE",
                        "PRES",
                        "PRES",
                        "TABLE",
                        "ALFQ",
                    ]
                ),
            ]
        )

    def write_wconprod_enty(
        fout,
        well_name,
        status,
        control,
        liquid_rate: float = None,
        oil_rate: float = None,
        water_rate: float = None,
        gas_rate: float = None,
        resv: float = None,
        bhp: float = None,
        thp: float = None,
        vfp_table: float = None,
        vfp_alfq: float = None,
    ):
        fout.writelines(
            [
                "\n",
                *format_string(
                    [
                        f"'{well_name}'",
                        f"'{status}'",
                        f"'{control}'",
                        format_value(oil_rate),
                        format_value(water_rate),
                        format_value(gas_rate),
                        format_value(liquid_rate),
                        format_value(resv),
                        format_value(bhp),
                        format_value(thp),
                        format_value(vfp_table),
                        format_value(vfp_alfq),
                    ]
                ),
                "\t/",
            ]
        )

    def write_wconinje_entry(
        fout,
        well_name,
        status,
        control,
        phase,
        rate: float = None,
        resv: float = None,
        bhp: float = None,
        thp: float = None,
        vfp_table: float = None,
    ):
        fout.writelines(
            [
                "\n",
                *format_string(
                    [
                        f"'{well_name}'",
                        f"'{phase}'",
                        f"'{status}'",
                        f"'{control}'",
                        format_value(rate),
                        format_value(resv),
                        format_value(bhp),
                        format_value(thp),
                        format_value(vfp_table),
                    ]
                ),
                "\t/",
            ]
        )

    filename = os.path.join(wdir, "include", project_name + "_WELLSCH")

    if experiment_name == "CENT":
        filename += str(stage) + ".INC"
    elif (experiment_name == "SS") or (experiment_name == "USS"):
        filename += ".INC"

    time_precision = int(4)
    num_timesteps = int(0)

    # Open file
    fout = open(filename, "w")

    current_time = np.float64(0.0)

    first_cell = 1
    last_cell = num_grid_blocks

    if grid_type in {
        "extended-core",
        "extended-core-refined",
        "centrifuge-core",
        "centrifuge-core-refined",
    }:
        last_cell += 2

    if experiment_name in {"SS", "USS"}:
        if stage == 0:
            current_time = np.float64(0.0)
        else:
            current_time = np.float64(simcontrol_data[stage][1])

        for i in range(0, len(simcontrol_data)):
            # t = time_data[i][0]
            # if( t != 0.0 ):
            #    fout.writelines(['\nTIME'])
            #    fout.writelines(['\n\t', str( t ),'\t/'])
            #    fout.writelines(['\n'])
            #    num_timesteps += 1

            qinj_total = np.float64(simcontrol_data[i][0][0])
            qinj_frac = [
                np.float64(simcontrol_data[i][0][1] / 100.0),
                np.float64(simcontrol_data[i][0][2] / 100.0),
            ]
            qinj = [qinj_total * frac for frac in qinj_frac]
            phase_idx = {phase: idx for idx, phase in enumerate(phases)}
            qinj_by_phase = {phase: qinj[idx] for idx, phase in enumerate(phases)}
            dp_max = qinj_total / TR + 10.0

            # @TODO: create universal approach
            # ECLIPSE:
            # if( qinj_wfrac >= qinj_ofrac ):
            #     fout.writelines(['\nWELSPECS'])
            #     fout.writelines(['\n--introduce the wells: prod and inj'])
            #     fout.writelines(['\n--wellname\tgroup\tI\tJ\tRefDepthForBHP\tPreferredPhase'])
            #     fout.writelines(['\n\t','\'INJ\'','\tG1\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'WATER\'','\t/'])
            #     fout.writelines(['\n\t','\'PROD\'','\tG1\t', str( last_cell ), '\t', str( 1 ),'\t1*\t','\'LIQ\'','\t/'])
            #     fout.writelines(['\n/\n'])
            #     fout.writelines(['\nWCONINJE'])
            #     fout.writelines(['\n--wellname\tInjType\tOpenShutFlag\tSurfFlowRate\t6 def. values\tQoFrac\tQwfrac'])
            #     fout.writelines(['\n\t','\'INJ\'','\t\'MULTI\'','\t\'OPEN\'','\t\'RATE\'','\t', str( qinj_total*qinj_wfrac ), '\t6*', '\t', str( qinj_ofrac ), '\t', str( qinj_wfrac ),'\t/'])
            #     fout.writelines(['\n/\n'])
            # else:
            #     fout.writelines(['\nWELSPECS'])
            #     fout.writelines(['\n--introduce the wells: prod and inj'])
            #     fout.writelines(['\n--wellname\tgroup\tI\tJ\tRefDepthForBHP\tPreferredPhase'])
            #     fout.writelines(['\n\t','\'INJ\'','\tG1\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'OIL\'','\t/'])
            #     fout.writelines(['\n\t','\'PROD\'','\tG1\t', str( last_cell ), '\t', str( 1 ),'\t1*\t','\'LIQ\'','\t/'])
            #     fout.writelines(['\n/\n'])
            #     fout.writelines(['\nWCONINJE'])
            #     fout.writelines(['\n--wellname\tInjType\tOpenShutFlag\tSurfFlowRate\t6 def. values\tQoFrac\tQwfrac'])
            #     fout.writelines(['\n\t','\'INJ\'','\t\'MULTI\'','\t\'OPEN\'','\t\'RATE\'','\t', str( qinj_total*qinj_ofrac ), '\t6*', '\t', str( qinj_ofrac ), '\t', str( qinj_wfrac ),'\t/'])
            #     fout.writelines(['\n/\n'])

            with_tuning = False
            # with_tuning = True
            # OPM:
            # fout.writelines(['\nWELSPECS'])
            # fout.writelines(['\n--introduce the wells: prod and inj'])
            # fout.writelines(['\n--wellname\tgroup\tI\tJ\tRefDepthForBHP\tPreferredPhase'])
            # fout.writelines(['\n\t','\'INJW\'','\tGINJ\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'WATER\'','\t/'])
            # fout.writelines(['\n\t','\'INJO\'','\tGINJ\t',str( first_cell ),'\t', str( 1 ), '\t1*\t','\'OIL\'','\t/'])
            # fout.writelines(['\n\t','\'PROD\'','\tGPROD\t', str( last_cell ), '\t', str( 1 ),'\t1*\t','\'LIQ\'','\t/'])
            # fout.writelines(['\n/\n'])

            # injectors
            inj_well_status = ["SHUT" if (frac == 0) else "OPEN" for frac in qinj_frac]
            fout.writelines(
                [
                    "\nWELOPEN",
                    *chain.from_iterable(
                        [
                            format_string([f"\n'{well_name}'", f"'{status}'", "/"])
                            for well_name, status in zip(
                                well_injectors, inj_well_status
                            )
                        ]
                    ),
                    *format_string([f"\n'{well_producer}'", f"'OPEN'", "/"]),
                    "\n/\n",
                ]
            )
            if "OPEN" in inj_well_status:
                fout.writelines(["\nWCONINJE"])
                write_wconinje_header(fout)
                for idx, (phase, well_name, status, inj_rate) in enumerate(
                    zip(phases, well_injectors, inj_well_status, qinj)
                ):
                    if status in {"OPEN"}:
                        write_wconinje_entry(
                            fout,
                            well_name=well_name,
                            status="OPEN",
                            control="RATE",
                            phase=phase,
                            rate=qinj[idx],
                            # bhp=wbhp_prod + dp_max,
                        )
                fout.writelines(["\n/\n"])

            # producer
            if flooding == "imbibition":
                preferred_prod_phase = oil_phase_name
            else:  # if flooding == "drainage":
                preferred_prod_phase = wat_phase_name
            fout.writelines(["\nWCONPROD"])
            write_wconprod_header(fout)
            write_wconprod_enty(
                fout,
                well_name=well_producer,
                status="OPEN",
                # control="LRAT",
                # control="ORAT",
                # control="WRAT",
                control="BHP",
                bhp=wbhp_prod,
                # liquid_rate=qinj_total,
                # oil_rate=qinj_by_phase.get(oil_phase_name, None),
                # water_rate=qinj_by_phase.get(wat_phase_name, None),
                # gas_rate=qinj_by_phase.get(gas_phase_name, None),
            )
            fout.writelines(["\n/\n"])

            fout.writelines(["\nNEXTSTEP"])
            fout.writelines(["\n\t", str(0.001 * timestep), "\t'YES'", "\n"])
            fout.writelines(["/\n"])

            if with_tuning:
                trglcv = np.float64(0.00001)
                xxxlcv = np.float64(0.0001)
                trgddp = np.float64(1.0)
                trgdds = np.float64(0.01)

                newtmn = math.floor(1)
                litmax = int(25)
                litmin = math.floor(1)

                # tsinit = np.float64( timestep )
                # tsmax  = np.float64( 5.0*timestep )
                # tsmin  = np.float64( 0.5*timestep )
                # tsmchp = np.float64( 0.5*timestep )
                # tsfmax = np.float64( 2.0 )
                # tsfmin = np.float64( 0.5 )

                # tsinit = np.float64( timestep )
                # tsmax  = np.float64( 2.0*timestep )
                # tsmin  = np.float64( 0.1*timestep )
                # tsmchp = np.float64( 0.1*timestep )
                # tsfmax = np.float64( 2.0 )
                # tsfmin = np.float64( 0.1 )

                tsinit = np.float64(0.1 * timestep)
                tsmax = np.float64(2.0 * timestep)
                tsmin = np.float64(0.001 * timestep)
                tsmchp = np.float64(0.01 * timestep)
                tsfmax = np.float64(2.0)
                tsfmin = np.float64(0.01)
                tsfcnv = np.float64(0.1)
                tfdiff = np.float64(1.25)

                new_line = "\n"
                if timestep <= 0.0:
                    new_line += "--"

                fout.writelines([new_line, "TUNING"])
                fout.writelines(["\n-- time step control"])
                fout.writelines(
                    [
                        "\n-- TSINIT(max init tstep)\tTSMAXZ(max tstep)\tTSMINZ(min tstep)\tTSMCHP( min chopable tstep)\tTSFMAX(max increase factor)\tTSFMIN(min cutback factor)"
                    ]
                )
                fout.writelines(
                    [
                        "\n-- default:TSINIT(1)\tTSMAXZ(365)\tTSMINZ(0.1)\tTSMCHP(0.15)\tTSFMAX(3.0)\tTSFMIN(0.3)"
                    ]
                )
                fout.writelines(
                    [
                        new_line,
                        "\t",
                        str(tsinit),
                        "\t",
                        str(tsmax),
                        "\t",
                        str(tsmin),
                        "\t",
                        str(tsmchp),
                        "\t",
                        str(tsfmax),
                        "\t",
                        str(tsfmin),
                        "\t/",
                    ]
                )
                fout.writelines(["\n-- convergence tolerance parameters"])
                fout.writelines([new_line, "\t/"])
                fout.writelines(["\n-- control of Newton and linear iterations"])
                fout.writelines(
                    ["\n-- newtnmx\tnewtmn\tlitmax\tlitmin\tmxwsit\tmxwpit"]
                )
                fout.writelines(
                    [
                        "\n-- default: newtnmx(12)\tnewtmn(1)\tlitmax(25)\tlitmin(1)\tmxwsit(8)\tmxwpit(8)"
                    ]
                )
                fout.writelines(
                    [
                        new_line,
                        "\t",
                        str(newtmx),
                        "\t",
                        str(newtmn),
                        "\t",
                        str(litmax),
                        "\t",
                        str(litmin),
                        "\t",
                        str(newtmx),
                        "\t",
                        str(newtmx),
                        "\t/\n",
                    ]
                )

                # fout.writelines([new_line,'TUNINGDP'])
                # fout.writelines(['\n-- solution change control'])
                # fout.writelines(['\n--Essentially, convergence is assumed when either the residual is small or the solution change is small'])
                # fout.writelines(['\n--TRGLCV(target linear convergence error)\tXXXLCV(maximum linear convergence error)\tTRGDDP(maximum pressure change during a Newton iteration)\tTRGDDS(maximum saturation change during a Newton iteration)'])
                # fout.writelines(['\n-- default:TRGLCV(0.00001)\tXXXLCV(365)\tTRGDDP(1.0)\tTRGDDS(0.01)'])
                # fout.writelines([new_line,'\t', str( trglcv ), '\t', str( xxxlcv ), '\t', str( trgddp ), '\t', str( trgdds ), '\t/\n'])

                if legacy_versions:
                    fout.writelines(["\nMESSOPTS"])
                    fout.writelines(["\n---reports forced timestep as message"])
                    fout.writelines(["\n\tACCPTIME\t1\t/\n"])

            # for j in range( 1, len( time_data[i] ) ):
            #    fout.writelines(['\nTIME'])
            #    fout.writelines(['\n\t', str( time_data[i][j] ),'\t/'])
            #    fout.writelines(['\n'])
            #    num_timesteps += 1

            t = np.float64(simcontrol_data[i][1])
            if (i == 0) and (t != 0.0):
                substeps = True if (current_time < t) else False
                while substeps:
                    substeps = True
                    new_time = np.float64(current_time + timestep)
                    round_time = np.float64(round(new_time, time_precision))
                    if (round_time < t) and (round_time > current_time):
                        current_time = np.float64(new_time)
                        fout.writelines(["\nTSTEP"])
                        fout.writelines(["\n\t", str(timestep), "\t/"])
                        fout.writelines(["\n"])
                        num_timesteps += int(1)
                    elif new_time < t:
                        current_time = np.float64(new_time)
                    else:
                        substeps = False

                if legacy_versions:
                    fout.writelines(["\nTIME"])
                    fout.writelines(["\n\t", str(simcontrol_data[i][1]), "\t/"])
                    fout.writelines(["\n"])

                num_timesteps += int(1)
                current_time = np.float64(t)

            for j in range(2, len(simcontrol_data[i])):
                t = np.float64(simcontrol_data[i][j])
                if t != 0.0:
                    substeps = True if (current_time < t) else False
                    while substeps:
                        substeps = True
                        new_time = np.float64(current_time + timestep)
                        round_time = np.float64(round(new_time, time_precision))
                        if (round_time < t) and (round_time > current_time):
                            current_time = np.float64(new_time)
                            fout.writelines(["\nTSTEP"])
                            fout.writelines(
                                [
                                    "\n\t",
                                    str(timestep),
                                    "\t/",
                                ]
                            )
                            fout.writelines(["\n"])
                            num_timesteps += int(1)
                        elif new_time < t:
                            current_time = np.float64(new_time)
                        else:
                            substeps = False

                    if legacy_versions:
                        fout.writelines(["\nTIME"])
                        fout.writelines(["\n\t", str(t), "\t/"])
                        fout.writelines(["\n"])
                    num_timesteps += int(1)
                    current_time = np.float64(t)

    elif (experiment_name == "CENT") and (
        grid_type not in {"centrifuge-core", "centrifuge-core-refined"}
    ):
        # if( stage != 0 ):

        #     last_entry = len( time_data[stage-1] ) - 1
        #     t = time_data[stage-1][last_entry]
        #     if( t != 0.0 ):

        #         fout.writelines(['\nTIME'])
        #         fout.writelines(['\n\t', str( t ),'\t/'])
        #         fout.writelines(['\n'])
        #         num_timesteps += 1

        # for i in range( 0, len( time_data[stage] ) ):

        #     t = time_data[stage][i]
        #     if( t != 0.0 ):

        #         fout.writelines(['\nTIME'])
        #         fout.writelines(['\n\t', str( t ),'\t/'])
        #         fout.writelines(['\n'])
        #         num_timesteps += 1

        if stage == 0:
            write_wconinje_header(fout)
            fout.writelines(["\nWCONINJE"])
            fout.writelines(
                [
                    "\n--wellname\tInjType\tOpenShutFlag\tSurfFlowRate\t6 def. values\tQoFrac\tQwfrac"
                ]
            )
            if flooding == "imbibition":
                preferred_inj_phase = wat_phase_name
            else:  # if flooding == "drainage":
                preferred_inj_phase = oil_phase_name
            fout.writelines(
                [
                    "\n\t",
                    f"'{well_injector}'",
                    f"\t'{preferred_inj_phase}'",
                    "\t'OPEN'",
                    "\t'BHP'",
                    "\t2*\t",
                    str(wbhp_inj),
                    "\t/",
                ]
            )
            fout.writelines(["\n/\n"])

            write_wconprod_header(fout)
            fout.writelines(["\nWCONPROD"])
            fout.writelines(
                ["\n--wellname\tpFlag\tControlMode\tQo\tQw\tQg\tQl\tQr\tBHP"]
            )
            fout.writelines(
                [
                    "\n\t",
                    f"'{well_producer}'",
                    "\t",
                    "'OPEN'",
                    "\t",
                    "'BHP'",
                    "\t",
                    "5*\t",
                    str(wbhp_prod),
                    "\t/",
                ]
            )
            fout.writelines(["\n/\n"])

            current_time = np.float64(0.0)
        else:
            current_time = np.float64(simcontrol_data[stage][1])

        num_controldata = len(simcontrol_data[stage])
        for i in range(1, num_controldata):
            t = simcontrol_data[stage][i]
            if t != 0.0:
                if detailed_results_output:
                    substeps = True if (current_time < t) else False
                    while substeps:
                        substeps = True
                        new_time = np.float64(current_time + timestep)
                        round_time = np.float64(round(new_time, time_precision))
                        if (round_time < t) and (round_time > current_time):
                            current_time = np.float64(new_time)
                            fout.writelines(["\nTSTEP"])
                            fout.writelines(["\n\t", str(timestep), "\t/"])
                            fout.writelines(["\n"])
                            num_timesteps += int(1)
                        elif new_time < t:
                            current_time = np.float64(new_time)
                        else:
                            substeps = False

                if legacy_versions:
                    fout.writelines(["\nTIME"])
                    fout.writelines(["\n\t", str(t), "\t/"])
                    fout.writelines(["\n"])
                num_timesteps += int(1)
                current_time = np.float64(t)

                if i != num_controldata - 1:
                    fout.writelines(["\nWCONINJE"])
                    fout.writelines(
                        [
                            "\n--wellname\tInjType\tOpenShutFlag\tSurfFlowRate\t6 def. values\tQoFrac\tQwfrac"
                        ]
                    )
                    if flooding == "imbibition":
                        preferred_inj_phase = wat_phase_name
                    else:  # if flooding == "drainage":
                        preferred_inj_phase = oil_phase_name
                    fout.writelines(
                        [
                            "\n\t",
                            f"'{well_injector}'",
                            f"\t'{preferred_inj_phase}'",
                            "\t'OPEN'",
                            "\t'BHP'",
                            "\t2*\t",
                            str(wbhp_inj),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\n/\n"])

                    fout.writelines(["\nWCONPROD"])
                    fout.writelines(
                        ["\n--wellname\tpFlag\tControlMode\tQo\tQw\tQg\tQl\tQr\tBHP"]
                    )
                    fout.writelines(
                        [
                            "\n\t",
                            f"'{well_producer}'",
                            "\t",
                            "'OPEN'",
                            "\t",
                            "'BHP'",
                            "\t",
                            "5*\t",
                            str(wbhp_prod),
                            "\t/",
                        ]
                    )
                    fout.writelines(["\n/\n"])

    elif (experiment_name == "CENT") and (
        grid_type in {"centrifuge-core", "centrifuge-core-refined"}
    ):
        trglcv = np.float64(0.00001)  # 0.00001
        xxxlcv = np.float64(0.0001)  # 0.0001
        trgddp = np.float64(0.001)  # 1.0
        trgdds = np.float64(0.01)  # 0.01

        # benchmark
        litmax = int(25)
        newtmn = math.floor(1)
        litmin = math.floor(1)

        # exercises
        # litmax = int( 25 )
        # newtmn = math.floor( 1 )
        # litmin = math.floor( 1 )

        timestep /= np.float64(1**stage)
        newtmx += stage * 0
        litmax += stage * 0
        # if(verbose):
        #     print( '\nstage = ', stage, ' tstep = ', timestep, ' newtmx = ', newtmx, ' litmax = ', litmax )

        # benchmark
        tsinit = np.float64(0.1 * timestep)
        tsmax = np.float64(2.0 * timestep)
        tsmin = np.float64(0.001 * timestep)
        tsmchp = np.float64(0.01 * timestep)
        tsfmax = np.float64(2.0)
        tsfmin = np.float64(0.01)
        tsfcnv = np.float64(0.1)
        tfdiff = np.float64(1.25)

        # # exercises
        # tsinit = np.float64( 0.1*timestep )
        # tsmax  = np.float64( 2.0*timestep )
        # tsmin  = np.float64( 0.001*timestep )
        # tsmchp = np.float64( 0.01*timestep )
        # tsfmax = np.float64( 2.0 )
        # tsfmin = np.float64( 0.01 )
        # tsfcnv = np.float64( 0.1 )
        # tfdiff = np.float64( 1.25 )

        new_line = "\n"
        if timestep <= 0.0:
            new_line += "--"

        fout.writelines([new_line, "TUNING"])
        fout.writelines(["\n-- time step control"])
        fout.writelines(
            [
                "\n-- TSINIT(max init tstep)\tTSMAXZ(max tstep)\tTSMINZ(min tstep)\tTSMCHP( min chopable tstep)\tTSFMAX(max increase factor)\tTSFMIN(min cutback factor)\tTSFCNV( cut factor after convergence failure )\tTFDIFF( max. increase factor after a convergence failure )"
            ]
        )
        fout.writelines(
            [
                "\n-- default:TSINIT(1)\tTSMAXZ(365)\tTSMINZ(0.1)\tTSMCHP(0.15)\tTSFMAX(3.0)\tTSFMIN(0.3)\tTSFCNV(0.1)\tTFDIFF(1.25)"
            ]
        )
        fout.writelines(
            [
                new_line,
                "\t",
                str(tsinit),
                "\t",
                str(tsmax),
                "\t",
                str(tsmin),
                "\t",
                str(tsmchp),
                "\t",
                str(tsfmax),
                "\t",
                str(tsfmin),
                "\t/",
            ]
        )  # ,'\t', str( tsfcnv ), '\t', str( tfdiff ), '\t/'])
        fout.writelines(["\n-- convergence tolerance parameters"])
        fout.writelines([new_line, "\t/"])
        fout.writelines(["\n-- control of Newton and linear iterations"])
        fout.writelines(["\n-- default: newtnmx(12)\tnewtmn(1)\tlitmax(25)\tlitmin(1)"])
        fout.writelines(
            [
                new_line,
                "\t",
                str(newtmx),
                "\t",
                str(newtmn),
                "\t",
                str(litmax),
                "\t",
                str(litmin),
                "\t/\n",
            ]
        )

        # fout.writelines([new_line,'TUNINGDP'])
        # fout.writelines(['\n-- solution change control'])
        # fout.writelines(['\n--Essentially, convergence is assumed when either the residual is small or the solution change is small'])
        # fout.writelines(['\n--TRGLCV(target linear convergence error)\tXXXLCV(maximum linear convergence error)\tTRGDDP(maximum pressure change during a Newton iteration)\tTRGDDS(maximum saturation change during a Newton iteration)'])
        # fout.writelines(['\n-- default:TRGLCV(0.00001)\tXXXLCV(365)\tTRGDDP(1.0)\tTRGDDS(0.01)'])
        # fout.writelines([new_line,'\t', str( trglcv ), '\t', str( xxxlcv ), '\t', str( trgddp ), '\t', str( trgdds ), '\t/\n'])

        if legacy_versions:
            fout.writelines(["\nMESSOPTS"])
            fout.writelines(["\n---reports forced timestep as message"])
            fout.writelines(["\n\tACCPTIME\t1\t/\n"])

        if stage == 0:
            current_time = np.float64(0.0)
        else:
            current_time = np.float64(simcontrol_data[stage][1])
        num_controldata = len(simcontrol_data[stage])
        for i in range(1, num_controldata):
            t = np.float64(simcontrol_data[stage][i])
            if i == 2:
                fout.writelines([new_line, "TUNING"])
                fout.writelines(["\n-- time step control"])
                fout.writelines(
                    [
                        "\n-- TSINIT(max init tstep)\tTSMAXZ(max tstep)\tTSMINZ(min tstep)\tTSMCHP( min chopable tstep)\tTSFMAX(max increase factor)\tTSFMIN(min cutback factor)\tTSFCNV( cut factor after convergence failure )\tTFDIFF( max. increase factor after a convergence failure )"
                    ]
                )
                fout.writelines(
                    [
                        "\n-- default:TSINIT(1)\tTSMAXZ(365)\tTSMINZ(0.1)\tTSMCHP(0.15)\tTSFMAX(3.0)\tTSFMIN(0.3)\tTSFCNV(0.1)\tTFDIFF(1.25)"
                    ]
                )
                fout.writelines(
                    [
                        new_line,
                        "\t",
                        str(tsinit),
                        "\t",
                        str(tsmax),
                        "\t",
                        str(tsmin),
                        "\t",
                        str(tsmchp),
                        "\t",
                        str(tsfmax),
                        "\t",
                        str(tsfmin),
                        "\t/",
                    ]
                )  # ,'\t', str( tsfcnv ), '\t', str( tfdiff ), '\t/'])
                fout.writelines(["\n-- convergence tolerance parameters"])
                fout.writelines([new_line, "\t/"])
                fout.writelines(["\n-- control of Newton and linear iterations"])
                fout.writelines(
                    ["\n-- default: newtnmx(12)\tnewtmn(1)\tlitmax(25)\tlitmin(1)"]
                )
                fout.writelines(
                    [
                        new_line,
                        "\t",
                        str(newtmx),
                        "\t",
                        str(newtmn),
                        "\t",
                        str(litmax),
                        "\t",
                        str(litmin),
                        "\t/\n",
                    ]
                )

                # fout.writelines([new_line,'TUNINGDP'])
                # fout.writelines(['\n-- solution change control'])
                # fout.writelines(['\n--Essentially, convergence is assumed when either the residual is small or the solution change is small'])
                # fout.writelines(['\n--TRGLCV(target linear convergence error)\tXXXLCV(maximum linear convergence error)\tTRGDDP(maximum pressure change during a Newton iteration)\tTRGDDS(maximum saturation change during a Newton iteration)'])
                # fout.writelines(['\n-- default:TRGLCV(0.00001)\tXXXLCV(365)\tTRGDDP(1.0)\tTRGDDS(0.01)'])
                # fout.writelines([new_line,'\t', str( trglcv ), '\t', str( xxxlcv ), '\t', str( trgddp ), '\t', str( trgdds ), '\t/\n'])

                if legacy_versions:
                    fout.writelines(["\nMESSOPTS"])
                    fout.writelines(["\n---reports forced timestep as message"])
                    fout.writelines(["\n\tACCPTIME\t1\t/\n"])

            if t != 0.0:
                if detailed_results_output:
                    substeps = True if (current_time < t) else False
                    while substeps:
                        substeps = True
                        new_time = np.float64(current_time + timestep)
                        round_time = np.float64(round(new_time, time_precision))
                        if (round_time < t) and (round_time > current_time):
                            current_time = np.float64(new_time)
                            fout.writelines(["\nTSTEP"])
                            fout.writelines(["\n\t", str(timestep), "\t/"])
                            fout.writelines(["\n"])
                            num_timesteps += int(1)
                        elif new_time < t:
                            current_time = np.float64(new_time)
                        else:
                            substeps = False

                if legacy_versions:
                    fout.writelines(["\nTIME"])
                    fout.writelines(["\n\t", str(t), "\t/"])
                    fout.writelines(["\n"])
                num_timesteps += int(1)
                current_time = np.float64(t)

    # close file
    fout.close()

    return num_timesteps
