import numpy as np
import scipy as sp
from math import floor

from coreflow.io import table_data, math_tools
from coreflow.io.plotting import Plot as plt

eclipse_precision = int(4)


def sat_out_of_range(SW, SOWCR, SWL):
    if (SW < SWL) or (SW > 1.0 - SOWCR):
        return True
    else:
        return False


# ===========================================================================
#             capillary pressure functions
# ===========================================================================


def pc_corey(SW, SOWCR, SWLPC, SWI, PD, CP):
    # Brooks-Corey( 1964 ) ( oil-water ) capillary pressure
    # CP   -   - Corey's capillary pressure exponent
    # SWL(Swc) - connate(irreducible) water saturation
    # SOWCR    - critial oil in water saturation
    # PD       - displacement( entry ) pressure
    # PCMAX    - maximum capillary pressure

    # effective saturation
    Sweff = (SW - SWLPC) / (1.0 - SWLPC - SOWCR)

    # define max pressure
    Sweffi = (SWI - SWLPC) / (1.0 - SWLPC - SOWCR)
    pswi = pow(Sweffi, CP)
    PCMAX = np.float64(PD * pswi / (1.0 - pswi))
    PS = np.float64(PD - PCMAX)

    # pc = po-pw- capillary pressure between oil and water phases
    if SW <= SWLPC:
        pc = PCMAX
    elif SW < (1.0 - SOWCR):
        pc = PS * pow(Sweff, CP) + PCMAX
    else:
        pc = PD

    return pc


def pc_corey_modified(SW, SOWCR, SWLPC, SWI, PCMIN, PCMAX, SOD, SWD, POD, PWD, CO, CW):
    # Modified Corey
    # CW   -   - Corey's oil capillary pressure exponent
    # CO   -   - Corey's water capillary pressure exponent
    # AW   -   - Corey's oil capillary pressure amplitude
    # AO   -   - Corey's water capillary pressure amplitude
    # SWL(Swc) - connate(irreducible) water saturation
    # SOWCR    - critial oil in water saturation
    # SWD      - water domain saturation
    # SOD      - oil domian saturation
    # PWD      - water domain capillary pressure
    # POD      - oil domian capillary pressure
    # PCMIN    - minimum capillary pressure
    # PCMAX    - maximum capillary pressure
    # bi       - linear domain offset
    # ri       - linear domain slope

    # define PCMAX ( if we have swi information )
    if (SWD == SWI) or (PWD == 0.0) or (SWI == SWLPC) or (SWD == SWLPC):
        PCMAX = np.float64(0.0)
    elif (SWI != 0.0) and (SWD != SWI) and (PWD != 0.0):
        Soeffi = np.float64((SWD - SWI) / (SWD - SWLPC))
        PCMAX = np.float64(PWD * (1.0 - (1.0 / pow(Soeffi, CW))))

    # pc = po-pw- capillary pressure between oil and water phases
    if SW == SWD:
        pc = np.float64(PWD)
    elif SW == SOD:
        pc = np.float64(POD)
    elif (SW > SWD) and (SW < SOD) and (SWD != SOD):
        ri = np.float64((PWD - POD) / (SWD - SOD))
        bi = np.float64((POD * SWD - PWD * SOD) / (SWD - SOD))
        pc = SW * ri + bi
    elif (SW > SWLPC) and (SW < SWD):
        # effective saturation
        Soeff = np.float64((SWD - SW) / (SWD - SWLPC))
        pc = np.float64((PCMAX - PWD) * pow(Soeff, CW) + PWD)
    elif SW <= SWLPC:
        pc = np.float64(PCMAX)
    elif SW >= (1.0 - SOWCR):
        pc = np.float64(PCMIN)
    elif (SW > SOD) and (SW < (1.0 - SOWCR)):
        # effective saturation
        Sweff = np.float64((SW - SOD) / (1.0 - SOD - SOWCR))
        pc = np.float64((PCMIN - POD) * pow(Sweff, CO) + POD)

    return pc


def pc_brooks_corey(SW, SOWCR, SWLPC, PD, Lambda):
    # Brooks-Corey( 1964 ) ( oil-water ) capillary pressure
    # Lambda   - Corey's capillary pressure exponent
    # SWL(Swc) - connate(irreducible) water saturation
    # SOWCR    - critial oil in water saturation
    # PD       - displacement( entry ) pressure

    # effective saturation
    Sweff = (SW - SWLPC) / (1.0 - SWLPC - SOWCR)
    dSw = 1.0e-3
    Swcreff = dSw / (1.0 - SWLPC - SOWCR)
    # pc = po-pw- capillary pressure between oil and water phases
    if SW <= (SWLPC + dSw):
        pc = PD * pow(Swcreff, -1.0 / Lambda)
    elif SW < (1.0 - SOWCR):
        pc = PD * pow(Sweff, -1.0 / Lambda)
    else:
        pc = PD

    return pc


