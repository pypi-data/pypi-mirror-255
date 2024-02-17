import os
from enum import auto
import numpy as np
import scipy as sp
import math
import time

# import subprocess
# import datetime

from typing import Any, List, Dict

from coreflow.io import table_data, math_tools
from coreflow.io.plotting import Plot as plt
from coreflow.utils import os_utils
from coreflow import sat_funcs
from coreflow.simulators import deck

simulation_index = int(-1)

# centrifuge3D = True
centrifuge3D = False

# centrifugeRefined = True
centrifugeRefined = False

# option needed only for centrifuge experiment
# sameGrav = True
sameGrav = False


# Utils
class Utils:
    @staticmethod
    def get_class_properties(cls: Any) -> List:
        method_list = []
        for attribute in dir(cls):
            attribute_value = getattr(cls, attribute)
            if (
                not attribute.startswith("__")
                and hasattr(attribute_value, "__class__")
                and hasattr(attribute_value.__class__, "__name__")
                and attribute_value.__class__.__name__ == "property"
            ):
                method_list.append(attribute)
        return method_list

    @staticmethod
    def get_class_methods(cls: Any) -> List:
        method_list = []
        for attribute in dir(cls):
            attribute_value = getattr(cls, attribute)
            if (
                not attribute.startswith("__")
                and hasattr(attribute_value, "__class__")
                and hasattr(attribute_value.__class__, "__name__")
                and attribute_value.__class__.__name__ == "function"
            ):
                method_list.append(attribute)
        return method_list

    @staticmethod
    def get_class_members(cls: Any) -> List:
        method_list = []
        for attribute in dir(cls):
            attribute_value = getattr(cls, attribute)
            if (
                not attribute.startswith("__")
                and not callable(attribute_value)
                and hasattr(attribute_value.__class__, "__name__")
                and not attribute_value.__class__.__name__ == "property"
            ):
                method_list.append(attribute)
        return method_list


class Measurement:
    Pressure = auto()
    Acceleration = auto()


class UnitsConverter:
    # convert between bar and atm
    bar2atm = np.float64(1.0e5 / 101325.0)
    atm2bar = np.float64(101325.0 / 1.0e5)
    # convert between m/s/s and cm2*atm/gm
    cm2atmpergm = np.float64(10.0 / 101325.0)

    @staticmethod
    def convert(
        x, measurement: Measurement, src: str = "", dst: str = "", **kwargs
    ) -> float:
        if isinstance(src, str) and isinstance(dst, str):
            if measurement == Measurement.Pressure:
                return UnitsConverter.convert_pressure(x, src=src, dst=dst, **kwargs)
            elif measurement == Measurement.Acceleration:
                return UnitsConverter.convert_pressure(x, src=src, dst=dst, **kwargs)
        return x

    @staticmethod
    def convert_pressure(x, src: str = "", dst: str = "", **kwargs):
        if UnitsConverter.from_metric_to_lab(src, dst):
            return UnitsConverter.bar2atm * x
        elif UnitsConverter.from_lab_to_metric(src, dst):
            return UnitsConverter.atm2bar * x
        return x

    @staticmethod
    def convert_acceleration(x, src: str = "", dst: str = "", **kwargs):
        if UnitsConverter.from_metric_to_lab(src, dst):
            return UnitsConverter.cm2atmpergm * x
        elif UnitsConverter.from_lab_to_metric(src, dst):
            return x / UnitsConverter.cm2atmpergm
        return x

    @staticmethod
    def from_metric_to_lab(src: str, dst: str, **kwargs) -> bool:
        from_name = src.lower().strip()
        to_name = dst.lower().strip()
        return from_name == "metric" and to_name == "lab"

    @staticmethod
    def from_lab_to_metric(src: str, dst: str, **kwargs) -> bool:
        from_name = src.lower().strip()
        to_name = dst.lower().strip()
        return from_name == "lab" and to_name == "metric"


# files
class ProjectSetup:
    @property
    def ProjectName(self) -> str:
        return self.__project_name

    @property
    def ExperimentName(self) -> str:
        return self.__experiment_name

    @property
    def FloodingType(self) -> str:
        return self.__flooding

    @property
    def BaseDirectory(self) -> str:
        return self.__base_dir

    @property
    def SourceDirectory(self) -> str:
        return self.__source_dir

    @property
    def ProjectDirectoryName(self) -> str:
        return self.__project_dirname

    @property
    def SimulationDirectoryName(self) -> str:
        return self.__sim_dirname

    @property
    def ProjectDirectory(self) -> str:
        return self.__project_dir

    @property
    def SimulationDirectory(self) -> str:
        return self.__sim_dir

    @property
    def ProjectIncludeDirectory(self) -> str:
        return self.__include_dir

    @property
    def ObservedDatafile(self) -> str:
        return self.__obs_datafile

    @property
    def ObservedPlotfile(self) -> str:
        return self.__obs_plotfile

    @property
    def ObservedGraffile(self) -> str:
        return self.__obs_graffile

    @property
    def SimulationControlDatafile(self) -> str:
        return self.__simcontrol_datafile

    @property
    def SimulationControlPlotfile(self) -> str:
        return self.__simcontrol_plotfile

    @property
    def RockFluidDatafile(self) -> str:
        return self.__rock_and_fluid_datafile

    @property
    def Kr(self) -> str:
        return self.__kr

    @property
    def Pc(self) -> str:
        return self.__pc

    @property
    def ReferenceKr(self) -> str:
        return self.__ref_kr

    @property
    def ReferencePc(self) -> str:
        return self.__ref_pc

    @property
    def PressInit(self) -> str:
        return self.__pressure_init

    @property
    def DurationTime(self) -> str:
        return self.__duration_time

    @property
    def TimeData(self) -> str:
        return self.__time_data

    @property
    def SimulationControlData(self) -> str:
        return self.__simcontrol_data

    @property
    def SimulationControlDataVector(self) -> List:
        return self.__simcontrol_data_vec

    @property
    def ReferenceData(self) -> str:
        return self.__ref_data

    @property
    def ReferenceDataVector(self) -> str:
        return self.__ref_data_vec

    @property
    def NumObservationColumns(self) -> int:
        return self.__num_obs_cols

    # @property
    # def (self) -> str:
    #     return self.__
    # @.setter
    # def (self, value: str) -> None:
    #     self.__ = value

    def __init__(
        self,
        experiment_name: str = "",
        flooding: str = "",
        basedir: str = "",
        rootsdir: str = "",
        project_name: str = "",
        obs_datafile_prefix: str = "",
        simcontrol_datafile_prefix: str = "",
        rock_and_fluid_datafile: str = "",
        relperms: str = "",
        cappress: str = "",
        analyt_relperms: str = "",
        analyt_cappress: str = "",
        pressure_init: float = None,
        duration_time: float = None,
        verbose: bool = False,
        **kwargs,
    ):
        # experiment name
        self.__experiment_name = experiment_name
        # flooding type
        self.__flooding = flooding

        # observed data files
        # SS, USS: pressure difference vs. time
        # CENT: oil/water production vs. time
        self.__obs_datafile = obs_datafile_prefix + ".txt"
        self.__obs_plotfile = obs_datafile_prefix + ".png"
        self.__obs_graffile = obs_datafile_prefix + ".graf"

        # simulation control file
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        self.__simcontrol_datafile = simcontrol_datafile_prefix + ".txt"
        self.__simcontrol_plotfile = simcontrol_datafile_prefix + ".png"
        # rock and fluid data
        self.__rock_and_fluid_datafile = rock_and_fluid_datafile

        # project name
        self.__project_name = project_name
        self.__project_dirname = project_name + "_PROJECT"
        self.__sim_dirname = project_name + "_SIMULATIONS"

        # directories
        self.__base_dir = basedir
        self.__source_dir = rootsdir
        self.__project_dir = os.path.join(basedir, self.__project_dirname)
        self.__include_dir = os.path.join(self.__project_dir, "include")
        self.__sim_dir = os.path.join(basedir, self.__sim_dirname)

        # saturation functions
        self.__kr = relperms
        self.__pc = cappress
        self.__ref_kr = analyt_relperms
        self.__ref_pc = analyt_cappress

        # initial pressure
        self.__pressure_init = pressure_init
        self.__duration_time = duration_time

        # create project directories
        self.create_project_directories(verbose=verbose, **kwargs)

        # read simulator control and observed data
        self.read_simulation_control_and_observed_data(verbose=verbose, **kwargs)

    # create project directories
    def create_project_directories(self, verbose: bool = False, **kwargs):
        # create project directories
        os_utils.make_dir(self.__project_dir)
        os_utils.make_dir(self.__include_dir)
        os_utils.make_dir(self.__source_dir)
        os_utils.make_dir(self.__sim_dir)

    # read simulation control and observed data
    def read_simulation_control_and_observed_data(
        self, verbose: bool = False, **kwargs
    ):
        # reference data
        # SS, USS: pressure difference vs. time
        # CENT: oil/water production vs. time
        # simulator control data
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        simcontrol_datafile = self.SimulationControlDatafile
        obs_datafile = self.ObservedDatafile
        duration_time = self.DurationTime
        (
            self.__time_data,
            self.__simcontrol_data_vec,
            self.__simcontrol_data,
            self.__ref_data_vec,
            self.__ref_data,
        ) = table_data.load_control_and_observed_data(
            simcontrol_datafile, obs_datafile, duration_time, verbose
        )

        if self.__experiment_name in {"SS", "USS"}:
            pass
            # simcontrol_data_array = np.asarray( self.__simcontrol_data_vec.copy() )
            # t    = simcontrol_data_array[:,0]
            # qtot = simcontrol_data_array[:,1]
            # qo   = simcontrol_data_array[:,2]
            # qw   = simcontrol_data_array[:,3]
            # for i in range( 0, len( qtot ) ):
            #     qo[i] *= np.float64( qtot[i]/100. )
            #     qw[i] *= np.float64( qtot[i]/100. )
        elif self.__experiment_name == "CENT":
            # simcontrol_data_array = np.asarray( self.__simcontrol_data_vec.copy() )
            # t        = simcontrol_data_array[:,0]
            # acc      = simcontrol_data_array[:,1]
            # convert from m/s/s to cm2*atm/gm
            for i in range(0, len(self.__simcontrol_data)):
                self.__simcontrol_data[i][0][0] *= (
                    self.__distance_to_inlet / self.__radius_centre
                )
                self.__simcontrol_data[i][0][0] *= UnitsConverter.cm2atmpergm
                self.__simcontrol_data[i][0][0] = round(
                    self.__simcontrol_data[i][0][0], 6
                )
        # number of observation columns
        self.__num_obs_cols = len(self.__ref_data_vec[0]) - 2


# fluid phase properties: 'oil', 'water', 'gas'
class FluidPhase:
    @property
    def Density(self) -> float:
        return self.__density

    @Density.setter
    def Density(self, value: float) -> None:
        self.__density = value

    @property
    def Viscosity(self) -> str:
        return self.__viscosity

    @Viscosity.setter
    def Viscosity(self, value: float) -> None:
        self.__viscosity = value

    @property
    def Viscosibility(self) -> float:
        return self.__viscosibility

    @Viscosibility.setter
    def Viscosibility(self, value: float) -> None:
        self.__viscosibility = value

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, viscosity: float, verbose: bool = False, **kwargs):
        self.Viscosity = viscosity


# rock properties
class Rock:
    @property
    def Permeability(self) -> str:
        return self.__permeability

    @Permeability.setter
    def Permeability(self, value: float) -> None:
        self.__permeability = value

    @property
    def Porosity(self) -> str:
        return self.__porosity

    @Porosity.setter
    def Porosity(self, value: float) -> None:
        self.__porosity = value

    @property
    def PoreVolume(self) -> str:
        return self.__porevolume

    @PoreVolume.setter
    def PoreVolume(self, value: float) -> None:
        self.__porevolume = value

    @property
    def Compressibility(self) -> float:
        return self.__compressibility

    @Compressibility.setter
    def Compressibility(self, value: float) -> None:
        self.__compressibility = value

    @property
    def Ooip(self) -> float:
        return self.__ooip

    @Ooip.setter
    def Ooip(self, value: float) -> None:
        self.__ooip = value

    @property
    def Owip(self) -> float:
        return self.__owip

    @Owip.setter
    def Owip(self, value: float) -> None:
        self.__owip = value

    @property
    def Ogip(self) -> float:
        return self.__ogip

    @Ogip.setter
    def Ogip(self, value: float) -> None:
        self.__ogip = value

    @property
    def SwatInit(self) -> float:
        return self.__sw_init

    @SwatInit.setter
    def SwatInit(self, value: float) -> None:
        self.__sw_init = value

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(
        self, porosity: float, permeability: float, verbose: bool = False, **kwargs
    ):
        self.Porosity = porosity
        self.Permeability = permeability


# scal model: fluid and rock data
class ScalModel:
    @property
    def Oil(self) -> FluidPhase:
        return self.__oil

    @Oil.setter
    def Oil(self, value: FluidPhase) -> None:
        self.__oil = value

    @property
    def Water(self) -> FluidPhase:
        return self.__water

    @Water.setter
    def Water(self, value: FluidPhase) -> None:
        self.__water = value

    @property
    def Gas(self) -> FluidPhase:
        return self.__gas

    @Gas.setter
    def Gas(self, value: FluidPhase) -> None:
        self.__gas = value

    @property
    def RockData(self) -> Rock:
        return self.__rock

    @RockData.setter
    def RockData(self, value: Rock) -> None:
        self.__rock = value

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(
        self,
        visc_oil: float = None,
        visc_water: float = None,
        visc_gas: float = None,
        porosity: float = None,
        permeability: float = None,
        verbose: bool = False,
        **kwargs,
    ):
        # oil properties
        self.Oil = FluidPhase(viscosity=visc_oil, **kwargs)
        # water properties
        self.Water = FluidPhase(viscosity=visc_water, **kwargs)
        # gas properties
        self.Gas = FluidPhase(viscosity=visc_gas, **kwargs)
        # rock
        self.RockData = Rock(porosity=porosity, permeability=permeability, **kwargs)


# core sample data
class CoreSample:
    @property
    def Length(self) -> float:
        return self.__length

    @Length.setter
    def Length(self, value: float) -> None:
        self.__length = value

    @property
    def Width(self) -> float:
        return self.__width

    @Width.setter
    def Width(self, value: float) -> None:
        self.__width = value

    @property
    def Area(self) -> float:
        return self.__area

    @Area.setter
    def Area(self, value: float) -> None:
        self.__area = value

    @property
    def Volume(self) -> float:
        return self.__volume

    @Volume.setter
    def Volume(self, value: float) -> None:
        self.__volume = value

    @property
    def DistanceToInlet(self) -> float:
        return self.__distance_to_inlet

    @DistanceToInlet.setter
    def DistanceToInlet(self, value: float) -> None:
        self.__distance_to_inlet = value

    @property
    def DistanceToOutlet(self) -> float:
        return self.__distance_to_outlet

    @DistanceToOutlet.setter
    def DistanceToOutlet(self, value: float) -> None:
        self.__distance_to_outlet = value

    @property
    def Diameter(self) -> float:
        return self.__diameter

    @Diameter.setter
    def Diameter(self, value: float) -> None:
        self.__diameter = value

    @property
    def RadiusCentre(self) -> float:
        return self.__radius_centre

    @RadiusCentre.setter
    def RadiusCentre(self, value: float) -> None:
        self.__radius_centre = value

    @property
    def Depth(self) -> float:
        return self.__depth

    @Depth.setter
    def Depth(self, value: float) -> None:
        self.__depth = value

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, **kwargs):
        pass