# ===========================================================================
#             relative permeability functions
# ===========================================================================


def kr_corey(SW, SOWCR, SWL, CO, CW, KRO, KRW):
    # Corey's relative permebilities ( oil-water )
    # CO       - Corey's oil relative permeability exponent
    # CW       - Corey's water relative permeability exponent
    # Lambda   - Corey's capillary pressure exponent
    # SWL(Swc) - connate(irreducible) water saturation
    # SOWCR    - critial oil in water saturation
    # KRW      - water relative permeability at maximum water saturation
    # KRO      - oil relative permeability at connate water saturation

    # effective saturation
    Sweff = (SW - SWL) / (1.0 - SWL - SOWCR)

    # water relative permeability function
    if SW <= SWL:
        krw = float(0.0)
    elif SW <= 1.0 - SOWCR:
        krw = KRW * pow(Sweff, CW)
    else:
        krw = float(0.0)

    Soeff = (1.0 - SW - SOWCR) / (1.0 - SWL - SOWCR)

    # oil relative permeability function
    if SW < SWL:
        kro = float(0.0)
    elif SW < (1.0 - SOWCR):
        kro = KRO * pow(Soeff, CO)
    else:
        kro = float(0.0)

    return krw, kro


def kr_brooks_corey(SW, SOWCR, SWL, Lambda):
    # Brooks-Corey( 1964 ) ( oil-water ) relative permebilities
    # developed as an analytical solution from pc function
    # after Burdine( 1953 ) and Mualem( 1976 )
    # Lambda   - Brooks Corey parameter
    # SWL(Swc) - connate(irreducible) water saturation
    # SOWCR    - critial oil in water saturation

    # effective saturation
    Sweff = (SW - SWL) / (1.0 - SWL - SOWCR)

    # water relative permeability function
    if SW <= SWL:
        krw = float(0.0)
    elif SW < (1.0 - SOWCR):
        krw = pow(Sweff, 3.0 + 2.0 / Lambda)
    else:
        krw = float(1.0)

    # oil relative permeability function
    if SW <= SWL:
        kro = float(1.0)
    elif SW < (1.0 - SOWCR):
        kro = pow(1.0 - Sweff, 2.0) * (1.0 - pow(Sweff, 1.0 + 2.0 / Lambda))
    else:
        kro = float(0.0)

    return krw, kro


def kr_burdine_mualem(SW, pc_data):
    # sw = np.zeros( len( pc_data ) )
    # pc = np.zeros( len( pc_data ) )
    # for i in range( 0, len( pc_data ) ):
    #    sw[i] = pc_data[i][0]
    #    pc[i] = pc_data[i][1]

    def integrand(SW, data):
        pc = np.float64(math_tools.interpolate(SW, data, 0, 1, False))
        if pc == np.inf:
            res = np.float64(0.0)
        else:
            res = np.float64(1.0 / (pc * pc))
        return res

    sw_min = np.float64(pc_data[0][0])
    sw_max = np.float64(pc_data[len(pc_data) - 1][0])

    In = np.float64(0.0)
    Id = np.float64(0.0)
    InId = np.float64(0.0)
    if SW == sw_min:
        InId = np.float64(0.0)
    elif SW == sw_max:
        InId = np.float64(1.0)
    else:
        In, nerr = sp.integrate.quad(integrand, sw_min, SW, args=(pc_data))
        Id, derr = sp.integrate.quad(integrand, sw_min, sw_max, args=(pc_data))
        InId = In / Id

    se = (SW - sw_min) / (sw_max - sw_min)
    krw = np.float64((se**2) * InId)
    kro = np.float64(((1.0 - se) ** 2) * (1.0 - InId))

    return krw, kro


def kr_LET(SW, SOWCR, SWI, LO, EO, TO, LW, EW, TW, KRO, KRW):
    # Corey's relative permebilities ( oil-water )
    # LO,EO,TO - oil relative permeability shape parameters
    # LW,EW,TW - water relative permeability shape parameters
    # SWI      - initial water saturation
    # SOWCR    - critial oil in water saturation
    # KRW      - water relative permeability at maximum water saturation
    # KRO      - oil relative permeability at connate water saturation

    # normalized water saturation
    Swn = (SW - SWI) / (1.0 - SWI - SOWCR)

    # water relative permeability function
    if SW <= SWI:
        krw = float(0.0)
    elif SW <= 1.0 - SOWCR:
        krw = KRW * pow(Swn, LW) / (pow(Swn, LW) + EW * pow(1.0 - Swn, TW))
    else:
        krw = float(0.0)

    # oil relative permeability function
    if SW < SWI:
        kro = float(0.0)
    elif SW < (1.0 - SOWCR):
        kro = KRO * pow(1.0 - Swn, LO) / (pow(1.0 - Swn, LO) + EO * pow(Swn, TO))
    else:
        kro = float(0.0)

    return krw, kro


# ===========================================================================
#             table saturation functions
# ===========================================================================


def relperm_table_functions(SW, filename):
    data = []
    data = table_data.load(filename, False)
    krw = math_tools.interpolate(SW, data, 0, 1, False)
    kro = math_tools.interpolate(SW, data, 0, 2, False)

    del data

    return krw, kro


def pc_table_function(SW, filename):
    data = []
    data = table_data.load(filename, False)
    pc = math_tools.interpolate(SW, data, 0, 1, False)

    del data

    return pc


def swof_table_functions(SW, filename):
    data = []
    data = table_data.load(filename, False)
    krw = math_tools.interpolate(SW, data, 0, 1, False)
    kro = math_tools.interpolate(SW, data, 0, 2, False)
    pc = math_tools.interpolate(SW, data, 0, 3, False)

    del data

    return krw, kro, pc


# ===========================================================================
#             generic saturation functions
# ===========================================================================


def relperm_functions(SW, relperms, parameters, verbose):
    # relperms
    if relperms == "Corey":
        krw, kro = kr_corey(
            SW,
            parameters["SOWCR"],
            parameters["SWL"],
            parameters["CO"],
            parameters["CW"],
            parameters["KRO"],
            parameters["KRW"],
        )
    elif relperms == "Brooks-Corey":
        krw, kro = kr_brooks_corey(
            SW,
            parameters["SOWCR"],
            parameters["SWL"],
            parameters["SWCR"],
            parameters["Lambda"],
        )
    else:
        krw, kro = relperm_table_functions(SW, relperms)

    return krw, kro


def pc_function(SW, cappress, parameters, verbose):
    # capillary pressure
    if cappress == "Corey":
        pc = pc_corey(
            SW,
            parameters["SOWCR"],
            parameters["SWL"],
            parameters["SWI"],
            parameters["PD"],
            parameters["CP"],
        )
    elif cappress == "Corey-modified":
        pc = pc_corey_modified(
            SW,
            parameters["SOWCR"],
            parameters["SWL"],
            parameters["SWI"],
            parameters["PD"],
            parameters["PCMAX"],
            parameters["SOD"],
            parameters["SWD"],
            parameters["POD"],
            parameters["PWD"],
            parameters["COI"],
            parameters["CWI"],
        )
    elif cappress == "Brooks-Corey":
        pc = pc_brooks_corey(
            SW,
            parameters["SOWCR"],
            parameters["SWL"],
            parameters["PD"],
            parameters["Lambda"],
        )
    else:
        pc = pc_table_function(SW, cappress)

    return pc


def saturation_functions(SW, relperms, cappress, parameters, verbose):
    # relperms
    krw, kro = relperm_functions(SW, relperms, parameters, verbose)

    # capillary pressure
    pc = pc_function(SW, cappress, parameters, verbose)

    return krw, kro, pc


# ===========================================================================
#             saturation function parameters selection
# ===========================================================================