# grid
class Grid:
    @property
    def Type(self) -> str:
        return self.__grid_type

    @Type.setter
    def Type(self, value: float) -> None:
        self.__grid_type = value

    @property
    def NumGridBlocks(self) -> int:
        return self.__num_grid_blocks

    @NumGridBlocks.setter
    def NumGridBlocks(self, value: int) -> None:
        self.__num_grid_blocks = value

    @property
    def NumCells(self) -> int:
        return self.__num_cells

    @NumCells.setter
    def NumCells(self, value: int) -> None:
        self.__num_cells = value

    @property
    def RefinedCells(self) -> int:
        return self.__num_refined_cells

    @RefinedCells.setter
    def RefinedCells(self, value: int) -> None:
        self.__num_refined_cells = value

    @property
    def FirstCells(self) -> int:
        return self.__num_first_cells

    @FirstCells.setter
    def FirstCells(self, value: int) -> None:
        self.__num_first_cells = value

    @property
    def LastCells(self) -> int:
        return self.__num_last_cells

    @LastCells.setter
    def LastCells(self, value: int) -> None:
        self.__num_last_cells = value

    @property
    def Dl(self) -> float:
        return self.__dl

    @Dl.setter
    def Dl(self, value: float) -> None:
        self.__dl = value

    @property
    def Dr(self) -> float:
        return self.__dr

    @Dr.setter
    def Dr(self, value: float) -> None:
        self.__dr = value

    @property
    def GravityMultiplier(self) -> float:
        return self.__gravity_multiplier

    @GravityMultiplier.setter
    def GravityMultiplier(self, value: float) -> None:
        self.__gravity_multiplier = value

    @property
    def CoreRegionId(self) -> int:
        return self.__core_region_id

    @CoreRegionId.setter
    def CoreRegionId(self, value: int) -> None:
        self.__core_region_id = value

    @property
    def OutcoreRegionId(self) -> int:
        return self.__outcore_region_id

    @OutcoreRegionId.setter
    def OutcoreRegionId(self, value: int) -> None:
        self.__outcore_region_id = value

    @property
    def NumGridCells(self) -> int:
        return self.__num_grid_cells

    @NumGridCells.setter
    def NumGridCells(self, value: int) -> None:
        self.__num_grid_cells = value

    @property
    def Nx(self) -> int:
        return self.__nx

    @Nx.setter
    def Nx(self, value: int) -> None:
        self.__nx = value

    @property
    def Ny(self) -> int:
        return self.__ny

    @Ny.setter
    def Ny(self, value: int) -> None:
        self.__ny = value

    @property
    def Nz(self) -> int:
        return self.__nz

    @Nz.setter
    def Nz(self, value: int) -> None:
        self.__nz = value

    @property
    def Dx(self) -> float:
        return self.__dx

    @Dx.setter
    def Dx(self, value: float) -> None:
        self.__dx = value

    @property
    def Dy(self) -> float:
        return self.__dy

    @Dy.setter
    def Dy(self, value: float) -> None:
        self.__dy = value

    @property
    def Dz(self) -> float:
        return self.__dz

    @Dz.setter
    def Dz(self, value: float) -> None:
        self.__dz = value

    @property
    def DxC(self) -> List[float]:
        return self.__dxc

    @DxC.setter
    def DxC(self, value: List[float]) -> None:
        self.__dxc = value

    @property
    def Pxyz(self) -> List[Any]:
        return self.__pxyz

    @Pxyz.setter
    def Pxyz(self, value: List[Any]) -> None:
        self.__pxyz = value

    @property
    def CellPoints(self) -> List[Any]:
        return self.__cell_points

    @CellPoints.setter
    def CellPoints(self, value: List[Any]) -> None:
        self.__cell_points = value

    @property
    def Cells(self) -> List[Any]:
        return self.__cells

    @Cells.setter
    def Cells(self, value: List[Any]) -> None:
        self.__cells = value

    @property
    def CoreCells(self) -> List[Any]:
        return self.__core_cells

    @CoreCells.setter
    def CoreCells(self, value: List[Any]) -> None:
        self.__core_cells = value

    @property
    def OutsideCells(self) -> List[Any]:
        return self.__outside_cells

    @OutsideCells.setter
    def OutsideCells(self, value: List[Any]) -> None:
        self.__outside_cells = value

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(
        self,
        grid_type: str = "",
        num_grid_blocks: int = 0,
        verbose: bool = False,
        **kwargs,
    ):
        # grid type
        self.__grid_type = grid_type
        # cells
        self.__num_grid_blocks = num_grid_blocks


# summary keyword
class SummaryKeywords:
    # special keyword values
    non_wellname = ":+:+:+:+"
    field_wellname = "FIELD"
    time_num = int(-32767)
    interregion_num = int(393217)

    @property
    def Keyword(self) -> List[int]:
        return self.__keyword

    @property
    def Type(self) -> List[str]:
        return self.__type

    @property
    def Wgname(self) -> List[str]:
        return self.__wgname

    @property
    def Num(self) -> List[int]:
        return self.__num

    @property
    def UnitConversionFactor(self) -> List[float]:
        return self.__unit_mult

    @property
    def Unit(self) -> List[str]:
        return self.__unit

    @property
    def WgnamesLen(self) -> int:
        return self.__num_wgnames

    @property
    def NumsLen(self) -> int:
        return self.__num_nums

    def __init__(self, verbose: bool = False, **kwargs):
        self.__keyword = []
        self.__type = []
        self.__wgname = []
        self.__num = []
        self.__unit_mult = []
        self.__unit = []
        self.__num_wgnames = 0
        self.__num_nums = 0

    # add keyword
    def add_keyword(
        self,
        kw: str,
        kw_type: str,
        kw_wgname: str,
        kw_num: int,
        unit: str = "",
        unit_mult: float = 1.0,
        **kwargs,
    ):
        """
        Add summary keywords to be read

        kw : str
            Keyword name
        kw_type : str
            Keyword type
        kw_wgname : str
            Well or Group name
        kw_num : int
            Region number
        unit : float
            Units
        unit_mult : float
            Units conversion factor
        """
        self.__keyword.append(kw)
        self.__type.append(kw_type)
        self.__wgname.append(kw_wgname)
        self.__num.append(kw_num)
        self.__unit.append(unit)
        self.__unit_mult.append(unit_mult)
        # 'WGNAMES', 'NUMS'
        if kw_type == "WGNAMES":
            self.__num_wgnames += 1
        elif kw_type == "NUMS":
            self.__num_nums += 1

    # add 'Well' or 'Group' keyword
    def add_well_or_group_keyword(
        self, kw: str, kw_wgname: str, unit: str = "", unit_mult: float = 1.0, **kwargs
    ):
        """
        Add well or group summary keywords to be read

        kw : str
            Keyword name
        kw_wgname : str
            Well or Group name
        unit : float
            Units
        unit_mult : float
            Units conversion factor
        """
        # summary keyword specs
        return self.add_keyword(
            kw, "WGNAMES", kw_wgname, 0, unit=unit, unit_mult=unit_mult, **kwargs
        )

    # add 'Region' or 'Block' keyword
    def add_region_or_block_keyword(
        self, kw: str, kw_num: int, unit: str = "", unit_mult: float = 1.0, **kwargs
    ):
        """
        Add region summary keywords to be read

        kw : str
            Keyword name
        kw_num : int
            Region number
        unit : float
            Units
        unit_mult : float
            Units conversion factor
        """
        # summary keyword specs
        non_wellname = SummaryKeywords.non_wellname
        return self.add_keyword(
            kw, "NUMS", non_wellname, kw_num, unit=unit, unit_mult=unit_mult, **kwargs
        )

    # add 'Field' keyword
    def add_field_keyword(
        self, kw: str, unit: str = "", unit_mult: float = 1.0, **kwargs
    ):
        """
        Add region summary keywords to be read

        kw : str
            Keyword name
        unit : float
            Units
        unit_mult : float
            Units conversion factor
        """
        # summary keyword specs
        non_wellname = SummaryKeywords.non_wellname
        return self.add_keyword(
            kw, "WGNAMES", non_wellname, 0, unit=unit, unit_mult=unit_mult, **kwargs
        )


# objective function
class ObjectiveFunction:
    # observations
    Qprod = "Qprod"
    Savg = "Savg"
    Pin = "Pin"
    Pout = "Pout"
    Fip = "Fip"
    Dp = "Dp"
    Qo = "Qo"
    Qw = "Qw"
    Qg = "Qg"
    Io = "Io"
    Iw = "Iw"
    Ig = "Ig"
    So = "So"
    Sw = "Sw"
    Sg = "Sg"
    Wip = "Wip"
    Oip = "Oip"
    Gip = "Qip"
    Time = "Time"

    @property
    def Name(self) -> List[str]:
        return self.__name

    @property
    def Weight(self) -> List[float]:
        return self.__weight

    @property
    def ReferenceId(self) -> List[int]:
        return self.__ref_id

    @property
    def ObservationIds(self) -> Dict[str, int]:
        return self.__obsrv_ids

    @ObservationIds.setter
    def ObservationIds(self, value: Dict[str, int]) -> None:
        self.__obsrv_ids = value

    @property
    def ObservationWeights(self) -> Dict[str, float]:
        return self.__obsrv_weights

    @ObservationWeights.setter
    def ObservationWeights(self, value: Dict[str, float]) -> None:
        self.__obsrv_weights = value

    def __init__(self, verbose: bool = False, **kwargs):
        self.__name = []
        self.__weight = []
        self.__ref_id = []
        # observation weights
        self.__obsrv_weights = {
            ObjectiveFunction.Dp: 100.0,
            ObjectiveFunction.Qprod: 25.0,
            ObjectiveFunction.Savg: 10000.0,
            ObjectiveFunction.Fip: 10000.0,
            ObjectiveFunction.Pin: 1.0,
            ObjectiveFunction.Pout: 1.0,
            ObjectiveFunction.Qw: 25.0,
            ObjectiveFunction.Qo: 25.0,
            ObjectiveFunction.Qg: 25.0,
            ObjectiveFunction.Iw: 1.0,
            ObjectiveFunction.Io: 1.0,
            ObjectiveFunction.Ig: 1.0,
            ObjectiveFunction.Sw: 1000.0,
            ObjectiveFunction.So: 1000.0,
            ObjectiveFunction.Sg: 1000.0,
            ObjectiveFunction.Wip: 1000.0,
            ObjectiveFunction.Oip: 1000.0,
            ObjectiveFunction.Gip: 1000.0,
            ObjectiveFunction.Time: 1.0,
        }
        # observation ids
        self.__obsrv_ids = {k: -1 for k in self.__obsrv_weights.keys()}

    # add observation
    def add_observation(
        self, name: str, weight: float = 1.0, ref_id: int = -1, **kwargs
    ):
        """
        Add observation specs

        name : str
            Name
        weight : float
            Observation weight
        ref_id : int
            Observation id in corresponsing table
        """
        self.__name.append(name)
        self.__weight.append(weight)
        self.__ref_id.append(ref_id)


# simulation output
class SimulationOutput:
    @property
    def ProductionData(self) -> SummaryKeywords:
        return self.__prod_data

    @ProductionData.setter
    def ProductionData(self, value: SummaryKeywords) -> None:
        self.__prod_data = value

    @property
    def SaturationProfile(self) -> SummaryKeywords:
        return self.__satprof_data

    @SaturationProfile.setter
    def SaturationProfile(self, value: SummaryKeywords) -> None:
        self.__satprof_data = value

    @property
    def Sw(self) -> SummaryKeywords:
        return self.__sw

    @Sw.setter
    def Sw(self, value: SummaryKeywords) -> None:
        self.__sw = value

    @property
    def So(self) -> SummaryKeywords:
        return self.__so

    @So.setter
    def So(self, value: SummaryKeywords) -> None:
        self.__so = value

    @property
    def Sg(self) -> SummaryKeywords:
        return self.__sg

    @Sg.setter
    def Sg(self, value: SummaryKeywords) -> None:
        self.__sg = value

    @property
    def Pw(self) -> SummaryKeywords:
        return self.__pw

    @Pw.setter
    def Pw(self, value: SummaryKeywords) -> None:
        self.__pw = value

    @property
    def Po(self) -> SummaryKeywords:
        return self.__po

    @Po.setter
    def Po(self, value: SummaryKeywords) -> None:
        self.__po = value

    @property
    def Pg(self) -> SummaryKeywords:
        return self.__pg

    @Pg.setter
    def Pg(self, value: SummaryKeywords) -> None:
        self.__pg = value

    @property
    def Pcow(self) -> SummaryKeywords:
        return self.__pcow

    @Pcow.setter
    def Pcow(self, value: SummaryKeywords) -> None:
        self.__pcow = value

    @property
    def Pcog(self) -> SummaryKeywords:
        return self.__pcog

    @Pcog.setter
    def Pcog(self, value: SummaryKeywords) -> None:
        self.__pcog = value

    @property
    def Pcgw(self) -> SummaryKeywords:
        return self.__pcgw

    @Pcgw.setter
    def Pcgw(self, value: SummaryKeywords) -> None:
        self.__pcgw = value

    # @property
    # def (self) -> SummaryKeywords:
    #     return self.__
    # @.setter
    # def (self, value: SummaryKeywords) -> None:
    #     self.__ = value

    def __init__(self, verbose: bool = False, **kwargs):
        # production data
        self.__prod_data = SummaryKeywords(verbose=verbose, **kwargs)
        # saturation profile data
        self.__satprof_data = SummaryKeywords(verbose=verbose, **kwargs)
        # sw data
        self.__sw = SummaryKeywords(verbose=verbose, **kwargs)
        # so data
        self.__so = SummaryKeywords(verbose=verbose, **kwargs)
        # sg data
        self.__sg = SummaryKeywords(verbose=verbose, **kwargs)
        # pw data
        self.__pw = SummaryKeywords(verbose=verbose, **kwargs)
        # po data
        self.__po = SummaryKeywords(verbose=verbose, **kwargs)
        # pg data
        self.__pg = SummaryKeywords(verbose=verbose, **kwargs)
        # pcow data
        self.__pcow = SummaryKeywords(verbose=verbose, **kwargs)
        # pcog data
        self.__pcog = SummaryKeywords(verbose=verbose, **kwargs)
        # pcgw data
        self.__pcgw = SummaryKeywords(verbose=verbose, **kwargs)


# grid block data
class GridBlockData:
    @property
    def Sw(self) -> List:
        return self.__sw

    @Sw.setter
    def Sw(self, value: List) -> None:
        self.__sw = value

    @property
    def So(self) -> List:
        return self.__so

    @So.setter
    def So(self, value: List) -> None:
        self.__so = value

    @property
    def Sg(self) -> List:
        return self.__sg

    @Sg.setter
    def Sg(self, value: List) -> None:
        self.__sg = value

    @property
    def Pw(self) -> List:
        return self.__pw

    @Pw.setter
    def Pw(self, value: List) -> None:
        self.__pw = value

    @property
    def Po(self) -> List:
        return self.__po

    @Po.setter
    def Po(self, value: List) -> None:
        self.__po = value

    @property
    def Pg(self) -> List:
        return self.__pg

    @Pg.setter
    def Pg(self, value: List) -> None:
        self.__pg = value

    @property
    def Pcow(self) -> List:
        return self.__pcow

    @Pcow.setter
    def Pcow(self, value: List) -> None:
        self.__pcow = value

    @property
    def Pcog(self) -> List:
        return self.__pcog

    @Pcog.setter
    def Pcog(self, value: List) -> None:
        self.__pcog = value

    @property
    def Pcgw(self) -> List:
        return self.__pcgw

    @Pcgw.setter
    def Pcgw(self, value: List) -> None:
        self.__pcgw = value

    # @property
    # def (self) -> List:
    #     return self.__
    # @.setter
    # def (self, value: List) -> None:
    #     self.__ = value

    def __init__(self, verbose: bool = False, **kwargs):
        # sw data
        self.__sw = []
        # so data
        self.__so = []
        # sg data
        self.__sg = []
        # pw data
        self.__pw = []
        # po data
        self.__po = []
        # pg data
        self.__pg = []
        # pcow data
        self.__pcow = []
        # pcog data
        self.__pcog = []
        # pcgw data
        self.__pcgw = []

    # get property names
    @staticmethod
    def get_property_names(verbose: bool = False, **kwargs):
        return Utils.get_class_properties(GridBlockData)

    # get full property names
    @staticmethod
    def get_full_property_names(verbose: bool = False, **kwargs):
        props = GridBlockData.get_property_names(verbose=verbose, **kwargs)
        full_props = {k: k for k in props}
        for k in props:
            if k == "Sw":
                full_props[k] = "saturation water"
            elif k == "So":
                full_props[k] = "saturation oil"
            elif k == "Sg":
                full_props[k] = "saturation gas"
            elif k == "Pw":
                full_props[k] = "pressure water"
            elif k == "Po":
                full_props[k] = "pressure oil"
            elif k == "Pg":
                full_props[k] = "pressure gas"
            elif k == "Pcow":
                full_props[k] = "capillary pressure oil-water"
            elif k == "Pcog":
                full_props[k] = "capillary pressure oil-gas"
            elif k == "Pcgw":
                full_props[k] = "capillary pressure gas-water"
        return full_props

    # append data
    def append(self, data: Any, verbose: bool = False, **kwargs):
        props = GridBlockData.get_property_names(verbose=verbose, **kwargs)
        for prop in props:
            if hasattr(data, prop):
                data_prop = getattr(data, prop)
                if data_prop and isinstance(data_prop, list):
                    for k in range(0, len(data_prop)):
                        getattr(self, prop).append(data_prop[k])


# plot settings
class PlotSettings:
    @property
    def Name(self) -> str:
        return self.__solution_name

    @Name.setter
    def Name(self, value: str) -> None:
        self.__solution_name = value

    @property
    def Xlabel(self) -> str:
        return self.__solution_xlabel

    @Xlabel.setter
    def Xlabel(self, value: str) -> None:
        self.__solution_xlabel = value

    @property
    def Ylabel(self) -> str:
        return self.__solution_ylabel

    @Ylabel.setter
    def Ylabel(self, value: str) -> None:
        self.__solution_ylabel = value

    @property
    def Xmin(self) -> float:
        return self.__solution_xmin

    @Xmin.setter
    def Xmin(self, value: float) -> None:
        self.__solution_xmin = value

    @property
    def Xmax(self) -> float:
        return self.__solution_xmax

    @Xmax.setter
    def Xmax(self, value: float) -> None:
        self.__solution_xmax = value

    @property
    def Ymin(self) -> float:
        return self.__solution_ymin

    @Ymin.setter
    def Ymin(self, value: float) -> None:
        self.__solution_ymin = value

    @property
    def Ymax(self) -> float:
        return self.__solution_ymax

    @Ymax.setter
    def Ymax(self, value: float) -> None:
        self.__solution_ymax = value

    @property
    def Xref(self) -> List:
        return self.__solution_xref

    @Xref.setter
    def Xref(self, value: List) -> None:
        self.__solution_xref = value

    @property
    def Yref(self) -> List:
        return self.__solution_yref

    @Yref.setter
    def Yref(self, value: List) -> None:
        self.__solution_yref = value

    @property
    def Qprod(self) -> List:
        return self.__solution_qprod

    @Qprod.setter
    def Qprod(self, value: List) -> None:
        self.__solution_qprod = value

    @property
    def Savg(self) -> List:
        return self.__solution_savg

    @Savg.setter
    def Savg(self, value: List) -> None:
        self.__solution_savg = value

    @property
    def NumSatPoints(self) -> int:
        return self.__num_sat_points

    @NumSatPoints.setter
    def NumSatPoints(self, value: int) -> None:
        self.__num_sat_points = value

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, num_sat_points: int = 10, verbose: bool = True, **kwargs):
        self.__solution_name = ""
        self.__solution_xlabel = "time: hours"
        self.__solution_ylabel = ""
        self.__solution_xmin = np.float64(0.0)
        self.__solution_xmax = np.float64(0.0)  # duration_time
        self.__solution_ymin = np.float64(0.0)
        self.__solution_ymax = np.float64(1.0)
        self.__solution_xref = np.empty([1, 1])
        self.__solution_yref = np.empty([1, 1])
        self.__solution_savg = np.empty([1, 1])
        self.__solution_qprod = np.empty([1, 1])
        self.__num_sat_points = num_sat_points