def select_params(
    relperms,
    cappress,
    parameters0,
    parameters0_min,
    parameters0_max,
    paramsprec0,
    paramopt0,
    verbose,
):
    parameters = {}
    parameters_min = {}
    parameters_max = {}
    paramsprec = {}
    paramopt = {}

    parameters["SOWCR"] = parameters0["SOWCR"]
    parameters_min["SOWCR"] = parameters0_min["SOWCR"]
    parameters_max["SOWCR"] = parameters0_max["SOWCR"]
    paramsprec["SOWCR"] = paramsprec0["SOWCR"]
    paramopt["SOWCR"] = paramopt0["SOWCR"]

    parameters["SWL"] = parameters0["SWL"]
    parameters_min["SWL"] = parameters0_min["SWL"]
    parameters_max["SWL"] = parameters0_max["SWL"]
    paramsprec["SWL"] = paramsprec0["SWL"]
    paramopt["SWL"] = paramopt0["SWL"]

    # relperms
    if relperms == "Corey":
        parameters["CO"] = parameters0["CO"]
        parameters_min["CO"] = parameters0_min["CO"]
        parameters_max["CO"] = parameters0_max["CO"]
        paramsprec["CO"] = paramsprec0["CO"]
        paramopt["CO"] = paramopt0["CO"]

        parameters["CW"] = parameters0["CW"]
        parameters_min["CW"] = parameters0_min["CW"]
        parameters_max["CW"] = parameters0_max["CW"]
        paramsprec["CW"] = paramsprec0["CW"]
        paramopt["CW"] = paramopt0["CW"]

        parameters["KRO"] = parameters0["KRO"]
        parameters_min["KRO"] = parameters0_min["KRO"]
        parameters_max["KRO"] = parameters0_max["KRO"]
        paramsprec["KRO"] = paramsprec0["KRO"]
        paramopt["KRO"] = paramopt0["KRO"]

        parameters["KRW"] = parameters0["KRW"]
        parameters_min["KRW"] = parameters0_min["KRW"]
        parameters_max["KRW"] = parameters0_max["KRW"]
        paramsprec["KRW"] = paramsprec0["KRW"]
        paramopt["KRW"] = paramopt0["KRW"]
    elif relperms == "Brooks-Corey":
        parameters["Lambda"] = parameters0["Lambda"]
        parameters_min["Lambda"] = parameters0_min["Lambda"]
        parameters_max["Lambda"] = parameters0_max["Lambda"]
        paramsprec["Lambda"] = paramsprec0["Lambda"]
        paramopt["Lambda"] = paramopt0["Lambda"]
    else:
        parameters["KRO"] = parameters0["KRO"]
        parameters_min["KRO"] = parameters0_min["KRO"]
        parameters_max["KRO"] = parameters0_max["KRO"]
        paramsprec["KRO"] = paramsprec0["KRO"]
        paramopt["KRO"] = paramopt0["KRO"]

        parameters["KRW"] = parameters0["KRW"]
        parameters_min["KRW"] = parameters0_min["KRW"]
        parameters_max["KRW"] = parameters0_max["KRW"]
        paramsprec["KRW"] = paramsprec0["KRW"]
        paramopt["KRW"] = paramopt0["KRW"]

    # capillary pressure
    if cappress == "Corey":
        parameters["SWI"] = parameters0["SWI"]
        parameters_min["SWI"] = parameters0_min["SWI"]
        parameters_max["SWI"] = parameters0_max["SWI"]
        paramsprec["SWI"] = paramsprec0["SWI"]
        paramopt["SWI"] = paramopt0["SWI"]

        parameters["CP"] = parameters0["CP"]
        parameters_min["CP"] = parameters0_min["CP"]
        parameters_max["CP"] = parameters0_max["CP"]
        paramsprec["CP"] = paramsprec0["CP"]
        paramopt["CP"] = paramopt0["CP"]

        parameters["PD"] = parameters0["PD"]
        parameters_min["PD"] = parameters0_min["PD"]
        parameters_max["PD"] = parameters0_max["PD"]
        paramsprec["PD"] = paramsprec0["PD"]
        paramopt["PD"] = paramopt0["PD"]

    elif cappress == "Corey-modified":
        parameters["SWI"] = parameters0["SWI"]
        parameters_min["SWI"] = parameters0_min["SWI"]
        parameters_max["SWI"] = parameters0_max["SWI"]
        paramsprec["SWI"] = paramsprec0["SWI"]
        paramopt["SWI"] = paramopt0["SWI"]

        parameters["PD"] = parameters0["PD"]
        parameters_min["PD"] = parameters0_min["PD"]
        parameters_max["PD"] = parameters0_max["PD"]
        paramsprec["PD"] = paramsprec0["PD"]
        paramopt["PD"] = paramopt0["PD"]

        parameters["PCMAX"] = parameters0["PCMAX"]
        parameters_min["PCMAX"] = parameters0_min["PCMAX"]
        parameters_max["PCMAX"] = parameters0_max["PCMAX"]
        paramsprec["PCMAX"] = paramsprec0["PCMAX"]
        paramopt["PCMAX"] = paramopt0["PCMAX"]

        parameters["CWI"] = parameters0["CWI"]
        parameters_min["CWI"] = parameters0_min["CWI"]
        parameters_max["CWI"] = parameters0_max["CWI"]
        paramsprec["CWI"] = paramsprec0["CWI"]
        paramopt["CWI"] = paramopt0["CWI"]

        parameters["COI"] = parameters0["COI"]
        parameters_min["COI"] = parameters0_min["COI"]
        parameters_max["COI"] = parameters0_max["COI"]
        paramsprec["COI"] = paramsprec0["COI"]
        paramopt["COI"] = paramopt0["COI"]

        parameters["PWD"] = parameters0["PWD"]
        parameters_min["PWD"] = parameters0_min["PWD"]
        parameters_max["PWD"] = parameters0_max["PWD"]
        paramsprec["PWD"] = paramsprec0["PWD"]
        paramopt["PWD"] = paramopt0["PWD"]

        parameters["POD"] = parameters0["POD"]
        parameters_min["POD"] = parameters0_min["POD"]
        parameters_max["POD"] = parameters0_max["POD"]
        paramsprec["POD"] = paramsprec0["POD"]
        paramopt["POD"] = paramopt0["POD"]

        parameters["SWD"] = parameters0["SWD"]
        parameters_min["SWD"] = parameters0_min["SWD"]
        parameters_max["SWD"] = parameters0_max["SWD"]
        paramsprec["SWD"] = paramsprec0["SWD"]
        paramopt["SWD"] = paramopt0["SWD"]

        parameters["SOD"] = parameters0["SOD"]
        parameters_min["SOD"] = parameters0_min["SOD"]
        parameters_max["SOD"] = parameters0_max["SOD"]
        paramsprec["SOD"] = paramsprec0["SOD"]
        paramopt["SOD"] = paramopt0["SOD"]

    elif cappress == "Brooks-Corey":
        parameters["Lambda"] = parameters0["Lambda"]
        parameters_min["Lambda"] = parameters0_min["Lambda"]
        parameters_max["Lambda"] = parameters0_max["Lambda"]
        paramsprec["Lambda"] = paramsprec0["Lambda"]
        paramopt["Lambda"] = paramopt0["Lambda"]

        parameters["PD"] = parameters0["PD"]
        parameters_min["PD"] = parameters0_min["PD"]
        parameters_max["PD"] = parameters0_max["PD"]
        paramsprec["PD"] = paramsprec0["PD"]
        paramopt["PD"] = paramopt0["PD"]

    # for key in parameters:
    #    if( parameters_min[key] == parameters_max[key] ):
    #        parameters[key] = parameters_min[key]

    return paramopt, parameters, parameters_min, parameters_max, paramsprec


def find_precision(x):
    prec = int(0)
    while x != round(x, prec):
        prec += 1

    return x, prec


def create_parameters_list(
    parameters, parameters_min, parameters_max, paramsprec, verbose
):
    num_combinations = 1
    par_vals = {}
    par_numb = {}
    for key in parameters:
        par_min = parameters_min[key]
        par_max = parameters_max[key]
        par_prec = float(paramsprec[key])

        par_set = set()
        par_set.add(par_min)
        par_set.add(par_max)

        # add values based on parameter precision
        if par_min == par_max:
            parameters[key] = par_min
        elif (par_prec != float(0.0)) and (par_min != par_max):
            par_round = math_tools.find_precision(par_prec)
            par_val = par_min
            while par_val < par_max:
                par_set.add(round(par_val, par_round))
                par_val += par_prec

        par_vals[key] = sorted(par_set)
        par_numb[key] = len(par_vals[key])
        num_combinations *= par_numb[key]
        del par_set

    # initialize parameters list
    parameters_list = [parameters.copy() for i in range(0, num_combinations)]

    # fill in parameters list
    num_cycles = 1.0
    previous_num_repeat = num_combinations
    for key in parameters:
        num_repeat = floor(previous_num_repeat / par_numb[key])
        num_cycles = floor(num_combinations / previous_num_repeat)
        index = 0
        for j in range(0, num_cycles):
            for i in range(0, par_numb[key]):
                for k in range(0, num_repeat):
                    parameters_list[index][key] = par_vals[key][i]
                    index += 1
        previous_num_repeat = num_repeat

    return parameters_list


# ===========================================================================
#             saturation function tables
# ===========================================================================


def write_relperms_table(
    filename, is_new_file, relperms, cappress, n, parameters, verbose
):
    # read history data
    if verbose:
        output_text = "Writing relperms table to file: " + filename
        print(output_text)

    # write data to file
    output_mode = "w"
    if not is_new_file:
        output_mode = "a"

    fout = open(filename, output_mode)

    # Loop over lines to extract variables of interest
    SW = 0.0
    dSW = 0.0
    dSW = (
        1.0 - np.float64(parameters["SOWCR"]) - np.float64(parameters["SWL"])
    ) / np.float64(n - 1)
    # dSW = ( float(parameters['SWU'])-float(parameters['SWL']))/float(n-1)

    if relperms != "Burdine-Mualem":
        for i in range(0, n):
            # new saturation value
            if i == n - 1:
                SW = np.float64(1.0 - parameters["SOWCR"])
                # SW = float(parameters['SWU'])
            else:
                SW = np.float64(parameters["SWL"]) + np.float64(i * dSW)

            krw, kro = relperm_functions(SW, relperms, parameters, verbose)

            # write data to file
            if i != 0:
                fout.writelines(["\n", str(SW), "\t", str(krw), "\t", str(kro)])
            else:
                fout.writelines([str(SW), "\t", str(krw), "\t", str(kro)])

    else:
        # calculate pc
        pc_data = []
        for i in range(0, n):
            # new saturation value
            if i == n - 1:
                SW = np.float64(1.0 - parameters["SOWCR"])
                # SW = float(parameters['SWU'])
            else:
                SW = np.float64(parameters["SWL"]) + np.float64(i * dSW)

            pc = pc_function(SW, cappress, parameters, verbose)

            pc_data.append([SW, pc])

        # calculate krw, kro and write data
        for i in range(0, n):
            krw, kro = kr_burdine_mualem(pc_data[i][0], pc_data)

            # write data to file
            if i != 0:
                fout.writelines(
                    ["\n", str(pc_data[i][0]), "\t", str(krw), "\t", str(kro)]
                )
            else:
                fout.writelines([str(pc_data[i][0]), "\t", str(krw), "\t", str(kro)])

    fout.close()

    if verbose:
        print(f"Finished writing relperms table to file: '{filename}'")