# scal experiment specs
class ScalExperiment:
    @property
    def ProjectSetupData(self) -> ProjectSetup:
        return self.__project_setup

    @ProjectSetupData.setter
    def ProjectSetupData(self, value: ProjectSetup) -> None:
        self.__project_setup = value

    @property
    def ScalModelData(self) -> ScalModel:
        return self.__scal_model

    @ScalModelData.setter
    def ScalModelData(self, value: ScalModel) -> None:
        self.__scal_model = value

    @property
    def CoreSampleData(self) -> CoreSample:
        return self.__core_sample

    @CoreSampleData.setter
    def CoreSampleData(self, value: CoreSample) -> None:
        self.__core_sample = value

    @property
    def GridData(self) -> Grid:
        return self.__grid

    @GridData.setter
    def GridData(self, value: Grid) -> None:
        self.__grid = value

    @property
    def SimulationOutputData(self) -> SimulationOutput:
        return self.__simulation_output

    @SimulationOutputData.setter
    def SimulationOutputData(self, value: SimulationOutput) -> None:
        self.__simulation_output = value

    @property
    def ObjectiveFunctionData(self) -> ObjectiveFunction:
        return self.__obj_func

    @ObjectiveFunctionData.setter
    def ObjectiveFunctionData(self, value: ObjectiveFunction) -> None:
        self.__obj_func = value

    @property
    def SimulationRun(self) -> int:
        return self.__simulation_run

    @SimulationRun.setter
    def SimulationRun(self, value: int) -> None:
        self.__simulation_run = value

    @property
    def PlotSettingsData(self) -> PlotSettings:
        return self.__plot_settings

    @PlotSettingsData.setter
    def PlotSettingsData(self, value: PlotSettings) -> None:
        self.__plot_settings = value

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, vtu_output: bool = False, verbose: bool = True, **kwargs):
        # project setup
        self.ProjectSetupData = ProjectSetup(verbose=verbose, **kwargs)

        # scal model
        self.ScalModelData = ScalModel(verbose=verbose, **kwargs)

        # core sample
        self.CoreSampleData = CoreSample(verbose=verbose, **kwargs)

        # grid
        self.GridData = Grid(verbose=verbose, **kwargs)

        # simulation output data
        self.SimulationOutputData = SimulationOutput(verbose=verbose, **kwargs)

        # objective function data
        self.ObjectiveFunctionData = ObjectiveFunction(verbose=verbose, **kwargs)

        # simulation run
        self.SimulationRun = -1

        # plot settings
        self.PlotSettingsData = PlotSettings(verbose=verbose, **kwargs)

        # read rock and fluid data
        self.read_rock_and_fluid_data(verbose=verbose, **kwargs)

        # add observation keywords
        self.add_observation_keywords(verbose=verbose, **kwargs)

        # assign plot settings
        self.assign_plot_settings(verbose=verbose, **kwargs)

    # read grid data
    def read_rock_and_fluid_data(self, verbose: bool = False, **kwargs):
        # experiment name
        experiment_name = self.ProjectSetupData.ExperimentName
        # flooding
        flooding = self.ProjectSetupData.FloodingType
        # rock and fluid data file
        rock_and_fluid_datafile = self.ProjectSetupData.RockFluidDatafile
        # grid type
        grid_type = self.GridData.Type
        # number of grid blocks
        num_grid_blocks = self.GridData.NumGridBlocks

        if verbose:
            print("\nConfiguring", experiment_name, "experiment data set ...")

        (
            length,
            diameter,
            radius_centre,
            depth,
            porosity,
            permeability,
            rock_compressibility,
            density_water,
            viscosity_water,
            viscosibility_water,
            density_oil,
            viscosity_oil,
            viscosibility_oil,
            sw_init,
        ) = table_data.load_rock_and_fluid_data(rock_and_fluid_datafile, verbose)

        visc_oil = self.ScalModelData.Oil.Viscosity
        visc_water = self.ScalModelData.Water.Viscosity
        if visc_oil is not None and visc_oil != "default":
            viscosity_oil = np.float64(visc_oil)
        if visc_water is not None and visc_water != "default":
            viscosity_water = np.float64(visc_water)

        area = np.float64(math.pi * np.float64(diameter**2) / np.float64(4.0))
        volume = np.float64(length * area)
        porevolume = np.float64(porosity * volume)
        distance_to_inlet = np.float64(radius_centre - 0.5 * length)
        distance_to_outlet = np.float64(radius_centre + 0.5 * length)
        width = diameter

        # fluid-in-place
        owip = np.float64(porevolume * sw_init)
        ooip = np.float64(porevolume - owip)
        ogip = np.float64(0.0)

        # assign core sample data
        self.CoreSampleData.Length = length
        self.CoreSampleData.Width = width
        self.CoreSampleData.Area = area
        self.CoreSampleData.Volume = volume
        self.CoreSampleData.DistanceToInlet = distance_to_inlet
        self.CoreSampleData.DistanceToOutlet = distance_to_outlet
        self.CoreSampleData.Diameter = diameter
        self.CoreSampleData.RadiusCentre = radius_centre
        self.CoreSampleData.Depth = depth

        # assign rock data
        self.ScalModelData.RockData.Permeability = permeability
        self.ScalModelData.RockData.Porosity = porosity
        self.ScalModelData.RockData.PoreVolume = porevolume
        self.ScalModelData.RockData.Compressibility = rock_compressibility
        self.ScalModelData.RockData.Ooip = ooip
        self.ScalModelData.RockData.Owip = owip
        self.ScalModelData.RockData.Ogip = ogip
        self.ScalModelData.RockData.SwatInit = sw_init

        # assign fluid data
        self.ScalModelData.Oil.Density = density_oil
        self.ScalModelData.Oil.Viscosity = viscosity_oil
        self.ScalModelData.Oil.Viscosibility = viscosibility_oil

        self.ScalModelData.Water.Density = density_water
        self.ScalModelData.Water.Viscosity = viscosity_water
        self.ScalModelData.Water.Viscosibility = viscosibility_water

        # output core sample properties
        if verbose:
            print(f"\nСore sample characteristics:")
            print(f"\ncore sample length = {self.CoreSampleData.Length} [ cm ]")
            print(f"\ncore sample area = {self.CoreSampleData.Area} [ cm^2 ]")
            print(f"\ncore sample volume = {self.CoreSampleData.Volume} [ cc ]")
            print(f"\ncentre radius = {self.CoreSampleData.RadiusCentre} [ cm ]")

            print(
                f"\ncore sample permeability = {self.ScalModelData.RockData.Permeability} [ mD ]"
            )
            print(
                f"\ncore sample porosity = {self.ScalModelData.RockData.Porosity} [ % ]"
            )
            print(
                f"\ncore sample pore volume = {self.ScalModelData.RockData.PoreVolume} [ cc ]"
            )

            print(f"\nbrine density  = {self.ScalModelData.Water.Density} [ gm/cc ]")
            print(f"\nbrine viscosity  = {self.ScalModelData.Water.Viscosity} [ cP ]")
            print(f"\noil density  = {self.ScalModelData.Oil.Density} [ gm/cc ]")
            print(f"\noil viscosity  = {self.ScalModelData.Oil.Viscosity} [ cP ]")

            print(
                f"\noriginal oil in place = {self.ScalModelData.RockData.Ooip} [ cc ]"
            )
            print(
                f"\noriginal water in place = {self.ScalModelData.RockData.Owip} [ cc ]"
            )
            print(
                f"\ninitial water saturation = {self.ScalModelData.RockData.SwatInit} [ VOLFRAC ]"
            )

        # core and outcore region numbers
        core_region = int(1)  # core region number with respect to FIP table
        outcore_region = int(
            2
        )  # outside of core region number with respect to FIP table

        (
            num_cells,
            num_refined_cells,
            num_first_cells,
            num_last_cells,
            dl,
            dr,
        ) = deck.grid_blocks(
            experiment_name,
            flooding,
            grid_type,
            num_grid_blocks,
            self.CoreSampleData.Length,
        )
        uniform_gravity = False
        gmult = deck.cell_gravity_multipliers(
            uniform_gravity,
            num_cells,
            num_first_cells,
            num_last_cells,
            self.CoreSampleData.Length,
            self.CoreSampleData.DistanceToInlet,
            dr,
        )
        if verbose:
            print("\nGrid characteristics:")
            print("\nTotal number of cells = ", num_cells)
            print("\nNumber of core cells = ", num_grid_blocks)
            print("\nNumber of first outside-cells = ", num_first_cells)
            print("\nNumber of last  outside-cells = ", num_last_cells)
            if experiment_name == "CENT":
                print("\nGravity multipliers:\n")
                print(gmult)

        # assign grid data
        self.GridData.CoreRegionId = core_region
        self.GridData.OutcoreRegionId = outcore_region
        self.GridData.NumCells = num_cells
        self.GridData.RefinedCells = num_refined_cells
        self.GridData.FirstCells = num_first_cells
        self.GridData.LastCells = num_last_cells
        self.GridData.Dl = dl
        self.GridData.Dr = dr
        self.GridData.GravityMultiplier = gmult

        # define mesh parameters
        (
            NX,
            NY,
            NZ,
            dx,
            dy,
            dz,
            cells,
            core_cells,
            outside_cells,
        ) = deck.get_mesh(
            experiment_name,
            flooding,
            grid_type,
            num_grid_blocks,
            length,
            diameter,
            distance_to_inlet,
            depth,
            verbose,
        )
        # define mesh coordinates
        pxyz = deck.blocked_mesh(NX, NY, NZ, dx, dy, dz, depth)
        # define connectivity
        cell_points = deck.cell_points(NX, NY, NZ)

        # define blocks for saturation profile
        dxC = np.empty([1, 1])
        dxC = deck.centres_of_grid_blocks(
            experiment_name, flooding, grid_type, num_grid_blocks, length
        )

        if verbose:
            print("NX = ", NX, "NY = ", NY, "NZ = ", NZ)

        self.GridData.Nx = NX
        self.GridData.Ny = NY
        self.GridData.Nz = NZ
        self.GridData.NumGridCells = NX * NY * NZ
        self.GridData.Dx = dx
        self.GridData.Dy = dy
        self.GridData.Dz = dz
        self.GridData.DxC = dxC
        self.GridData.Pxyz = pxyz
        self.GridData.CellPoints = cell_points
        self.GridData.Cells = cells
        self.GridData.CoreCells = core_cells
        self.GridData.OutsideCells = outside_cells

    # add production data keywords
    # @TODO: create universal approach for 'ECLIPSE', 'OPM', 'tNavigator', etc.
    def add_observation_keywords(self, verbose: bool = False, **kwargs):
        # production data
        self.add_production_data_summary_keywords(verbose=verbose, **kwargs)
        # saturation profile keywords
        self.add_saturation_profile_summary_keywords(verbose=verbose, **kwargs)
        # block keywords
        self.add_block_summary_keywords(verbose=verbose, **kwargs)

    # add production data keywords
    # @TODO: create universal approach for 'ECLIPSE', 'OPM', 'tNavigator', etc.
    def add_production_data_summary_keywords(self, verbose: bool = False, **kwargs):
        # experiment name
        experiment_name = self.ProjectSetupData.ExperimentName
        # flooding
        flooding = self.ProjectSetupData.FloodingType
        # grid type
        grid_type = self.GridData.Type
        # number of grid blocks
        num_grid_blocks = self.GridData.NumGridBlocks
        num_first_cells = self.GridData.FirstCells
        num_last_cells = self.GridData.LastCells
        num_cells = self.GridData.NumCells  # including outer regions
        first_cell_id = 1  # num_first_cells + 1
        last_cell_id = num_cells  # num_cells - num_last_cells
        # summary keywords
        sum_data = self.SimulationOutputData.ProductionData
        # core region number
        core_region_num = self.GridData.CoreRegionId
        outcore_region_num = self.GridData.OutcoreRegionId

        # summary keyword specs
        non_wellname = SummaryKeywords.non_wellname
        field_wellname = SummaryKeywords.field_wellname
        time_num = SummaryKeywords.time_num
        interregion_num = SummaryKeywords.interregion_num

        # units and conversion factors
        press_unit = "bar"
        press_unit_mult = UnitsConverter.atm2bar
        vol_unit = "cc"
        vol_unit_mult = 1.0
        sat_unit = ""
        sat_unit_mult = 1.0

        # legacy version
        # the code is kept for potential use in future
        # WARNING: several keywords muight be under legacy versions, ONLY ONE must be used
        legacy_versions = False

        # setup of simulator specific output
        if (experiment_name == "SS") or (experiment_name == "USS"):
            # Observations:
            # 0 : time
            # 1 : inlet pressure
            # 2 : outlet pressure
            # 3 : cumulative oil injected
            # 4 : cumulative water injected
            # 5 : cumulative oil production
            # 6 : cumulative water production
            # 7 : oil in-place
            # 8 : water in-place

            # === 1: inlet pressure ===
            # WARNING: ONLY ONE keyword must be used
            if legacy_versions:
                # WBHP ( well bottomhole pressure - inlet )
                sum_data.add_well_or_group_keyword(
                    "WBHP", "INJ", unit=press_unit, unit_mult=press_unit_mult, **kwargs
                )
            # BPR ( block oil pressure - inlet )
            sum_data.add_region_or_block_keyword(
                "BPR",
                first_cell_id,
                unit=press_unit,
                unit_mult=press_unit_mult,
                **kwargs,
            )

            # === 2: outlet pressure ===
            if legacy_versions:
                # WBHP ( well bottomhole pressure - outlet )
                sum_data.add_well_or_group_keyword(
                    "WBHP", "PROD", unit=press_unit, unit_mult=press_unit_mult, **kwargs
                )
            # BPR ( block oil pressure - outlet )
            sum_data.add_region_or_block_keyword(
                "BPR",
                last_cell_id,
                unit=press_unit,
                unit_mult=press_unit_mult,
                **kwargs,
            )

            # === 3: cumulative oil injection ===
            # WARNING: ONLY ONE keyword must be used
            if legacy_versions:
                # FOIT ( field oil injection total )
                sum_data.add_field_keyword(
                    "FOIT", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                )
            # ROIT ( region oil injection total )
            sum_data.add_region_or_block_keyword(
                "ROIT",
                outcore_region_num,
                unit=vol_unit,
                unit_mult=vol_unit_mult,
                **kwargs,
            )

            # === 4: cumulative water injection ===
            # WARNING: ONLY ONE keyword must be used
            if legacy_versions:
                # FWIT ( field oil injection total )
                sum_data.add_field_keyword(
                    "FWIT", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                )
            # RWPT ( region water injection total )
            sum_data.add_region_or_block_keyword(
                "RWIT",
                outcore_region_num,
                unit=vol_unit,
                unit_mult=vol_unit_mult,
                **kwargs,
            )

            # === 5: cumulative oil production ===
            # WARNING: ONLY ONE keyword must be used
            if legacy_versions:
                if grid_type in {"core", "core-refined"}:
                    # WOPT ( well oil production total )
                    sum_data.add_well_or_group_keyword(
                        "WOPT", "PROD", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
                    # FOPT ( field oil production total )
                    sum_data.add_field_keyword(
                        "FOPT", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
                    # ROFT ( interregion oil flow total - liquid and wet gas phase )
                    sum_data.add_region_or_block_keyword(
                        "ROFT",
                        interregion_num,
                        unit=vol_unit,
                        unit_mult=vol_unit_mult,
                        **kwargs,
                    )
                    # WOPT ( well oil production total )
                    sum_data.add_well_or_group_keyword(
                        "WOPT", "PROD", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
                else:
                    # WARNING: ONLY ONE keyword must be used
                    if experiment_name == "SS":
                        # WARNING: ONLY ONE keyword must be used
                        pass
                    elif experiment_name == "USS":
                        # WARNING: ONLY ONE keyword must be used
                        # ROFTL( interregion oil flow total - liquid phase )
                        sum_data.add_region_or_block_keyword(
                            "ROFTL",
                            interregion_num,
                            unit=vol_unit,
                            unit_mult=vol_unit_mult,
                            **kwargs,
                        )
                        # ROFT ( interregion oil flow total - liquid and wet gas phase )
                        sum_data.add_region_or_block_keyword(
                            "ROFT",
                            interregion_num,
                            unit=vol_unit,
                            unit_mult=vol_unit_mult,
                            **kwargs,
                        )
                    # WOPT ( well oil production total )
                    sum_data.add_well_or_group_keyword(
                        "WOPT", "PROD", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
                    # FOPT ( field oil production total )
                    sum_data.add_field_keyword(
                        "FOPT", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
                    # WOPT ( well oil production total )
                    sum_data.add_well_or_group_keyword(
                        "WOPT", "PROD", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
            # ROPT ( region oil production total )
            sum_data.add_region_or_block_keyword(
                "ROPT",
                outcore_region_num,
                unit=vol_unit,
                unit_mult=vol_unit_mult,
                **kwargs,
            )

            # === 6: cumulative water production ===
            # WARNING: ONLY ONE keyword must be used
            if legacy_versions:
                if grid_type in {"core", "core-refined"}:
                    # WWPT ( well water production total )
                    sum_data.add_well_or_group_keyword(
                        "WWPT", "PROD", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
                    # FWPT ( field water production total )
                    sum_data.add_field_keyword(
                        "FWPT", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
                else:
                    if experiment_name == "SS":
                        # WWPT ( well water production total )
                        sum_data.add_well_or_group_keyword(
                            "WWPT",
                            "PROD",
                            unit=vol_unit,
                            unit_mult=vol_unit_mult,
                            **kwargs,
                        )
                    elif experiment_name == "USS":
                        # RWFT ( inter region water flow total )
                        sum_data.add_region_or_block_keyword(
                            "RWFT",
                            interregion_num,
                            unit=vol_unit,
                            unit_mult=vol_unit_mult,
                            **kwargs,
                        )
                    # FWFT ( field water flow total )
                    sum_data.add_field_keyword(
                        "FWPT", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )
            # RWPT ( region water production total )
            sum_data.add_region_or_block_keyword(
                "RWPT",
                outcore_region_num,
                unit=vol_unit,
                unit_mult=vol_unit_mult,
                **kwargs,
            )

            # === 7: oil in-place ===
            if legacy_versions:
                # ROSAT ( average oil saturation in the core sample )
                sum_data.add_region_or_block_keyword(
                    "ROSAT",
                    core_region_num,
                    unit=sat_unit,
                    unit_mult=sat_unit_mult,
                    **kwargs,
                )
                # FOSAT ( average oil saturation in the core sample )
                sum_data.add_field_keyword(
                    "FOSAT", unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
                )
                # FOPV ( pore volume containing oil )
                sum_data.add_field_keyword(
                    "FOSAT", unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
                )
            # ROIP ( oil in place )
            sum_data.add_region_or_block_keyword(
                "ROIP",
                core_region_num,
                unit=vol_unit,
                unit_mult=vol_unit_mult,
                **kwargs,
            )

            # === 8: water in-place ===
            if legacy_versions:
                # RWSAT ( average water saturation in the core sample )
                sum_data.add_region_or_block_keyword(
                    "RWSAT",
                    core_region_num,
                    unit=sat_unit,
                    unit_mult=sat_unit_mult,
                    **kwargs,
                )
                # FWSAT ( average water saturation in the core sample )
                sum_data.add_field_keyword(
                    "FWSAT", unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
                )
                # FWPV ( pore volume containing water )
                sum_data.add_field_keyword(
                    "FWPV", unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
                )
            # RWIP ( water in place )
            sum_data.add_region_or_block_keyword(
                "RWIP",
                core_region_num,
                unit=vol_unit,
                unit_mult=vol_unit_mult,
                **kwargs,
            )

        elif experiment_name == "CENT":
            # Observations:
            # 0 : time
            # 1 : cumulative oil production
            # 2 : cumulative water production
            # 3 : average oil saturation
            # 4 : average water saturation

            # === 1: cumulative oil production ===
            if grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
                # WARNING: ONLY ONE keyword must be used
                if legacy_versions:
                    # ROIP ( outside of the core oil in place )
                    sum_data.add_region_or_block_keyword(
                        "ROIP",
                        outcore_region_num,
                        unit=vol_unit,
                        unit_mult=vol_unit_mult,
                        **kwargs,
                    )
                    # ROFTL( interregion oil flow total - liquid phase - outlet )
                    sum_data.add_region_or_block_keyword(
                        "ROFTL",
                        interregion_num,
                        unit=vol_unit,
                        unit_mult=vol_unit_mult,
                        **kwargs,
                    )
                # ROFT( interregion oil flow total - liquid and wet gas phase - outlet )
                sum_data.add_region_or_block_keyword(
                    "ROFT",
                    interregion_num,
                    unit=vol_unit,
                    unit_mult=vol_unit_mult,
                    **kwargs,
                )
            else:
                # WARNING: ONLY ONE keyword must be used
                if legacy_versions:
                    # WOPT ( oil production total - outlet )
                    sum_data.add_well_or_group_keyword(
                        "WOPT", "PROD", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                    )

            # === 2: cumulative water production ===
            if grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
                # WARNING: ONLY ONE keyword must be used
                if legacy_versions:
                    # RWIP ( outside of the core water in place )
                    sum_data.add_region_or_block_keyword(
                        "RWIP",
                        outcore_region_num,
                        unit=vol_unit,
                        unit_mult=vol_unit_mult,
                        **kwargs,
                    )
                # RWFT ( interregion water flow total )
                sum_data.add_region_or_block_keyword(
                    "RWFT",
                    interregion_num,
                    unit=vol_unit,
                    unit_mult=vol_unit_mult,
                    **kwargs,
                )
            else:
                # WWPT ( water production total )
                sum_data.add_well_or_group_keyword(
                    "WWPT", "PROD", unit=vol_unit, unit_mult=vol_unit_mult, **kwargs
                )

            # === 3: average oil saturation ===
            # ROSAT ( average oil saturation in the core sample )
            sum_data.add_region_or_block_keyword(
                "ROSAT",
                core_region_num,
                unit=sat_unit,
                unit_mult=sat_unit_mult,
                **kwargs,
            )

            # === 4: average water saturation ===
            # RWSAT ( average water saturation in the core sample )
            sum_data.add_region_or_block_keyword(
                "RWSAT",
                core_region_num,
                unit=sat_unit,
                unit_mult=sat_unit_mult,
                **kwargs,
            )

        # assign summary data
        self.SimulationOutputData.ProductionData = sum_data

        # define objective function
        obj_func = self.ObjectiveFunctionData
        observation_weights = obj_func.ObservationWeights
        observation_ids = obj_func.ObservationIds
        # observation ids
        if experiment_name in {"SS", "USS"}:
            # Observations:
            # 0 : inlet pressure
            # 1 : outlet pressure
            # 3 : cumulative oil injected
            # 4 : cumulative water injected
            # 5 : cumulative oil production <- obj.func. observation
            # 6 : cumulative water production <- obj.func. observation
            # 7 : oil in-place
            # 8 : water in-place
            # 9 : average water saturation <- obj.func. observation
            # 10 : pressure difference <- obj.func. observation
            observation_ids[ObjectiveFunction.Pin] = 1
            observation_ids[ObjectiveFunction.Pout] = 2
            observation_ids[ObjectiveFunction.Io] = 3
            observation_ids[ObjectiveFunction.Iw] = 4
            observation_ids[ObjectiveFunction.Qo] = 5
            observation_ids[ObjectiveFunction.Qw] = 6
            observation_ids[ObjectiveFunction.Oip] = 7
            observation_ids[ObjectiveFunction.Wip] = 8

            # differential pressure and average saturation
            max_idx = -1
            for k, v in observation_ids.items():
                if v > max_idx:
                    max_idx = v
            if max_idx > -1:
                savg_idx = max_idx + 1
                dp_idx = max_idx + 2
            else:
                savg_idx = -1
                dp_idx = -1
            observation_ids[ObjectiveFunction.Savg] = savg_idx
            observation_ids[ObjectiveFunction.Dp] = dp_idx
            observation_ids[ObjectiveFunction.Fip] = observation_ids[
                ObjectiveFunction.Wip
            ]
            observation_ids[ObjectiveFunction.Savg] = savg_idx
            observation_ids[ObjectiveFunction.Sw] = savg_idx

            # cumulative production
            if flooding == "drainage":
                observation_ids[ObjectiveFunction.Qprod] = observation_ids[
                    ObjectiveFunction.Qw
                ]
            elif flooding == "imbibition":
                observation_ids[ObjectiveFunction.Qprod] = observation_ids[
                    ObjectiveFunction.Qo
                ]

        elif experiment_name in {"CENT"}:
            # Observations:
            # 1 : cumulative oil production <- obj.func. observation
            # 2 : cumulative water production <- obj.func. observation
            # 3 : average oil saturation <- obj.func. observation
            # 4 : average water saturation <- obj.func. observation
            observation_ids[ObjectiveFunction.Qo] = 1
            observation_ids[ObjectiveFunction.Qw] = 2
            observation_ids[ObjectiveFunction.So] = 3
            observation_ids[ObjectiveFunction.Sw] = 4
            # observation_ids[ObjectiveFunction.Pv] = 5

            # cumulative production
            if flooding == "drainage":
                observation_ids[ObjectiveFunction.Qprod] = observation_ids[
                    ObjectiveFunction.Qw
                ]
            elif flooding == "imbibition":
                observation_ids[ObjectiveFunction.Qprod] = observation_ids[
                    ObjectiveFunction.Qo
                ]

            # average saturation
            observation_ids[ObjectiveFunction.Savg] = observation_ids[
                ObjectiveFunction.Sw
            ]

        # assign observation weights and ids
        obj_func.ObservationWeights = observation_weights
        obj_func.ObservationIds = observation_ids

        # add objective function observations
        for obs_name in [
            ObjectiveFunction.Dp,
            ObjectiveFunction.Qprod,
            ObjectiveFunction.Savg,
        ]:
            if obs_name in observation_ids and observation_ids[obs_name] >= 0:
                obj_func.add_observation(
                    obs_name,
                    weight=observation_weights[obs_name],
                    ref_id=observation_ids[obs_name],
                )

    # @TODO: create universal approach for 'ECLIPSE', 'OPM', 'tNavigator', etc.
    # add saturation profile keywords
    def add_saturation_profile_summary_keywords(self, verbose: bool = False, **kwargs):
        # experiment name
        experiment_name = self.ProjectSetupData.ExperimentName
        # flooding
        flooding = self.ProjectSetupData.FloodingType
        # grid type
        grid_type = self.GridData.Type
        # number of grid blocks
        num_grid_blocks = self.GridData.NumGridBlocks
        # number of first cells
        num_first_cells = self.GridData.FirstCells
        # number of last cells
        num_last_cells = self.GridData.LastCells
        # summary keywords
        sum_data = self.SimulationOutputData.SaturationProfile

        # units and conversion factors
        sat_unit = " "
        sat_unit_mult = 1.0

        if grid_type in {"centrifuge-core", "centrifuge-core-refined"}:
            if not centrifuge3D:
                if flooding == "imbibition":
                    for i in range(0, num_grid_blocks):
                        # BWSAT ( water saturation )
                        sum_data.add_region_or_block_keyword(
                            "BWSAT",
                            3 * (i + num_first_cells) + 2,
                            unit=sat_unit,
                            unit_mult=sat_unit_mult,
                            **kwargs,
                        )
                elif flooding == "drainage":
                    for i in range(0, num_grid_blocks):
                        # BOSAT ( oil saturation )
                        sum_data.add_region_or_block_keyword(
                            "BOSAT",
                            3 * (i + num_first_cells) + 2,
                            unit=sat_unit,
                            unit_mult=sat_unit_mult,
                            **kwargs,
                        )
            else:
                if flooding == "imbibition":
                    for i in range(0, num_grid_blocks):
                        # BWSAT ( water saturation )
                        sum_data.add_region_or_block_keyword(
                            "BWSAT",
                            9 * (i + num_first_cells) + 5,
                            unit=sat_unit,
                            unit_mult=sat_unit_mult,
                            **kwargs,
                        )
                elif flooding == "drainage":
                    for i in range(0, num_grid_blocks):
                        # BOSAT ( oil saturation )
                        sum_data.add_region_or_block_keyword(
                            "BOSAT",
                            9 * (i + num_first_cells) + 5,
                            unit=sat_unit,
                            unit_mult=sat_unit_mult,
                            **kwargs,
                        )
        elif grid_type in {"extended-core", "extended-core-refined"}:
            if flooding == "imbibition":
                for i in range(0, num_grid_blocks):
                    # BWSAT ( water saturation )
                    sum_data.add_region_or_block_keyword(
                        "BWSAT",
                        i + num_first_cells + 1,
                        unit=sat_unit,
                        unit_mult=sat_unit_mult,
                        **kwargs,
                    )
            elif flooding == "drainage":
                for i in range(0, num_grid_blocks):
                    # BOSAT ( oil saturation )
                    sum_data.add_region_or_block_keyword(
                        "BOSAT",
                        i + num_first_cells + 1,
                        unit=sat_unit,
                        unit_mult=sat_unit_mult,
                        **kwargs,
                    )
        elif grid_type in {"core", "core-refined"}:
            if flooding == "imbibition":
                for i in range(0, num_grid_blocks):
                    # BWSAT ( water saturation )
                    sum_data.add_region_or_block_keyword(
                        "BWSAT", i + 1, unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
                    )
            elif flooding == "drainage":
                for i in range(0, num_grid_blocks):
                    # BOSAT ( oil saturation )
                    sum_data.add_region_or_block_keyword(
                        "BOSAT", i + 1, unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
                    )

    # @TODO: create universal approach for 'ECLIPSE', 'OPM', 'tNavigator', etc.
    # add keywords
    def add_block_summary_keywords(self, verbose: bool = False, **kwargs):
        # experiment name
        experiment_name = self.ProjectSetupData.ExperimentName
        # flooding
        flooding = self.ProjectSetupData.FloodingType
        # grid type
        grid_type = self.GridData.Type
        # number of grid blocks
        num_grid_blocks = self.GridData.NumGridBlocks
        # number of cells
        # cells = self.GridData.Cells
        # NX = self.GridData.Nx
        # NY = self.GridData.Ny
        # NZ = self.GridData.Nz
        # num_cells = len( cells )
        # num_cells = int( NX * NY * NZ )
        num_cells = self.GridData.NumGridCells

        # units and conversion factors
        sat_unit = 1.0
        sat_unit_mult = 1.0
        press_unit = 1.0
        press_unit_mult = UnitsConverter.atm2bar

        for i in range(0, num_cells):
            # cell_id = cells[i]+1
            cell_id = i + 1
            # BWSAT ( water saturation )
            self.SimulationOutputData.Sw.add_region_or_block_keyword(
                "BWSAT", cell_id, unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
            )
            # BOSAT ( oil saturation )
            self.SimulationOutputData.So.add_region_or_block_keyword(
                "BOSAT", cell_id, unit=sat_unit, unit_mult=sat_unit_mult, **kwargs
            )
            # BPR ( oil phase pressure )
            self.SimulationOutputData.Po.add_region_or_block_keyword(
                "BPR", cell_id, unit=press_unit, unit_mult=press_unit_mult, **kwargs
            )
            # WBPR ( water phase pressure )
            self.SimulationOutputData.Pw.add_region_or_block_keyword(
                "BWPR", cell_id, unit=press_unit, unit_mult=press_unit_mult, **kwargs
            )
            # WGPR ( gas phase pressure )
            self.SimulationOutputData.Pg.add_region_or_block_keyword(
                "BGPR", cell_id, unit=press_unit, unit_mult=press_unit_mult, **kwargs
            )
            # BWPC ( water-oil phase capillary pressure )
            self.SimulationOutputData.Pcow.add_region_or_block_keyword(
                "BWPC", cell_id, unit=press_unit, unit_mult=press_unit_mult, **kwargs
            )
            # BGPC ( gas-oil phase capillary pressure )
            self.SimulationOutputData.Pcog.add_region_or_block_keyword(
                "BGPC", cell_id, unit=press_unit, unit_mult=press_unit_mult, **kwargs
            )

    # assign plot settings
    def assign_plot_settings(self, verbose: bool = False, **kwargs):
        # experiment name
        experiment_name = self.ProjectSetupData.ExperimentName
        # flooding
        flooding = self.ProjectSetupData.FloodingType
        # duration time
        duration_time = self.ProjectSetupData.DurationTime
        # initial pressure
        pressure_init = self.ProjectSetupData.PressInit

        # plotting setup
        solution_name = ""
        solution_xlabel = "time [ hours ]"
        solution_ylabel = ""
        solution_xmin = np.float64(0.0)
        solution_xmax = duration_time
        solution_ymin = np.float64(0.0)
        solution_ymax = np.float64(1.0)
        Xref = np.empty([1, 1])
        Yref = np.empty([1, 1])
        SatA = np.empty([1, 1])
        QprodA = np.empty([1, 1])
        # num_sw_ponts  = int( 50 )

        # read simulator control and observed data
        # time data
        time_data = self.ProjectSetupData.TimeData
        # reference data
        # SS, USS: pressure difference vs. time
        # CENT: oil/water production vs. time
        ref_data = self.ProjectSetupData.ReferenceData
        ref_data_vec = self.ProjectSetupData.ReferenceDataVector
        # simulator control data
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        simcontrol_data = self.ProjectSetupData.SimulationControlData

        # output simulation characteristics
        last_section = len(time_data) - 1
        last_entry = len(time_data[last_section]) - 1
        if verbose:
            print(
                "\nDuration time = ", time_data[last_section][last_entry], "[ hours ]"
            )

        if experiment_name in {"SS", "USS"}:
            # find min and max solution
            solution_min = pressure_init
            solution_max = pressure_init
            for i in range(0, len(ref_data)):
                for j in range(0, len(ref_data[i])):
                    # dp = ref_data[i][j][1]
                    if ref_data[i][j][1] > solution_max:
                        solution_max = ref_data[i][j][1]
                    if ref_data[i][j][1] < solution_min:
                        solution_min = ref_data[i][j][1]
            # plotting setup
            solution_name = "pressure"
            solution_xlabel = "time [ hours ]"
            solution_ylabel = "pressure [ bar ]"
            solution_xmin = 0.0
            solution_xmax = duration_time
            solution_ymin = solution_min
            solution_ymax = solution_max
        elif experiment_name == "CENT":
            # find min and max solution
            solution_min = np.float64(0.0)
            solution_max = np.float64(0.0)
            for i in range(0, len(ref_data)):
                for j in range(0, len(ref_data[i])):
                    if ref_data[i][j][1] > solution_max:
                        solution_max = ref_data[i][j][1]
                    if ref_data[i][j][1] < solution_min:
                        solution_min = ref_data[i][j][1]
            # plotting setup
            if flooding == "drainage":
                # plotting setup
                solution_name = "water production"
                solution_xlabel = "time [ hours ]"
                solution_ylabel = "water production [ cm3 ]"
                solution_xmin = 0.0
                solution_xmax = duration_time
                solution_ymin = solution_min
                solution_ymax = solution_max
            elif flooding == "imbibition":
                solution_name = "oil production"
                solution_xlabel = "time [ hours ]"
                solution_ylabel = "oil production [ cm3 ]"
                solution_xmin = 0.0
                solution_xmax = duration_time
                solution_ymin = solution_min
                solution_ymax = solution_max

        if experiment_name in {"SS", "USS"}:
            # reference data
            ref_data_array = np.asarray(ref_data_vec.copy())
            Xref = ref_data_array[:, 0]
            Yref = ref_data_array[:, 1]
            num_obs_cols = len(ref_data_vec[0]) - 2

            if num_obs_cols > 2:
                QprodA = ref_data_array[:, 2]
                SatA = ref_data_array[:, 3]
            elif num_obs_cols > 1:
                SatA = ref_data_array[:, 2]
            else:
                pass

        elif experiment_name in {"CENT"}:
            # reference data
            ref_data_array = np.asarray(ref_data_vec.copy())
            Xref = ref_data_array[:, 0]
            Yref = ref_data_array[:, 1]
            num_obs_cols = len(ref_data_vec[0]) - 2

            if num_obs_cols > 1:
                SatA = ref_data_array[:, 2]
            else:
                pass

        self.PlotSettingsData.Name = solution_name
        self.PlotSettingsData.Xlabel = solution_xlabel
        self.PlotSettingsData.Ylabel = solution_ylabel
        self.PlotSettingsData.Xmin = solution_xmin
        self.PlotSettingsData.Xmax = solution_xmax
        self.PlotSettingsData.Ymin = solution_ymin
        self.PlotSettingsData.Ymax = solution_ymax
        self.PlotSettingsData.Xref = Xref
        self.PlotSettingsData.Yref = Yref
        self.PlotSettingsData.Savg = SatA
        self.PlotSettingsData.Qprod = QprodA
        # self.PlotSettingsData.NumSatPoints = num_sw_ponts

        # del simcontrol_data_vec
        # del ref_data_vec


# optimization settings
class OptimizationSettings:
    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, verbose=False, **kwargs):
        pass


# parameter settings
class ParameterSettings:
    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, verbose=False, **kwargs):
        pass


# simulation settings
class SimulationSettings:
    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, verbose=False, **kwargs):
        pass


# run settings
class RunSettings:
    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    def __init__(self, verbose=False, **kwargs):
        pass


# SCAL simulator
class ScalSimulator:
    @property
    def Experiments(self) -> List[ScalExperiment]:
        return self.__experiments

    @property
    def SimulationSettingsData(self) -> List[SimulationSettings]:
        return self.__simulation_settings

    # @property
    # def (self) -> float:
    #     return self.__
    # @.setter
    # def (self, value: float) -> None:
    #     self.__ = value

    # get experiment
    def get_experiment(self, id: int = 0, **kwargs) -> ScalExperiment:
        return self.__experiments[id]

    # get simulation settings
    def get_simulation_settings(self, id: int = 0, **kwargs) -> SimulationSettings:
        if id < 0:
            return SimulationSettings(**kwargs)
        num_settings = len(self.__simulation_settings)
        if id >= num_settings:
            for _ in range(id - num_settings + 1):
                self.__simulation_settings.append(None)
        # get simulation settings
        if self.__simulation_settings[id] is None:
            self.__simulation_settings[id] = SimulationSettings(**kwargs)
        return self.__simulation_settings[id]

    def __init__(self, verbose=False, **kwargs):
        self.__experiments = []
        self.__simulation_settings = []

    # add experiment
    def add_experiment(self, **kwargs) -> ScalExperiment:
        experiment = ScalExperiment(**kwargs)
        if experiment:
            self.__experiments.append(experiment)
        return experiment

    # run simulation
    def run(
        self,
        experiment: ScalExperiment,
        simulator_option,
        simulation_name,
        optimize_relperms,
        optimize_cappress,
        # === parameters
        parameters0,
        parameters0_min,
        parameters0_max,
        paramsprec0,
        paramopt0,
        # === simulation settings
        tolerance,
        timestep,
        newtmx,
        # === simulation output mode
        delete_result_files=False,
        detailed_results_output=False,
        verbose=False,
        grid_props_output=False,
        **kwargs,
    ):
        optimization_method = "single-run"
        return self.optimize(
            experiment,
            simulator_option,
            simulation_name,
            optimize_relperms,
            optimize_cappress,
            parameters0,
            parameters0_min,
            parameters0_max,
            paramsprec0,
            paramopt0,
            optimization_method,
            tolerance,
            timestep,
            newtmx,
            delete_result_files=delete_result_files,
            detailed_results_output=detailed_results_output,
            verbose=verbose,
            grid_props_output=grid_props_output,
            **kwargs,
        )

    # optimize parameters
    def optimize(
        self,
        experiment: ScalExperiment,
        simulator_option,
        simulation_name,
        optimize_relperms,
        optimize_cappress,
        # === parameters
        parameters0,
        parameters0_min,
        parameters0_max,
        paramsprec0,
        paramopt0,
        # === simulation settings
        optimization_method,
        tolerance,
        timestep,
        newtmx,
        # === simulation output mode
        delete_result_files=False,
        detailed_results_output=False,
        verbose=False,
        grid_props_output=False,
        plot_with: str = None,
        **kwargs,
    ):
        # # get experiment
        # experiment = self.get_experiment(0)

        # -------------------------------
        # project and workspace settings
        # -------------------------------

        # project name
        project_name = experiment.ProjectSetupData.ProjectName

        # project directories
        basedir = experiment.ProjectSetupData.BaseDirectory
        rootsdir = experiment.ProjectSetupData.SourceDirectory
        project_dirname = experiment.ProjectSetupData.ProjectDirectoryName
        rootwdir = experiment.ProjectSetupData.ProjectDirectory
        rootidir = experiment.ProjectSetupData.ProjectIncludeDirectory
        sim_dirname = experiment.ProjectSetupData.SimulationDirectoryName
        simdir = experiment.ProjectSetupData.SimulationDirectory

        # experiment name
        experiment_name = experiment.ProjectSetupData.ExperimentName

        # ============================================================================
        #            simulation control and observed data
        # ============================================================================

        # flooding type
        flooding = experiment.ProjectSetupData.FloodingType

        # saturation functions
        relperms = experiment.ProjectSetupData.Kr
        cappress = experiment.ProjectSetupData.Pc
        analyt_relperms = experiment.ProjectSetupData.ReferenceKr
        analyt_cappress = experiment.ProjectSetupData.ReferencePc

        # initial pressure
        pressure_init = experiment.ProjectSetupData.PressInit

        # duration time
        # duration_time = experiment.ProjectSetupData.DurationTime

        # rock and fluid data file
        # rock_and_fluid_datafile = experiment.ProjectSetupData.RockFluidDatafile

        # simulator control data file
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        # simcontrol_datafile  = experiment.ProjectSetupData.SimulationControlDatafile
        # simcontrol_plotfile  = experiment.ProjectSetupData.SimulationControlPlotfile

        # observed data file
        # SS, USS: pressure difference vs. time
        # CENT: oil/water production vs. time
        # obs_datafile = experiment.ProjectSetupData.ObservedDatafile
        # obs_plotfile = experiment.ProjectSetupData.ObservedPlotfile

        # simulator control and observed data
        # time data
        time_data = experiment.ProjectSetupData.TimeData
        # reference data
        # SS, USS: pressure difference vs. time
        # CENT: oil/water produxtion vs. time
        # ref_data = experiment.ProjectSetupData.ReferenceData
        # simulator control data
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        simcontrol_data = experiment.ProjectSetupData.SimulationControlData

        # ============================================================================
        #            grid data
        # ============================================================================

        # core sample data
        length = experiment.CoreSampleData.Length
        area = experiment.CoreSampleData.Area
        volume = experiment.CoreSampleData.Volume
        distance_to_inlet = experiment.CoreSampleData.DistanceToInlet
        distance_to_outlet = experiment.CoreSampleData.DistanceToOutlet
        diameter = experiment.CoreSampleData.Diameter
        radius_centre = experiment.CoreSampleData.RadiusCentre
        depth = experiment.CoreSampleData.Depth

        # rock data
        permeability = experiment.ScalModelData.RockData.Permeability
        porosity = experiment.ScalModelData.RockData.Porosity
        porevolume = experiment.ScalModelData.RockData.PoreVolume
        rock_compressibility = experiment.ScalModelData.RockData.Compressibility
        # ooip = experiment.ScalModelData.Rock.Ooip
        # owip = experiment.ScalModelData.Rock.Owip
        # ogip = experiment.ScalModelData.Rock.Ogip
        sw_init = experiment.ScalModelData.RockData.SwatInit

        # fluid data
        density_oil = experiment.ScalModelData.Oil.Density
        viscosity_oil = experiment.ScalModelData.Oil.Viscosity
        viscosibility_oil = experiment.ScalModelData.Oil.Viscosibility

        density_water = experiment.ScalModelData.Water.Density
        viscosity_water = experiment.ScalModelData.Water.Viscosity
        viscosibility_water = experiment.ScalModelData.Water.Viscosibility

        # grid data
        grid_type = experiment.GridData.Type
        num_grid_blocks = experiment.GridData.NumGridBlocks
        # core_region = experiment.GridData.CoreRegionId
        # outcore_region = experiment.GridData.OutcoreRegionId
        # num_cells = experiment.GridData.NumCells
        # num_refined_cells = experiment.GridData.RefinedCells
        # num_first_cells = experiment.GridData.FirstCells
        # num_last_cells = experiment.GridData.LastCells
        # dl = experiment.GridData.Dl
        # dr = experiment.GridData.Dr
        # gmult = experiment.GridData.GravityMultiplier
        # NX = experiment.GridData.Nx
        # NY = experiment.GridData.Ny
        # NZ = experiment.GridData.Nz
        # num_grid_cells = experiment.GridData.NumGridCells
        # dx = experiment.GridData.Dx
        # dy = experiment.GridData.Dy
        # dz = experiment.GridData.Dz
        # dxC = experiment.GridData.DxC
        # pxyz = experiment.GridData.Pxyz
        # cell_points = experiment.GridData.CellPoints
        # cells = experiment.GridData.Cells
        # core_cells = experiment.GridData.CoreCells
        # outside_cells = experiment.GridData.OutsideCells

        # number of saturation points
        num_sw_points = experiment.PlotSettingsData.NumSatPoints

        # language
        # language = 'hungarian'
        language = "english"

        # ============================================================================
        #            saturation functions setup
        # ============================================================================

        if verbose:
            print("\nConfiguring", experiment_name, "experiment data set ...")

        # create analytical saturation function tables if needed
        # in case if there is no analytical capillary pressure function use the initial simulated one
        if analyt_cappress == "empty":
            analyt_cappress = os.path.join(rootsdir, "analyt-cappress.txt")
            is_new_file = True
            sat_funcs.write_pc_table(
                analyt_cappress,
                is_new_file,
                relperms,
                cappress,
                num_sw_points,
                parameters0,
                verbose,
            )

        # in case if there is no analytical relperm functions use the initial simulated one
        if analyt_relperms == "empty":
            analyt_relperms = os.path.join(rootsdir, "analyt-relperms.txt")
            is_new_file = True
            sat_funcs.write_relperms_table(
                analyt_relperms,
                is_new_file,
                relperms,
                cappress,
                num_sw_points,
                parameters0,
                verbose,
            )
        elif analyt_relperms == "Burdine-Mualem":
            analyt_relperms = os.path.join(rootsdir, "analyt-relperms.txt")
            is_new_file = True
            sat_funcs.write_relperms_table(
                analyt_relperms,
                is_new_file,
                "Burdine-Mualem",
                analyt_cappress,
                num_sw_points,
                parameters0,
                verbose,
            )

        # SWI - initial water saturation
        parameters0["SWI"] = np.float64(sw_init)
        parameters0_min["SWI"] = np.float64(sw_init)
        parameters0_max["SWI"] = np.float64(sw_init)
        paramsprec0["SWI"] = np.float64(0.01)
        paramopt0["SWI"] = False

        (
            parameters,
            parameters_min,
            parameters_max,
            paramsprec,
        ) = sat_funcs.optimize_satfunctions(
            relperms,
            analyt_relperms,
            optimize_relperms,
            cappress,
            analyt_cappress,
            optimize_cappress,
            parameters0,
            parameters0_min,
            parameters0_max,
            paramsprec0,
            paramopt0,
            verbose,
        )

        del parameters0
        del parameters0_min
        del parameters0_max
        del paramsprec0

        swof_datafile = os.path.join(rootidir, project_name + "_SWOF.INC")
        swof_dataplot = os.path.join(rootwdir, project_name + "_SWOF.png")
        pc_dataplot = os.path.join(rootwdir, project_name + "_PC.png")
        deck.write_saturation_functions_datafile(
            rootwdir,
            project_name,
            experiment_name,
            flooding,
            relperms,
            cappress,
            num_sw_points,
            parameters,
            verbose,
        )
        sat_funcs.swof_plot(
            swof_datafile,
            swof_dataplot,
            pc_dataplot,
            analyt_relperms,
            analyt_cappress,
            verbose,
            plot_with=plot_with,
        )

        if simulator_option != "output_rock_fluid_data":
            # ====================================================================
            #                         handle observed data
            # ====================================================================

            # plot experiment setup
            self.plot_observed_data(
                experiment, plot_with=plot_with, verbose=verbose, **kwargs
            )

            # save observed data to '.graf' file
            self.save_graf_file(experiment, verbose=verbose, **kwargs)

            # ====================================================================
            #                         generate project data
            # ====================================================================

            # number of data files
            num_datafiles = int(1)

            # project data files
            # SS, USS: one project data file
            # CENT: multiple project data files ( one for each acceleration stage )
            project_datafile = []

            # grid section
            deck.write_grid_operations_datafile(
                rootwdir, project_name, experiment_name, flooding, verbose
            )
            deck.write_grid_geometry_datafile(
                rootwdir,
                project_name,
                experiment_name,
                flooding,
                grid_type,
                num_grid_blocks,
                length,
                diameter,
                distance_to_inlet,
                depth,
                verbose,
            )
            deck.write_grid_properties_datafile(
                rootwdir,
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
            )

            # properties section
            deck.write_pvt_datafile(
                rootwdir,
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
            )
            deck.write_scal_datafile(
                rootwdir,
                project_name,
                experiment_name,
                flooding,
                grid_type,
                num_grid_blocks,
                verbose,
            )
            # deck.write_saturation_functions_datafile( rootwdir, project_name, experiment_name, flooding, relperms, cappress, num_sw_points, parameters, verbose )

            # regions section
            deck.write_regions_datafile(
                rootwdir,
                project_name,
                experiment_name,
                flooding,
                grid_type,
                num_grid_blocks,
                length,
                diameter,
                sameGrav,
                verbose,
            )

            # summary section
            deck.write_summary_datafile(
                rootwdir,
                project_name,
                experiment_name,
                flooding,
                grid_type,
                num_grid_blocks,
                length,
                diameter,
                verbose,
            )

            # schedule section
            deck.write_schedule_specs_datafile(
                rootwdir,
                project_name,
                experiment_name,
                flooding,
                grid_type,
                num_grid_blocks,
                length,
                simcontrol_data,
                pressure_init,
                pressure_init,
                timestep,
                newtmx,
                verbose,
            )

            if (experiment_name == "SS") or (experiment_name == "USS"):
                stage = int(0)
                # solution section
                gravcons = 0.000968  # g [cm2atm/gm]
                if flooding == "drainage":
                    deck.write_initial_conditions_datafile(
                        rootwdir,
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
                        gravcons,
                        gravcons,
                        density_water,
                        density_oil,
                        sameGrav,
                        verbose,
                    )
                elif flooding == "imbibition":
                    deck.write_initial_conditions_datafile(
                        rootwdir,
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
                        gravcons,
                        gravcons,
                        density_oil,
                        density_water,
                        sameGrav,
                        verbose,
                    )

                # schedule section
                deck.write_schedule_datafile(
                    rootwdir,
                    project_name,
                    experiment_name,
                    flooding,
                    grid_type,
                    num_grid_blocks,
                    stage,
                    simcontrol_data,
                    pressure_init,
                    pressure_init,
                    time_data,
                    timestep,
                    newtmx,
                    detailed_results_output,
                    verbose,
                )

                # number of reports in restart file
                num_reports = int(0)

                # data file
                deck.write_simulator_datafile(
                    rootwdir,
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
                    verbose,
                )

                project_datafile.append(os.path.join(rootwdir, project_name + ".data"))

            elif experiment_name == "CENT":
                num_datafiles = len(simcontrol_data)

                # initial acceleration
                gravcons = simcontrol_data[0][0][0]

                # number of reports in restart file
                num_reports = int(0)

                pressure_cent = pressure_init
                for stage in range(0, num_datafiles):
                    gravcons0 = np.float64(0.0)
                    if stage > 0:
                        gravcons0 = simcontrol_data[stage - 1][0][0]
                    gravcons = simcontrol_data[stage][0][0]

                    # data file
                    deck.write_simulator_datafile(
                        rootwdir,
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
                        verbose,
                    )

                    if stage != 0:
                        pressure_cent = 0.0

                    # solution section
                    if flooding == "drainage":
                        deck.write_initial_conditions_datafile(
                            rootwdir,
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
                            pressure_cent,
                            gravcons0,
                            gravcons,
                            density_water,
                            density_oil,
                            sameGrav,
                            verbose,
                        )
                    elif flooding == "imbibition":
                        deck.write_initial_conditions_datafile(
                            rootwdir,
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
                            pressure_cent,
                            gravcons0,
                            gravcons,
                            density_oil,
                            density_water,
                            sameGrav,
                            verbose,
                        )

                    # schedule section
                    if flooding == "drainage":
                        (
                            wbhp_inj,
                            wbhp_prod,
                            press_core,
                            press_outside,
                        ) = deck.calculate_hydrostatic_pressure(
                            experiment_name,
                            flooding,
                            grid_type,
                            num_grid_blocks,
                            length,
                            distance_to_inlet,
                            pressure_init,
                            gravcons,
                            density_water,
                            density_oil,
                            sameGrav,
                        )
                        num_reports += deck.write_schedule_datafile(
                            rootwdir,
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
                        )
                    elif flooding == "imbibition":
                        (
                            wbhp_inj,
                            wbhp_prod,
                            press_core,
                            press_outside,
                        ) = deck.calculate_hydrostatic_pressure(
                            experiment_name,
                            flooding,
                            grid_type,
                            num_grid_blocks,
                            length,
                            distance_to_inlet,
                            pressure_init,
                            gravcons,
                            density_oil,
                            density_water,
                            sameGrav,
                        )
                        num_reports += deck.write_schedule_datafile(
                            rootwdir,
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
                        )
                    if stage > 0:
                        num_reports -= int(1)

                    project_datafile.append(
                        os.path.join(rootwdir, project_name + str(stage) + ".data")
                    )

            # plot relperms and capillary pressure

            # swof_datafile = os.path.join(rootidir, project_name + '_SWOF.INC')
            # swof_dataplot = os.path.join(rootwdir, project_name + '_SWOF.png')
            # pc_dataplot   = os.path.join(rootwdir, project_name + '_PC.png')
            # sat_funcs.swof_plot( swof_datafile, swof_dataplot, pc_dataplot, analyt_relperms, analyt_cappress, verbose )

            if verbose:
                print("\nProject was successfully generated!")
                if num_datafiles > 1:
                    print("\nNumber of generated data files = ", num_datafiles, "!")
                print("\nCurrent saturation functions parameters:")
                print(parameters)

            if simulator_option != "create_project":
                # ============================================================================
                #            simulation
                # ============================================================================

                # use current time for generated log file
                now = time.strftime("%H_%M_%S_%d_%m_%y")

                # necessary simulation files
                simfilename = os.path.join(
                    simdir,
                    str(project_name)
                    + "_"
                    + str(optimization_method)
                    + "_"
                    + str(now)
                    + ".log",
                )
                simplotfile = os.path.join(
                    simdir,
                    str(project_name)
                    + "_"
                    + str(optimization_method)
                    + "_"
                    + str(now)
                    + ".png",
                )

                # open simulation log file
                fout = open(simfilename, "w")
                fout.close()

                global simulation_index

                # array of calculated rms values
                total_rms = []
                default_rms = np.float64(1.0e7)

                num_parameters = len(parameters)

                # create mapping [ parameters vs. arguments ]
                parameters_map = {}
                arg_map = []
                arg_index = int(0)
                for key in sorted(parameters.keys()):
                    parameters_map[key] = int(-1)
                    if parameters_min[key] != parameters_max[key]:
                        arg_map.append(key)
                        parameters_map[key] = arg_index
                        arg_index += 1
                num_args = arg_index

                # initial guess
                xarg0 = np.empty([num_args])
                for key in sorted(parameters.keys()):
                    if parameters_map[key] != -1:
                        xarg0[parameters_map[key]] = parameters[key]

                # define argument bounds
                parameters_bounds = ()
                if num_args > 0:
                    for i in range(0, num_args):
                        parameters_bounds = parameters_bounds + (
                            (parameters_min[arg_map[i]], parameters_max[arg_map[i]]),
                        )

                if verbose:
                    output_text = (
                        "\nNumber of parameters to match is "
                        + str(num_args)
                        + " out of "
                        + str(num_parameters)
                    )
                    print(output_text)

                objfun_args = (
                    experiment,
                    # === rms
                    total_rms,
                    default_rms,
                    # === files and directories
                    simulation_name,
                    project_datafile,
                    simfilename,
                    num_datafiles,
                    # === parameters
                    parameters,
                    parameters_map,
                    parameters_min,
                    parameters_max,
                    # === output mode
                    delete_result_files,
                    grid_props_output,
                    verbose,
                    plot_with,
                )

                # simulation runs
                if optimization_method == "single-run":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nSingle run is going to be performed!"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    self.objective_func(xarg0, *objfun_args, **kwargs)
                elif optimization_method == "custom-brute-force":
                    sortedsimfilename = os.path.join(
                        simdir,
                        str(project_name)
                        + "_"
                        + str(optimization_method)
                        + "_"
                        + str(now)
                        + "_sorted.log",
                    )
                    # fill in parameteres list
                    parameters_list = sat_funcs.create_parameters_list(
                        parameters, parameters_min, parameters_max, paramsprec, verbose
                    )
                    num_runs = len(parameters_list)
                    rms_match = [0, default_rms]
                    parameters_match = parameters.copy()
                    output_text = "\nPlease, wait ..." + "\n" + str(num_runs)
                    if num_runs > 1:
                        output_text += " runs are going to be performed!"
                    else:
                        output_text += " run is going to be performed"
                    output_text += "\nHave a coffee or smth meanwhile ;)\n"

                    if verbose:
                        print(output_text)

                    for i in range(0, num_runs):
                        x = np.empty([num_args])
                        for key in sorted(parameters.keys()):
                            if parameters_map[key] != -1:
                                x[parameters_map[key]] = parameters_list[i][key]
                        total_rms[i][1] = self.objective_func(x, *objfun_args, **kwargs)

                        if total_rms[i][1] < rms_match[1]:
                            rms_match = total_rms[i].copy()
                            parameters_match = parameters.copy()

                    if num_runs != 1:
                        output_text = ""
                        if language == "hungarian":
                            output_text += "\nlegjobb_rms = " + str(rms_match[1])
                        else:
                            output_text += "\nbest_rms = " + str(rms_match[1])

                        if verbose:
                            print(output_text)

                        x = np.empty([num_args])
                        for key in sorted(parameters.keys()):
                            if parameters_map[key] != -1:
                                x[parameters_map[key]] = parameters_match[key]
                        simulation_index = rms_match[0]
                        self.objective_func(x, *objfun_args, **kwargs)

                        # sorted rms file
                        total_rms.sort(key=lambda x: x[1])
                        fouts = open(sortedsimfilename, "w")
                        for i in range(0, num_runs):
                            run_index = total_rms[i][0]
                            output_text = "\nrun:\trms = " + str(total_rms[i][1])
                            for key in sorted(parameters_list[run_index].keys()):
                                output_text += (
                                    "\t"
                                    + str(key)
                                    + " = "
                                    + str(parameters_list[run_index][key])
                                )
                            fouts.writelines([output_text, "\n"])
                        fouts.close()
                elif optimization_method == "brute":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.brute(
                        self.objective_func, parameters_bounds, args=objfun_args
                    )
                    if verbose:
                        output_text = (
                            " xarg = " + str(resopt[0]) + ", val = " + str(resopt[1])
                        )
                        print(output_text)
                    self.objective_func(resopt[0], *objfun_args, **kwargs)
                elif optimization_method == "Nelder-Mead":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args, **kwargs)
                elif optimization_method == "Powell":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args, **kwargs)
                elif optimization_method == "BFGS":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args, **kwargs)
                elif optimization_method == "CG":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args, **kwargs)
                elif optimization_method == "L-BFGS-B":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        bounds=parameters_bounds,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args, **kwargs)
                elif optimization_method == "TNC":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        bounds=parameters_bounds,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args**kwargs)
                elif optimization_method == "SLSQP":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        bounds=parameters_bounds,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args)
                elif optimization_method == "COBYLA":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.minimize(
                        self.objective_func,
                        xarg0,
                        args=objfun_args,
                        method=optimization_method,
                        tol=tolerance,
                        options={"disp": True},
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args, **kwargs)
                elif optimization_method == "differential-evolution":
                    if verbose:
                        output_text = (
                            "\nPlease, wait ..."
                            + "\nOptimization by "
                            + str(optimization_method)
                            + " method is going to be performed"
                            + "\nHave a coffee or smth meanwhile ;)\n"
                        )
                        print(output_text)
                    resopt = sp.optimize.differential_evolution(
                        self.objective_func,
                        parameters_bounds,
                        args=objfun_args,
                        tol=tolerance,
                        disp=True,
                    )
                    if verbose:
                        print(resopt.message)
                        print("Number of iterations performed by the optimizer:")
                        print(resopt.nit)
                        print("Solution of the optimization:")
                        print(resopt.x)
                        print("Value of the objective function:")
                        print(resopt.fun)
                    self.objective_func(resopt.x, *objfun_args, **kwargs)

                if len(total_rms) > 1:
                    # plot rms
                    total_loss_array = np.asarray(total_rms)
                    x_loss = total_loss_array[:, 0]
                    y_loss = total_loss_array[:, 1]
                    self.plot_loss(
                        x_loss, y_loss, plot_with=plot_with, write_file=simplotfile
                    )

                if verbose:
                    print("\nFinished scal simulation!")

    # objective function for optimization
    def objective_func(
        self,
        xarg,
        experiment: ScalExperiment,
        # === rms
        total_rms,
        default_rms,
        # === files and directories
        simulation_name,
        project_datafile,
        simfilename,
        num_datafiles,
        # === parameters
        parameters,
        parameters_map,
        parameters_min,
        parameters_max,
        # === output mode
        delete_result_files,
        grid_output,
        verbose,
        plot_with,
        **kwargs,
    ):
        # project name
        project_name = experiment.ProjectSetupData.ProjectName

        # project directories
        basedir = experiment.ProjectSetupData.BaseDirectory
        rootsdir = experiment.ProjectSetupData.SourceDirectory
        project_dirname = experiment.ProjectSetupData.ProjectDirectoryName
        rootwdir = experiment.ProjectSetupData.ProjectDirectory
        rootidir = experiment.ProjectSetupData.ProjectIncludeDirectory
        sim_dirname = experiment.ProjectSetupData.SimulationDirectoryName
        simdir = experiment.ProjectSetupData.SimulationDirectory

        # experiment name
        experiment_name = experiment.ProjectSetupData.ExperimentName

        # ============================================================================
        #            simulation control and observed data
        # ============================================================================

        # flooding type
        flooding = experiment.ProjectSetupData.FloodingType

        # saturation functions
        relperms = experiment.ProjectSetupData.Kr
        cappress = experiment.ProjectSetupData.Pc
        analyt_relperms = experiment.ProjectSetupData.ReferenceKr
        analyt_cappress = experiment.ProjectSetupData.ReferencePc

        # # initial pressure
        # pressure_init = experiment.ProjectSetupData.PressInit

        # # duration time
        # duration_time = experiment.ProjectSetupData.DurationTime

        # # rock and fluid data file
        # rock_and_fluid_datafile = experiment.ProjectSetupData.RockFluidDatafile

        # # simulator control data file
        # # SS, USS: oil/water injection rate vs. time
        # # CENT: centrifuge acceleration vs. time
        # simcontrol_datafile  = experiment.ProjectSetupData.SimulationControlDatafile
        # simcontrol_plotfile  = experiment.ProjectSetupData.SimulationControlPlotfile

        # # observed data file
        # # SS, USS: pressure difference vs. time
        # # CENT: oil/water production vs. time
        # obs_datafile = experiment.ProjectSetupData.ObservedDatafile
        # obs_plotfile = experiment.ProjectSetupData.ObservedPlotfile

        # simulator control and observed data
        # time data
        # time_data = experiment.ProjectSetupData.TimeData
        # reference data
        # SS, USS: pressure difference vs. time
        # CENT: oil/water produxtion vs. time
        ref_data = experiment.ProjectSetupData.ReferenceData
        # simulator control data
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        # simcontrol_data = experiment.ProjectSetupData.SimulationControlData

        # ============================================================================
        #            observation data
        # ============================================================================
        # objective function data
        obsdata_weights = experiment.ObjectiveFunctionData.Weight
        obsdata_id = experiment.ObjectiveFunctionData.ReferenceId
        prod_id = experiment.ObjectiveFunctionData.ObservationIds[
            ObjectiveFunction.Qprod
        ]
        sat_id = experiment.ObjectiveFunctionData.ObservationIds[ObjectiveFunction.Savg]

        # observation data keywords
        obsdata_keywords = experiment.SimulationOutputData.ProductionData.Keyword
        obsdata_type = experiment.SimulationOutputData.ProductionData.Type
        obsdata_wgnames = experiment.SimulationOutputData.ProductionData.Wgname
        obsdata_nums = experiment.SimulationOutputData.ProductionData.Num
        obsdata_convfactors = (
            experiment.SimulationOutputData.ProductionData.UnitConversionFactor
        )
        num_wgnames = experiment.SimulationOutputData.ProductionData.WgnamesLen
        num_nums = experiment.SimulationOutputData.ProductionData.NumsLen

        # saturation profile keywords
        satprof_keywords = experiment.SimulationOutputData.SaturationProfile.Keyword
        satprof_type = experiment.SimulationOutputData.SaturationProfile.Type
        satprof_wgnames = experiment.SimulationOutputData.SaturationProfile.Wgname
        satprof_nums = experiment.SimulationOutputData.SaturationProfile.Num
        satprof_weights = experiment.SimulationOutputData.SaturationProfile.Wgname
        satprof_convfactors = (
            experiment.SimulationOutputData.SaturationProfile.UnitConversionFactor
        )

        # ============================================================================
        #            plot settings
        # ============================================================================

        # plot settings
        solution_name = experiment.PlotSettingsData.Name
        num_sw_points = experiment.PlotSettingsData.NumSatPoints

        # assign new values to parameters
        out_of_range = False
        for key in parameters.keys():
            if parameters_map[key] != -1:
                parameters[key] = xarg.flat[parameters_map[key]]
                if parameters[key] < parameters_min[key]:
                    out_of_range = True
                if parameters[key] > parameters_max[key]:
                    out_of_range = True

        current_total_rms = default_rms
        current_total_rms_prime = default_rms
        current_rms = default_rms

        if out_of_range:
            raise Warning(
                "\nWarning: at least one of control parameters is out of range!\n"
            )

        # index of simulation
        global simulation_index

        simulation_index += 1

        # simulation name
        simname = "sim"
        for key in sorted(parameters.keys()):
            if parameters_map[key] != -1:
                simname += "_" + str(key) + "_" + str(parameters[key])
        simulation_name = simname if (simulation_name == "default") else simulation_name

        # new working directory
        rootwdir = os.path.join(basedir, project_dirname)
        rootidir = os.path.join(rootwdir, "include")
        simdir = os.path.join(sim_dirname, simulation_name)
        wdir = os.path.join(basedir, simdir)
        idir = os.path.join(wdir, "include")

        # results folder
        results_folder = os.path.join(wdir, "results")
        txt_folder = os.path.join(results_folder, "TXT")
        pics_folder = os.path.join(results_folder, "PICS")
        vtu_folder = os.path.join(results_folder, "VTU")
        # ecl_folder = os.path.join(results_folder, 'ECL')

        # rms
        paramsfile = os.path.join(txt_folder, project_name + "_parameters.txt")
        rmsfile = os.path.join(txt_folder, project_name + "_rms.txt")

        # solution
        sol_datafile = os.path.join(txt_folder, project_name + "_solution.txt")
        sol_dataplot = os.path.join(
            pics_folder, project_name + "_" + solution_name + ".png"
        )

        # difference between simulated and measured values
        soldiff_datafile = os.path.join(
            txt_folder, project_name + "_" + solution_name + "_difference.txt"
        )
        soldiff_dataplot = os.path.join(
            pics_folder, project_name + "_" + solution_name + "_difference.png"
        )

        # relperm and capillary pressure curves
        swof_datafile = os.path.join(idir, project_name + "_SWOF.INC")
        swof_dataplot = os.path.join(pics_folder, project_name + "_SWOF.png")
        pc_dataplot = os.path.join(pics_folder, project_name + "_PC.png")

        # average saturation
        swat_dataplot = os.path.join(pics_folder, project_name + "_SWAT" + ".png")

        # cumulative production
        prod_dataplot = ""
        if flooding == "imbibition":
            prod_dataplot = os.path.join(
                pics_folder, project_name + "_oil_production" + ".png"
            )
        elif flooding == "drainage":
            prod_dataplot = os.path.join(
                pics_folder, project_name + "_water_production" + ".png"
            )

        # saturation profile
        satprof_datafile = os.path.join(
            txt_folder, project_name + "_saturation_profile.txt"
        )
        satprof_dataplot = os.path.join(
            pics_folder, project_name + "_saturation_profile.png"
        )

        # solution file
        sol_specs_file, sol_sum_file = deck.simulator_solution_files(wdir, project_name)

        sat_data = []
        data = []
        data_diff = []

        sim_key = ""
        for key in sorted(parameters.keys()):
            sim_key += "\t" + str(key) + " = " + str(parameters[key])
        output_text = "\nrun[" + str(simulation_index) + "] :" + sim_key
        if verbose:
            print(output_text)

        simulation_status = False

        if delete_result_files:
            if os_utils.check_file(sol_datafile):
                os_utils.remove_file(sol_datafile)
            if os_utils.check_dir(wdir):
                os_utils.remove_dir(wdir)
            simulation_status = True
        elif experiment_name in {"SS", "USS"}:
            if (
                not os_utils.check_file(sol_specs_file)
                or not os_utils.check_file(sol_sum_file)
                or not os_utils.check_file(sol_datafile)
            ):
                simulation_status = True
        elif experiment_name == "CENT":
            if not os_utils.check_file(sol_datafile):
                simulation_status = True
            else:
                for stage in range(0, num_datafiles):
                    stage_project_name = project_name + str(stage)
                    (
                        temp_sol_specs_file,
                        temp_sol_sum_file,
                    ) = deck.simulator_solution_files(wdir, stage_project_name)

                    if (not os_utils.check_file(temp_sol_specs_file)) or (
                        not os_utils.check_file(temp_sol_sum_file)
                    ):
                        simulation_status = True
                        break

        if simulation_status:
            # # summary data keywords
            # summary_keywords = experiment.SimulationOutput
            # # objective function
            # objfunc = experiment.ObjectiveFunctionData
            # # define the type of observation data( defined by name or block number )
            # num_wgnames = experiment.SimulationOutputData.ProductionData.NumsLen
            # num_nums    = experiment.SimulationOutputData.ProductionData.WgnamesLen

            # copy include directory
            os_utils.copy_dir(rootidir, idir)
            os_utils.make_dir(results_folder)
            os_utils.make_dir(txt_folder)
            os_utils.make_dir(pics_folder)
            if grid_output:
                os_utils.make_dir(vtu_folder)
            if (experiment_name == "SS") or (experiment_name == "USS"):
                os_utils.copy_file(project_datafile[0], wdir)
            elif experiment_name == "CENT":
                for stage in range(0, num_datafiles):
                    os_utils.copy_file(project_datafile[stage], wdir)

            # write SWOF file
            deck.write_saturation_functions_datafile(
                wdir,
                project_name,
                experiment_name,
                flooding,
                relperms,
                cappress,
                num_sw_points,
                parameters,
                verbose,
            )

            if experiment_name in {"SS", "USS"}:
                # run simulator
                t0 = time.process_time()
                deck.run_simulator(basedir, simdir, project_name, verbose, **kwargs)
                if verbose:
                    print(
                        "\nit took",
                        time.process_time() - t0,
                        "seconds to perform the simulation",
                    )

                # read solution
                data = deck.read_solution(
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
                )

                # read saturation profile data
                sat_data = deck.read_solution(
                    wdir,
                    project_name,
                    int(0),
                    len(satprof_nums),
                    satprof_keywords,
                    satprof_type,
                    satprof_wgnames,
                    satprof_nums,
                    satprof_convfactors,
                    verbose,
                )

                if len(data) != 0:
                    # add extra observations
                    num_rows = len(data)
                    fip_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Fip
                    ]
                    oip_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Oip
                    ]
                    wip_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Wip
                    ]
                    pin_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Pin
                    ]
                    pout_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Pout
                    ]
                    sat_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Savg
                    ]
                    dp_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Dp
                    ]
                    prod_id = experiment.ObjectiveFunctionData.ObservationIds[
                        ObjectiveFunction.Qprod
                    ]

                    for i in range(num_rows):
                        data[i].append(np.nan)  # calculated savg
                        data[i].append(np.nan)  # calculated dp
                        # calculate 'Average Saturation'
                        data[i][sat_id] = np.float64(
                            data[i][fip_id] / (data[i][wip_id] + data[i][oip_id])
                        )
                        # calculate 'Differential Pressure'
                        data[i][dp_id] = np.float64(data[i][pin_id] - data[i][pout_id])

                    # save data
                    table_data.save(sol_datafile, data, verbose)

                    # save saturation profile data
                    table_data.save(satprof_datafile, sat_data, verbose)

                    # save grid data
                    if grid_output:
                        grid_data = self.read_grid_block_data(
                            experiment, project_name, wdir, verbose=verbose, **kwargs
                        )
                        self.save_grid_data(
                            experiment, vtu_folder, grid_data, verbose=verbose, **kwargs
                        )

                # plot solution, average saturation and cumulative production vs. time
                # plot the difference = solution - observed data
                # plot saturation profile at last step
                if os_utils.check_file(sol_datafile):
                    # self.plot_results(experiment,
                    #     sat_data,
                    #     sol_datafile,soldiff_datafile,sol_dataplot,soldiff_dataplot,
                    #     prod_dataplot,swat_dataplot,satprof_dataplot,
                    #     plot_soldiff = False,
                    #     plot_with = plot_with,
                    #     verbose = verbose, **kwargs)
                    pass

            elif experiment_name == "CENT":
                if grid_output:
                    grid_data = GridBlockData(**kwargs)

                for stage in range(0, num_datafiles):
                    stage_project_name = project_name + str(stage)

                    # run simulator
                    if verbose:
                        print("\ninjection stage = ", stage, " ...")
                    t0 = time.process_time()
                    deck.run_simulator(
                        basedir, simdir, stage_project_name, verbose, **kwargs
                    )
                    if verbose:
                        print(
                            "\nit took",
                            time.process_time() - t0,
                            "seconds to perform the simulation",
                        )

                    # read solution
                    data_temp = deck.read_solution(
                        wdir,
                        stage_project_name,
                        num_wgnames,
                        num_nums,
                        obsdata_keywords,
                        obsdata_type,
                        obsdata_wgnames,
                        obsdata_nums,
                        obsdata_convfactors,
                        verbose,
                    )
                    for k in range(0, len(data_temp)):
                        data.append(data_temp[k])
                    del data_temp

                    # read saturation profile data
                    sat_data_temp = deck.read_solution(
                        wdir,
                        stage_project_name,
                        int(0),
                        len(satprof_nums),
                        satprof_keywords,
                        satprof_type,
                        satprof_wgnames,
                        satprof_nums,
                        satprof_convfactors,
                        verbose,
                    )
                    for k in range(0, len(sat_data_temp)):
                        sat_data.append(sat_data_temp[k])

                    if len(data) != 0:
                        # save data
                        table_data.save(sol_datafile, data, verbose)

                        # save saturation profile data
                        # satprof_header = ''
                        # if( flooding == 'imbibition' ):
                        #    satprof_header = 'water saturation'
                        # elif( flooding == 'drainage' ):
                        #    satprof_header = 'oil saturation'
                        table_data.save(satprof_datafile, sat_data_temp, verbose)

                    # plot solution, average saturation and cumulative production vs. time
                    # plot the difference = solution - observed data
                    # plot saturation profile at last step
                    if os_utils.check_file(sol_datafile):
                        self.plot_results(
                            experiment,
                            sat_data_temp,
                            sol_datafile,
                            soldiff_datafile,
                            sol_dataplot,
                            soldiff_dataplot,
                            prod_dataplot,
                            swat_dataplot,
                            satprof_dataplot,
                            plot_soldiff=False,
                            plot_with=plot_with,
                            verbose=verbose,
                            **kwargs,
                        )

                    del sat_data_temp

                    # read grid data
                    if grid_output:
                        stage_grid_data = self.read_grid_block_data(
                            experiment,
                            stage_project_name,
                            wdir,
                            verbose=verbose,
                            **kwargs,
                        )
                        grid_data.append(stage_grid_data, verbose=verbose, **kwargs)
                        del stage_grid_data

                if len(data) != 0:
                    # save data
                    # table_data.save( sol_datafile, data, verbose )

                    # save saturation profile data
                    table_data.save(satprof_datafile, sat_data, verbose)

                    # save grid data
                    if grid_output:
                        self.save_grid_data(
                            experiment, vtu_folder, grid_data, verbose=verbose, **kwargs
                        )
        else:
            if verbose:
                print("\nReading solution file!")

            data = table_data.load(sol_datafile, verbose)
            sat_data = table_data.load(satprof_datafile, verbose)

        # calculate RMS
        if len(data) != 0:
            # table_data.save( sol_datafile, data, verbose )
            (
                current_total_rms,
                current_total_rms_prime,
                current_rms,
                data_diff,
            ) = math_tools.calc_rms(
                data, ref_data, obsdata_id, obsdata_weights, default_rms, verbose
            )
            table_data.save(soldiff_datafile, data_diff[0], verbose)

        # write rms
        math_tools.write_rms(
            rmsfile, current_total_rms, current_rms, parameters, verbose
        )

        if verbose:
            output_text = "\nrms = " + str(current_total_rms)
            print(output_text)

        output_text = "run:\trms = " + str(current_total_rms) + sim_key
        fout = open(simfilename, "a")
        fout.writelines([output_text, "\n"])
        fout.close()

        # write parameters file
        fout = open(paramsfile, "a")
        fout.writelines([sim_key, "\n"])
        fout.close()

        if verbose:
            if isinstance(current_rms, list):
                for k in range(0, len(current_rms)):
                    output_text = (
                        "\nobserved data["
                        + str(k)
                        + "]:\ttotal_rms = "
                        + str(float(current_rms[k][0]))
                    )
                    print(output_text)
                    for l in range(1, len(current_rms[k])):
                        output_text = (
                            "\ndata set["
                            + str(l)
                            + "] : rms = "
                            + str(current_rms[k][l])
                        )
                        print(output_text)
            else:
                output_text = (
                    "\nobserved data["
                    + str(0)
                    + "]:\ttotal_rms = "
                    + str(float(current_rms))
                )
                print(output_text)
                output_text = "\ndata set[" + str(0) + "] : rms = " + str(current_rms)
                print(output_text)

        # plot krw and kro
        if (current_total_rms != default_rms) and (os_utils.check_file(swof_datafile)):
            sat_funcs.swof_plot(
                swof_datafile,
                swof_dataplot,
                pc_dataplot,
                analyt_relperms,
                analyt_cappress,
                verbose,
                plot_with=plot_with,
            )

        # plot solution, average saturation and cumulative production vs. time
        # plot the difference = solution - observed data
        # plot saturation profile at last step
        if (current_total_rms != default_rms) and (
            os_utils.check_file(sol_datafile) == True
        ):
            self.plot_results(
                experiment,
                sat_data,
                sol_datafile,
                soldiff_datafile,
                sol_dataplot,
                soldiff_dataplot,
                prod_dataplot,
                swat_dataplot,
                satprof_dataplot,
                plot_soldiff=True,
                plot_with=plot_with,
                verbose=verbose,
                **kwargs,
            )

        del data
        del data_diff

        total_rms.append([int(simulation_index), float(current_total_rms)])

        return current_total_rms

    # read grid block data
    def read_grid_block_data(
        self,
        experiment: ScalExperiment,
        project_name: str,
        wdir: str,
        verbose: bool = False,
        **kwargs,
    ) -> GridBlockData:
        # define block properties
        sw_keywords = experiment.SimulationOutputData.Sw.Keyword
        sw_type = experiment.SimulationOutputData.Sw.Type
        sw_wgnames = experiment.SimulationOutputData.Sw.Wgname
        sw_nums = experiment.SimulationOutputData.Sw.Num
        sw_convfactors = experiment.SimulationOutputData.Sw.UnitConversionFactor

        so_keywords = experiment.SimulationOutputData.So.Keyword
        so_type = experiment.SimulationOutputData.So.Type
        so_wgnames = experiment.SimulationOutputData.So.Wgname
        so_nums = experiment.SimulationOutputData.So.Num
        so_convfactors = experiment.SimulationOutputData.So.UnitConversionFactor

        pw_keywords = experiment.SimulationOutputData.Pw.Keyword
        pw_type = experiment.SimulationOutputData.Pw.Type
        pw_wgnames = experiment.SimulationOutputData.Pw.Wgname
        pw_nums = experiment.SimulationOutputData.Pw.Num
        pw_convfactors = experiment.SimulationOutputData.Pw.UnitConversionFactor

        po_keywords = experiment.SimulationOutputData.Po.Keyword
        po_type = experiment.SimulationOutputData.Po.Type
        po_wgnames = experiment.SimulationOutputData.Po.Wgname
        po_nums = experiment.SimulationOutputData.Po.Num
        po_convfactors = experiment.SimulationOutputData.Po.UnitConversionFactor

        pc_keywords = experiment.SimulationOutputData.Pcow.Keyword
        pc_type = experiment.SimulationOutputData.Pcow.Type
        pc_wgnames = experiment.SimulationOutputData.Pcow.Wgname
        pc_nums = experiment.SimulationOutputData.Pcow.Num
        pc_convfactors = experiment.SimulationOutputData.Pcow.UnitConversionFactor

        # read grid block data
        grid_data = GridBlockData(**kwargs)
        grid_data.Sw = deck.read_solution(
            wdir,
            project_name,
            int(0),
            len(sw_nums),
            sw_keywords,
            sw_type,
            sw_wgnames,
            sw_nums,
            sw_convfactors,
            verbose,
        )
        grid_data.So = deck.read_solution(
            wdir,
            project_name,
            int(0),
            len(so_nums),
            so_keywords,
            so_type,
            so_wgnames,
            so_nums,
            so_convfactors,
            verbose,
        )
        grid_data.Pw = deck.read_solution(
            wdir,
            project_name,
            int(0),
            len(pw_nums),
            pw_keywords,
            pw_type,
            pw_wgnames,
            pw_nums,
            pw_convfactors,
            verbose,
        )
        grid_data.Po = deck.read_solution(
            wdir,
            project_name,
            int(0),
            len(po_nums),
            po_keywords,
            po_type,
            po_wgnames,
            po_nums,
            po_convfactors,
            verbose,
        )
        grid_data.Pcow = deck.read_solution(
            wdir,
            project_name,
            int(0),
            len(pc_nums),
            pc_keywords,
            pc_type,
            pc_wgnames,
            pc_nums,
            pc_convfactors,
            verbose,
        )
        return grid_data

    # save observed data to '.vtu' files
    def save_grid_data(
        self,
        experiment: ScalExperiment,
        vtu_folder: str,
        grid_data: GridBlockData,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        # project name
        project_name = experiment.ProjectSetupData.ProjectName
        # experiment name
        experiment_name = experiment.ProjectSetupData.ExperimentName
        # grid data
        pxyz = experiment.GridData.Pxyz
        cell_points = experiment.GridData.CellPoints
        cells = experiment.GridData.Cells
        core_cells = experiment.GridData.CoreCells
        outside_cells = experiment.GridData.OutsideCells
        # save grid data
        is_time_data = True
        full_name_props = GridBlockData.get_full_property_names(
            verbose=verbose, **kwargs
        )
        for prop in GridBlockData.get_property_names(verbose=verbose, **kwargs):
            propertyname = full_name_props[prop]
            grid_data_file = os.path.join(vtu_folder, project_name + "_VTU_" + prop)
            if verbose:
                print(f"Saving {propertyname} VTU files ... ")
            prop_data = getattr(grid_data, prop)
            table_data.save_data_to_vtk_file(
                grid_data_file + "_grid",
                experiment_name,
                propertyname,
                pxyz,
                cell_points,
                cells,
                prop_data,
                is_time_data,
                verbose,
            )
            table_data.save_data_to_vtk_file(
                grid_data_file + "_grid_core",
                experiment_name,
                propertyname,
                pxyz,
                cell_points,
                core_cells,
                prop_data,
                is_time_data,
                verbose,
            )
            table_data.save_data_to_vtk_file(
                grid_data_file + "_grid_outside",
                experiment_name,
                propertyname,
                pxyz,
                cell_points,
                outside_cells,
                prop_data,
                is_time_data,
                verbose,
            )

    # save observed data to '.graf' file
    def save_graf_file(
        self, experiment: ScalExperiment, verbose: bool = False, **kwargs
    ) -> None:
        # experiment name
        experiment_name = experiment.ProjectSetupData.ExperimentName
        # flooding type
        flooding = experiment.ProjectSetupData.FloodingType
        # project name
        project_name = experiment.ProjectSetupData.ProjectName

        # get simulator control and observed data
        # time data
        # time_data = experiment.ProjectSetupData.TimeData
        # reference data
        # SS, USS: pressure difference vs. time
        # CENT: oil/water produxtion vs. time
        ref_data = experiment.ProjectSetupData.ReferenceData
        # ref_data_vec = experiment.ProjectSetupData.ReferenceDataVector
        # simulator control data
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        # simcontrol_data = experiment.ProjectSetupData.SimulationControlData
        # simcontrol_data_vec = experiment.ProjectSetupData.SimulationControlDataVector

        # save observed data in '*.graf' format
        obs_graffile = experiment.ProjectSetupData.ObservedGraffile
        if (experiment_name == "SS") or (experiment_name == "USS"):
            mnemonis = ["TIME", "WBHP"]
            units = ["HOURS", "ATMOSA"]
            well_or_group_name = "INJ"
            dp_data = []
            for i in range(0, len(ref_data)):
                dp_data.append([])
                for j in range(0, len(ref_data[i])):
                    dp_data[i].append([])
                    dp_data[i][j].append(np.float64(ref_data[i][j][0]))
                    dp_data[i][j].append(
                        np.float64(ref_data[i][j][1]) * UnitsConverter.bar2atm
                    )
            table_data.save_graf_file(
                obs_graffile,
                project_name,
                dp_data,
                mnemonis,
                units,
                well_or_group_name,
                0,
                1,
                verbose,
            )
            del dp_data
        elif experiment_name == "CENT":
            # save observed data to '*.graf' format
            # @TODO: create universal approach
            # ECLIPSE:
            mnemonics = ["TIME", "RWFT"]
            # OPM:
            # FOFT( field water flow total )
            # mnemonics = [ 'TIME', 'FWFT' ]
            if flooding == "imbibition":
                # @TODO: create universal approach
                # ECLIPSE:
                # ROFTL( interregion oil flow total - liquid phase)
                # mnemonics = [ 'TIME', 'ROFTL' ]
                # ROFT( interregion oil flow total - liquid and wet gas phase)
                mnemonics = ["TIME", "ROFT"]
                # OPM:
                # FOFT( field oil flow total )
                # mnemonics = [ 'TIME', 'FOFT' ]
            units = ["HOURS", "SCC"]
            well_or_group_name = "PROD"
            table_data.save_graf_file(
                obs_graffile,
                project_name,
                ref_data,
                mnemonics,
                units,
                well_or_group_name,
                0,
                1,
                verbose,
            )

    # plot observed data
    def plot_observed_data(
        self,
        experiment: ScalExperiment,
        plot_with: str = None,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        return self.plot_results(
            experiment,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            plot_soldiff=False,
            plot_observed_data=True,
            plot_with=plot_with,
            verbose=verbose,
            **kwargs,
        )

    # plot results
    def plot_results(
        self,
        experiment: ScalExperiment,
        sat_data: List,
        sol_datafile: str,
        soldiff_datafile: str,
        sol_dataplot: str,
        soldiff_dataplot: str,
        prod_dataplot: str,
        swat_dataplot: str,
        satprof_dataplot: str,
        plot_soldiff: bool = False,
        plot_observed_data: bool = False,
        plot_with: str = None,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        # experiment name
        experiment_name = experiment.ProjectSetupData.ExperimentName
        # flooding type
        flooding = experiment.ProjectSetupData.FloodingType
        # simulator control data file
        simcontrol_datafile = experiment.ProjectSetupData.SimulationControlDatafile
        simcontrol_plotfile = experiment.ProjectSetupData.SimulationControlPlotfile
        # observed data file
        obs_datafile = experiment.ProjectSetupData.ObservedDatafile
        obs_plotfile = experiment.ProjectSetupData.ObservedPlotfile
        # initial pressure
        pressure_init = experiment.ProjectSetupData.PressInit
        # duration time
        duration_time = experiment.ProjectSetupData.DurationTime
        # distance to inlet
        distance_to_inlet = experiment.CoreSampleData.DistanceToInlet
        # radius center
        radius_centre = experiment.CoreSampleData.RadiusCentre

        # get simulator control and observed data
        # time data
        time_data = experiment.ProjectSetupData.TimeData
        # reference data
        # SS, USS: pressure difference vs. time
        # CENT: oil/water produxtion vs. time
        ref_data = experiment.ProjectSetupData.ReferenceData
        ref_data_vec = experiment.ProjectSetupData.ReferenceDataVector
        # simulator control data
        # SS, USS: oil/water injection rate vs. time
        # CENT: centrifuge acceleration vs. time
        simcontrol_data = experiment.ProjectSetupData.SimulationControlData
        simcontrol_data_vec = experiment.ProjectSetupData.SimulationControlDataVector
        num_obs_cols = experiment.ProjectSetupData.NumObservationColumns

        # plot settings
        solution_name = experiment.PlotSettingsData.Name
        solution_xlabel = experiment.PlotSettingsData.Xlabel
        solution_ylabel = experiment.PlotSettingsData.Ylabel
        solution_xmin = experiment.PlotSettingsData.Xmin
        solution_xmax = experiment.PlotSettingsData.Xmax
        solution_ymin = experiment.PlotSettingsData.Ymin
        solution_ymax = experiment.PlotSettingsData.Ymax
        xref = experiment.PlotSettingsData.Xref
        yref = experiment.PlotSettingsData.Yref
        sat_avg = experiment.PlotSettingsData.Savg
        qprod_avg = experiment.PlotSettingsData.Qprod
        num_sw_points = experiment.PlotSettingsData.NumSatPoints

        # objective function data
        obsdata_weights = experiment.ObjectiveFunctionData.Weight
        obsdata_id = experiment.ObjectiveFunctionData.ReferenceId
        prod_id = experiment.ObjectiveFunctionData.ObservationIds[
            ObjectiveFunction.Qprod
        ]
        sat_id = experiment.ObjectiveFunctionData.ObservationIds[ObjectiveFunction.Savg]

        # observation data keywords
        obsdata_keywords = experiment.SimulationOutputData.ProductionData.Keyword
        obsdata_type = experiment.SimulationOutputData.ProductionData.Type
        obsdata_wgnames = experiment.SimulationOutputData.ProductionData.Wgname
        obsdata_nums = experiment.SimulationOutputData.ProductionData.Num
        obsdata_convfactors = (
            experiment.SimulationOutputData.ProductionData.UnitConversionFactor
        )
        # num_wgnames         = experiment.SimulationOutputData.ProductionData.WgnamesLen
        # num_nums            = experiment.SimulationOutputData.ProductionData.NumsLen

        # saturation profile keywords
        # satprof_keywords    = experiment.SimulationOutputData.SaturationProfile.Keyword
        # satprof_type        = experiment.SimulationOutputData.SaturationProfile.Type
        # satprof_wgnames     = experiment.SimulationOutputData.SaturationProfile.Wgname
        # satprof_nums        = experiment.SimulationOutputData.SaturationProfile.Num
        # satprof_weights     = experiment.SimulationOutputData.SaturationProfile.Wgname
        # satprof_convfactors = experiment.SimulationOutputData.SaturationProfile.UnitConversionFactor

        # grid data
        num_grid_blocks = experiment.GridData.NumGridBlocks
        dx_c = experiment.GridData.DxC

        phases = {
            "oil": {"name": "oil"},
            "water": {"name": "water"},
            "gas": {"name": "gas"},
        }

        if plot_observed_data:
            # output simulation characteristics
            last_section = len(time_data) - 1
            last_entry = len(time_data[last_section]) - 1
            if verbose:
                print(
                    "\nDuration time = ",
                    time_data[last_section][last_entry],
                    "[ hours ]",
                )

            # plot schedule
            if experiment_name in {"SS", "USS"}:
                # plot injection rates ( control ) data
                simcontrol_data_array = np.asarray(simcontrol_data_vec.copy())
                t = simcontrol_data_array[:, 0]
                qtot = simcontrol_data_array[:, 1]
                phase1 = phases["oil"]
                phase2 = phases["water"]
                phase1["values"] = simcontrol_data_array[:, 2]
                phase2["values"] = simcontrol_data_array[:, 3]
                for i in range(0, len(qtot)):
                    phase1["values"][i] *= np.float64(qtot[i] / 100.0)
                    phase2["values"][i] *= np.float64(qtot[i] / 100.0)
                plt.plot_injection(
                    t,
                    (
                        dict(
                            values=phase1["values"],
                            name=phase1["name"],
                            tags=phase1["name"],
                        ),
                        dict(
                            values=phase2["values"],
                            name=phase2["name"],
                            tags=phase2["name"],
                        ),
                    ),
                    experiment_name=experiment_name,
                    flooding=flooding,
                    image_file=simcontrol_plotfile,
                    plot_with=plot_with,
                    **kwargs,
                )
                del t, qtot, phase1["values"], phase2["values"]

                # plot pressure
                plt.plot_pressure(
                    xref,
                    dict(
                        values=yref,
                        name="pressure",
                        tags="ref",
                    ),
                    experiment_name=experiment_name,
                    flooding=flooding,
                    image_file=obs_plotfile,
                    plot_with=plot_with,
                    **kwargs,
                )
                if num_obs_cols > 1:
                    plt.plot_saturation(
                        xref,
                        dict(
                            values=sat_avg,
                            name="saturation",
                            tags="ref",
                        ),
                        experiment_name=experiment_name,
                        flooding=flooding,
                        image_file=None,
                        plot_with=plot_with,
                        **kwargs,
                    )
                if num_obs_cols > 2:
                    plt.plot_production(
                        xref,
                        dict(
                            values=qprod_avg,
                            name="production",
                            tags="ref",
                        ),
                        experiment_name=experiment_name,
                        flooding=flooding,
                        image_file=None,
                        plot_with=plot_with,
                        **kwargs,
                    )

            elif experiment_name in {"CENT"}:
                # plot centrifuge acceleration ( control ) data
                simcontrol_data_array = np.asarray(simcontrol_data_vec.copy())
                t = simcontrol_data_array[:, 0]
                acc = simcontrol_data_array[:, 1]
                plt.plot_acceleration(
                    t,
                    dict(
                        values=acc,
                        name="acceleration",
                    ),
                    experiment_name=experiment_name,
                    flooding=flooding,
                    image_file=simcontrol_plotfile,
                    plot_with=plot_with,
                    **kwargs,
                )
                del t, acc
                # # convert from m/s/s to cm2*atm/gm
                # for i in range ( 0, len( simcontrol_data ) ):
                #     simcontrol_data[i][0][0] *= ( distance_to_inlet/radius_centre )
                #     simcontrol_data[i][0][0] *= UnitsConverter.cm2atmpergm
                #     simcontrol_data[i][0][0] = round( simcontrol_data[i][0][0], 6 )

                # plot production ( observed ) data
                plt.plot_production(
                    xref,
                    dict(
                        values=yref,
                        name="production",
                        tags="ref",
                    ),
                    experiment_name=experiment_name,
                    flooding=flooding,
                    image_file=None,
                    plot_with=plot_with,
                    **kwargs,
                )

                # plot average saturation ( observed ) data
                if num_obs_cols > 1:
                    plt.plot_saturation(
                        xref,
                        dict(
                            values=sat_avg,
                            name="saturation",
                            tags="ref",
                        ),
                        experiment_name=experiment_name,
                        flooding=flooding,
                        image_file=None,
                        plot_with=plot_with,
                        **kwargs,
                    )

            # del simcontrol_data_vec
            # del ref_data_vec
        else:
            # plot solution, average saturation and cumulative production vs. time
            if os_utils.check_file(sol_datafile):
                # read solution and average saturation
                sol_data = np.loadtxt(sol_datafile)
                if sol_data.ndim > 1:
                    xsol = sol_data[:, 0]
                    ysol = sol_data[:, obsdata_id[0]]
                    sat = sol_data[:, sat_id]

                    # plot cumulative production data
                    Qprod = sol_data[:, prod_id] if (prod_id != 1) else np.empty(0)
                    if Qprod.size > 0:
                        prod_traces = (
                            (
                                xsol,
                                dict(
                                    values=Qprod,
                                    name="calculated",
                                ),
                            ),
                        )
                    else:
                        prod_traces = ()
                    if qprod_avg.size > 1:
                        prod_traces += (
                            (
                                xref,
                                dict(
                                    values=qprod_avg,
                                    name="observed",
                                    tags="ref",
                                ),
                            ),
                        )
                    plt.plot_production(
                        prod_traces,
                        experiment_name=experiment_name,
                        flooding=flooding,
                        xaxis_title=solution_xlabel,
                        xaxis_range=(solution_xmin, solution_xmax),
                        image_file=prod_dataplot,
                        plot_with=plot_with,
                        **kwargs,
                    )
                    # plot average saturation
                    sat_traces = (
                        (
                            xsol,
                            dict(
                                values=sat,
                                name="calculated",
                            ),
                        ),
                    )
                    if sat_avg.size > 1:
                        sat_traces += (
                            (
                                xref,
                                dict(
                                    values=sat_avg,
                                    name="observed",
                                    tags="ref",
                                ),
                            ),
                        )
                    plt.plot_saturation(
                        sat_traces,
                        experiment_name=experiment_name,
                        flooding=flooding,
                        xaxis_title=solution_xlabel,
                        yaxis_title="saturation",
                        xaxis_range=(solution_xmin, solution_xmax),
                        yaxis_range=(-0.1, 1.1),
                        image_file=swat_dataplot,
                        plot_with=plot_with,
                        **kwargs,
                    )

                    if verbose:
                        print(
                            "\nAverage water saturation at t = ",
                            xsol[len(xsol) - 1],
                            " : Sw(avg) = ",
                            sat[len(sat) - 1],
                        )

                    # plot solution
                    sol_traces = (
                        (
                            xsol,
                            dict(
                                values=ysol,
                                name="calculated",
                            ),
                        ),
                        (
                            xref,
                            dict(
                                values=yref,
                                name="observed",
                                tags="ref",
                            ),
                        ),
                    )
                    plt.plot_solution(
                        sol_traces,
                        title=f"observed vs. calculated {solution_name}",
                        xaxis_title=solution_xlabel,
                        yaxis_title=solution_ylabel,
                        xaxis_range=(solution_xmin, solution_xmax),
                        image_file=sol_dataplot,
                        plot_with=plot_with,
                        **kwargs,
                    )
                    del sol_data
                    del xsol
                    del ysol
                    del sat
                    del Qprod

            # plot residual = solution - observed data
            if plot_soldiff and os_utils.check_file(sol_datafile):
                sol_data_diff = np.loadtxt(soldiff_datafile)
                if sol_data_diff.ndim > 1:
                    xsol_diff = sol_data_diff[:, 0]
                    ysol_diff = sol_data_diff[:, 1]
                    sol_diff_traces = (
                        xsol_diff,
                        dict(
                            values=ysol_diff,
                            name="calculated",
                        ),
                    )
                    plt.plot_solution(
                        sol_diff_traces,
                        title=f"( calculated - observed ) {solution_name}",
                        xaxis_title=solution_xlabel,
                        yaxis_title=solution_ylabel,
                        xaxis_range=(solution_xmin, solution_xmax),
                        yaxis_range=(-1, 1),
                        image_file=soldiff_dataplot,
                        plot_with=plot_with,
                        **kwargs,
                    )
                    del sol_data_diff
                    del xsol_diff
                    del ysol_diff

            # plot saturation profile at last step
            if os_utils.check_file(sol_datafile):
                # read solution and average saturation
                num_grid_blocks = len(dx_c)
                num_time_outputs = len(sat_data)
                Sprof = np.empty([num_grid_blocks, 1])
                for i in range(0, num_grid_blocks):
                    Sprof[i] = sat_data[num_time_outputs - 1][i + 1]
                # if(verbose):
                #     print( '\nXsol = ', dxC )
                #     print( '\nYsol = ', Ysol )

                sat_profile_trace = (
                    dx_c,
                    dict(
                        values=Sprof,
                        name="saturation profile",
                    ),
                )
                sat_profile_title = ""
                if flooding == "imbibition":
                    sat_profile_title = "water saturation profile"
                elif flooding == "drainage":
                    sat_profile_title = "oil saturation profile"
                sat_profile_title += (
                    f" at t = {str(sat_data[num_time_outputs - 1][0])} h"
                )
                plt.plot_saturation_profile(
                    sat_profile_trace,
                    experiment_name=experiment_name,
                    flooding=flooding,
                    title=sat_profile_title,
                    image_file=satprof_dataplot,
                    plot_with=plot_with,
                    **kwargs,
                )
                del Sprof