def write_pc_table(filename, is_new_file, relperms, cappress, n, parameters, verbose):
    # read history data
    if verbose:
        print(f"Writing capillary pressure table to file: '{filename}'")

    # write data to file
    output_mode = "w"
    if not is_new_file:
        output_mode = "a"

    fout = open(filename, output_mode)

    # Loop over lines to extract variables of interest
    SW = 0.0
    dSW = 0.0
    dSW = (
        1.0 - np.float64(parameters["SOWCR"]) - np.float64(parameters["SWL"])
    ) / np.float64(n - 1)
    # dSW = ( float(parameters['SWU'])-float(parameters['SWL']))/float(n-1)

    for i in range(0, n):
        # new saturation value
        if i == n - 1:
            SW = np.float64(1.0 - parameters["SOWCR"])
            # SW = float(parameters['SWU'])
        else:
            SW = np.float64(parameters["SWL"]) + np.float64(i * dSW)

        pc = pc_function(SW, cappress, parameters, verbose)

        # write data to file
        if i != 0:
            fout.writelines(["\n", str(SW), "\t", str(pc)])
        else:
            fout.writelines([str(SW), "\t", str(pc)])

    fout.close()

    if verbose:
        print(f"Finished writing capillary pressure table to file: '{filename}'")


def write_SWOF(filename, is_new_file, relperms, cappress, n, parameters, verbose):
    # convert from bar to atm
    bar2atm = np.float64(1.0e5 / 101325.0)

    # read history data
    if verbose:
        print(f"Writing SWOF table to file: '{filename}'")

    # write data to file
    output_mode = "w"
    if not is_new_file:
        output_mode = "a"

    fout = open(filename, output_mode)

    # Loop over lines to extract variables of interest
    SW = 0.0
    dSW = 0.0
    dSW = (
        1.0 - np.float64(parameters["SOWCR"]) - np.float64(parameters["SWL"])
    ) / np.float64(n - 1)
    # dSW = ( float(parameters['SWU'])-float(parameters['SWL']))/float(n-1)

    if relperms != "Burdine-Mualem":
        for i in range(0, n):
            # new saturation value
            if i == n - 1:
                SW = np.float64(1.0 - parameters["SOWCR"])
                # SW = float(parameters['SWU'])
            else:
                SW = np.float64(parameters["SWL"]) + np.float64(i * dSW)

            krw, kro, pc = saturation_functions(
                SW, relperms, cappress, parameters, verbose
            )

            # write data to file
            fout.writelines(
                [
                    "\n",
                    str(round(SW, eclipse_precision)),
                    "\t",
                    str(round(krw, eclipse_precision)),
                    "\t",
                    str(round(kro, eclipse_precision)),
                    "\t",
                    str(round(pc * bar2atm, eclipse_precision)),
                ]
            )

    else:
        # calculate pc
        pc_data = []
        for i in range(0, n):
            # new saturation value
            if i == n - 1:
                SW = np.float64(1.0 - parameters["SOWCR"])
                # SW = float(parameters['SWU'])
            else:
                SW = np.float64(parameters["SWL"]) + np.float64(i * dSW)

            pc = pc_function(SW, cappress, parameters, verbose)

            pc_data.append([SW, pc])

        # calculate krw, kro and write data
        for i in range(0, n):
            krw, kro = kr_burdine_mualem(pc_data[i][0], pc_data)

            # write data to file
            fout.writelines(
                [
                    "\n",
                    str(round(pc_data[i][0], eclipse_precision)),
                    "\t",
                    str(round(krw, eclipse_precision)),
                    "\t",
                    str(round(kro, eclipse_precision)),
                    "\t",
                    str(round(pc_data[i][1] * bar2atm, eclipse_precision)),
                ]
            )

    fout.close()

    if verbose:
        print(f"Finished writing SWOF table to file: '{filename}'")


def read_SWOF(filename, verbose):
    # convert from atm to bar
    atm2bar = np.float64(101325.0 / 1.0e5)
    #           sw   krw  kro  pc
    convfac = [1.0, 1.0, 1.0, atm2bar]

    data = []

    # read history data
    if verbose:
        print(f"Reading data from file: '{filename}'")

    # open input file
    fin = open(filename, "r")

    # Loop over lines to extract variables of interest
    for line in fin:
        # read line
        line = line.strip()
        line = line.replace(",", ".")
        columns = line.split()
        clen = len(columns)

        if clen != 0.0:
            if columns[0][0] == "/":
                break

            elif (columns[0] != "SWOF") and (columns[0][0] != "-"):
                row_data = []
                for i in range(0, clen):
                    if columns[i] != "/":
                        row_data.append(np.float64(columns[i]) * convfac[i])
                data.append(row_data)
                del row_data

    fin.close()

    if verbose:
        print(f"Finished reading data from file: '{filename}'")

    return data


# ===========================================================================
#             saturation functions plot
# ===========================================================================


def swof_plot(
    swof_datafile,
    swof_dataplot,
    pc_dataplot,
    analyt_relperms,
    analyt_cappress,
    verbose,
    plot_with: str = None,
):
    """
    Plot relative permeability and capillary pressure.
    """
    relperm_data = read_SWOF(swof_datafile, verbose)
    relperm_array = np.asarray(relperm_data)
    sw = relperm_array[:, 0]
    krw = relperm_array[:, 1]
    kro = relperm_array[:, 2]
    pc = relperm_array[:, 3]

    # plot relative permeabilities
    kr_traces = (
        (
            sw,
            dict(
                values=krw,
                name="krw",
                tags="water",
            ),
        ),
        (
            sw,
            dict(
                values=kro,
                name="kro",
                tags="oil",
            ),
        ),
    )
    if analyt_relperms != "empty":
        analyt_relperm_data = np.loadtxt(analyt_relperms)
        analyt_sw = analyt_relperm_data[:, 0]
        analyt_krw = analyt_relperm_data[:, 1]
        analyt_kro = analyt_relperm_data[:, 2]

        kr_traces += (
            (
                analyt_sw,
                dict(
                    values=analyt_krw,
                    name="krw (ref)",
                    tags={"water", "ref"},
                ),
            ),
            (
                analyt_sw,
                dict(
                    values=analyt_kro,
                    name="kro (ref)",
                    tags={"oil", "ref"},
                ),
            ),
        )
        del analyt_sw, analyt_krw, analyt_kro

    plt.plot_relperms(
        kr_traces,
        lin_scale=True,
        log_scale=True,
        image_file=swof_dataplot,
        plot_with=plot_with,
    )

    # plot capillary pressure
    pc_traces = (
        (
            sw,
            dict(
                values=pc,
                name="pc",
                tags={"oil", "water"},
            ),
        ),
    )
    if analyt_cappress != "empty":
        analyt_pc_data = np.loadtxt(analyt_cappress)
        analyt_sw = analyt_pc_data[:, 0]
        analyt_pc = analyt_pc_data[:, 1]
        pc_traces += (
            (
                analyt_sw,
                dict(
                    values=analyt_pc,
                    name="pc (ref)",
                    tags={"oil", "water", "ref"},
                ),
            ),
        )
        del analyt_pc_data, analyt_sw, analyt_pc

    plt.plot_pc(pc_traces, image_file=pc_dataplot, plot_with=plot_with)

    del relperm_array, relperm_data, sw, krw, kro, pc


# ===========================================================================
#             match saturation functions according to measured data
# ===========================================================================


def relperms_res(xarg, x, y, relperms, parameters, parameters_map, verbose):
    params = {}
    # assign new values to parameters
    for key in parameters.keys():
        if parameters_map[key] != -1:
            params[key] = xarg.flat[parameters_map[key]]
        else:
            params[key] = parameters[key]

    residual = np.zeros(x.size)
    num_points = floor(x.size / 2)
    for i in range(0, num_points):
        if not sat_out_of_range(x[i], parameters["SOWCR"], parameters["SWL"]):
            krw, kro = relperm_functions(x[i], relperms, params, verbose)
            residual[i] = krw - y[i]
            residual[i + num_points] = kro - y[i + num_points]

    return residual


def pc_res(xarg, x, y, cappress, parameters, parameters_map, verbose):
    params = {}
    # assign new values to parameters
    for key in parameters.keys():
        if parameters_map[key] != -1:
            params[key] = xarg.flat[parameters_map[key]]
        else:
            params[key] = parameters[key]

    residual = np.zeros(x.size)
    for i in range(0, x.size):
        if not sat_out_of_range(x[i], parameters["SOWCR"], parameters["SWL"]):
            pc = pc_function(x[i], cappress, params, verbose)
            residual[i] = pc - y[i]

    return residual


def optimize_satfunctions(
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
    # simulation output
    verbose,
):
    paramopt, parameters, parameters_min, parameters_max, paramsprec = select_params(
        relperms,
        cappress,
        parameters0,
        parameters0_min,
        parameters0_max,
        paramsprec0,
        paramopt0,
        verbose,
    )

    # optimze saturation functions
    empty_func = "empty"
    if (analyt_relperms != "empty") and optimize_relperms:
        analyt_relperm_data = np.loadtxt(analyt_relperms)
        analyt_sw = analyt_relperm_data[:, 0]
        analyt_krw = analyt_relperm_data[:, 1]
        analyt_kro = analyt_relperm_data[:, 2]
        x = np.empty(2 * analyt_sw.size)
        y = np.empty(2 * analyt_sw.size)
        for i in range(0, analyt_sw.size):
            x[i] = analyt_sw[i]
            x[i + analyt_sw.size] = analyt_sw[i]
            y[i] = analyt_krw[i]
            y[i + analyt_sw.size] = analyt_kro[i]
        del analyt_sw, analyt_krw, analyt_kro, analyt_relperm_data

        parameters_map = {}
        # initialize parameters map
        for key in sorted(parameters.keys()):
            parameters_map[key] = int(-1)

        # num_parameters = len( parameters )

        (
            relperm_paramopt,
            relperm_parameters,
            relperm_parameters_min,
            relperm_parameters_max,
            relperm_paramsprec,
        ) = select_params(
            relperms,
            empty_func,
            parameters,
            parameters_min,
            parameters_max,
            paramsprec,
            paramopt,
            verbose,
        )

        # create mapping [ parameters vs. arguments ]
        arg_map = []
        arg_index = int(0)
        for key in sorted(relperm_parameters.keys()):
            if relperm_paramopt[key]:
                arg_map.append(key)
                parameters_map[key] = arg_index
                arg_index += 1
        num_args = arg_index

        # define argument bounds
        if num_args > 0:
            parameters_min_bounds = []
            for i in range(0, num_args):
                parameters_min_bounds.append(parameters_min[arg_map[i]])
            parameters_max_bounds = []
            for i in range(0, num_args):
                parameters_max_bounds.append(parameters_max[arg_map[i]])
            parameters_bounds = (parameters_min_bounds, parameters_max_bounds)

            # initial guess
            xarg0 = np.empty([num_args])
            for key in sorted(parameters.keys()):
                if parameters_map[key] != -1:
                    xarg0[parameters_map[key]] = parameters[key]

            objfun_args = (x, y, relperms, parameters, parameters_map, verbose)

            del (
                relperm_paramopt,
                relperm_parameters,
                relperm_parameters_min,
                relperm_parameters_max,
                relperm_paramsprec,
            )

            resopt = sp.optimize.least_squares(
                relperms_res, xarg0, args=objfun_args, bounds=parameters_bounds
            )

            # assign new values to parameters
            for key in parameters.keys():
                if parameters_map[key] != -1:
                    parameters[key] = resopt.x.flat[parameters_map[key]]

    if (analyt_cappress != "empty") and optimize_cappress:
        analyt_pc_data = np.loadtxt(analyt_cappress)
        analyt_sw = analyt_pc_data[:, 0]
        analyt_pc = analyt_pc_data[:, 1]
        x = np.empty(analyt_sw.size)
        y = np.empty(analyt_sw.size)
        for i in range(0, analyt_sw.size):
            x[i] = analyt_sw[i]
            y[i] = analyt_pc[i]
        del analyt_sw, analyt_pc, analyt_pc_data

        parameters_map = {}
        # initialize parameters map
        for key in sorted(parameters.keys()):
            parameters_map[key] = int(-1)

        (
            pc_paramopt,
            pc_parameters,
            pc_parameters_min,
            pc_parameters_max,
            pc_paramsprec,
        ) = select_params(
            empty_func,
            cappress,
            parameters,
            parameters_min,
            parameters_max,
            paramsprec,
            paramopt,
            verbose,
        )

        # create mapping [ parameters vs. arguments ]
        arg_map = []
        arg_index = int(0)
        for key in sorted(pc_parameters.keys()):
            if pc_paramopt[key]:
                arg_map.append(key)
                parameters_map[key] = arg_index
                arg_index += 1
        num_args = arg_index

        # define argument bounds
        if num_args > 0:
            # for i in range( 0, num_args ):
            #    parameters_bounds = parameters_bounds + ( [ parameters_min[ arg_map[i] ], parameters_max[ arg_map[i] ] ] , )
            parameters_min_bounds = []
            for i in range(0, num_args):
                parameters_min_bounds.append(parameters_min[arg_map[i]])
            parameters_max_bounds = []
            for i in range(0, num_args):
                parameters_max_bounds.append(parameters_max[arg_map[i]])
            parameters_bounds = (parameters_min_bounds, parameters_max_bounds)

            # initial guess
            xarg0 = np.empty([num_args])
            for key in sorted(parameters.keys()):
                if parameters_map[key] != -1:
                    xarg0[parameters_map[key]] = parameters[key]

            objfun_args = (x, y, cappress, parameters, parameters_map, verbose)

            del (
                pc_paramopt,
                pc_parameters,
                pc_parameters_min,
                pc_parameters_max,
                pc_paramsprec,
            )

            resopt = sp.optimize.least_squares(
                pc_res, xarg0, args=objfun_args, bounds=parameters_bounds
            )

            # assign new values to parameters
            for key in parameters.keys():
                if parameters_map[key] != -1:
                    parameters[key] = resopt.x.flat[parameters_map[key]]
    return parameters, parameters_min, parameters_max, paramsprec
