import os
import numpy as np


def load(filename, verbose):
    data = []
    # read history data
    if verbose:
        print(f"Reading data from file: '{filename}'")

    # open input file
    fin = open(filename, "r")

    # Loop over lines to extract variables of interest
    comment_symbol = "#"
    for line in fin:
        # read line
        line = line.strip()
        line = line.replace(",", ".")
        columns = line.split()
        clen = len(columns)

        if clen > 0:
            if columns[0][0] != comment_symbol:
                row_data = []
                for i in range(0, clen):
                    row_data.append(np.float64(columns[i]))
                data.append(row_data.copy())
                del row_data

    fin.close()

    if verbose:
        print(f"Finished reading data from file: '{filename}'")
    return data


def load_and_average(filename, verbose):
    data = []

    # read history data
    if verbose:
        print(f"Reading data from file: '{filename}'")

    # open input file
    fin = open(filename, "r")

    # open output file
    wdir = os.path.dirname(filename)
    fname = os.path.basename(filename)
    new_filename = wdir + "/average-" + fname
    fout = open(new_filename, "w")

    # Loop over lines to extract variables of interest
    comment_symbol = "#"
    k = -1
    t = -1.0
    clen = 0
    data_sum = []
    data_block_size = 0
    for line in fin:
        # read line
        line = line.strip()
        line = line.replace(",", ".")
        columns = line.split()
        clen = len(columns)

        if clen > 0:
            if columns[0][0] != comment_symbol:
                row_data = []
                for i in range(0, clen):
                    row_data.append(np.float64(columns[i]))
                if len(data_sum) < clen:
                    for i in range(len(data_sum), clen):
                        data_sum.append(np.float64(0.0))

                # check whether time is the same as previous entry
                if row_data[0] == t:
                    data_block_size += 1
                    for i in range(1, clen):
                        data_sum[i] += row_data[i]
                else:
                    # save average values
                    if data_block_size > 1.0:
                        for i in range(1, clen):
                            data[k][i] = data_sum[i] / np.float64(data_block_size)
                    if k != -1:
                        # write to file
                        fout.writelines([str(data[k][0])])
                        iend = len(data[k])
                        for i in range(1, iend):
                            fout.writelines(["\t", str(data[k][i])])
                        fout.writelines(["\n"])

                    # record new data
                    t = row_data[0]
                    for i in range(1, clen):
                        data_sum[i] = row_data[i]

                    data_block_size = 1

                    data.append(row_data)
                    del row_data
                    k += 1
            else:
                fout.writelines([line, "\n"])
        else:
            fout.writelines(["\n"])

    if k != -1:
        if data_block_size > 1:
            for i in range(1, clen):
                data[k][i] = data_sum[i] / np.float64(data_block_size)
        # write last entry to file
        fout.writelines([str(data[k][0])])
        iend = len(data[k])
        for i in range(1, iend):
            fout.writelines(["\t", str(data[k][i])])
        fout.writelines(["\n"])
    fin.close()
    fout.close()

    if verbose:
        print(f"Finished reading data from file: '{filename}'")
    return data


def save(filename, data, verbose):
    # read history data
    if verbose:
        print(f"Writing data to file: '{filename}'")

    # write data to file
    fout = open(filename, "w")

    # Loop over lines to extract variables of interest
    num_rows = len(data)
    num_cols = len(data[0])
    for i in range(0, num_rows):
        for j in range(0, num_cols - 1):
            fout.writelines([str(data[i][j]), "\t"])
        fout.writelines([str(data[i][num_cols - 1]), "\n"])

    fout.close()

    if verbose:
        print(f"Finished writing data to file: '{filename}'")


def load_multiple_arrays(filename, verbose):
    data = []

    # read history data
    if verbose:
        print(f"Reading data from file: '{filename}'")

    # open input file
    fin = open(filename, "r")

    # Loop over lines to extract variables of interest
    layer_id = int(-1)
    is_new_layer = True
    comment_symbol = "#"
    for line in fin:
        # read line
        line = line.strip()
        line = line.replace(",", ".")
        columns = line.split()
        clen = len(columns)

        if clen == 0:
            is_new_layer = True
        else:
            if columns[0][0] != comment_symbol:
                if is_new_layer:
                    is_new_layer = False
                    layer_id += int(1)
                    data.append([])
                row_data = []

                for i in range(0, clen):
                    row_data.append(float(columns[i]))
                data[layer_id].append(row_data.copy())
                del row_data

    # if verbose:
    #     print('Data matrix: ')
    #     num_data_rows = len(data)
    #     for i in range(0, num_data_rows):
    #         output_text = f"data[{str(i)}] = {str(data[i])}"
    #         print(output_text)
    fin.close()

    if verbose:
        print(f"Finished reading data from file: '{filename}'")
    return data


def save_multiple_arrays(filename, header, data, verbose):
    # read history data
    if verbose:
        print(f"Writing data to file: '{filename}'")

    # write data to file
    fout = open(filename, "w")
    fout.writelines(["# ", header, "\n"])

    # Loop over lines to extract variables of interest
    num_blocks = len(data)
    for k in range(0, num_blocks):
        num_rows = len(data[k])
        num_cols = len(data[k][0])
        for i in range(0, num_rows):
            for j in range(0, num_cols - 1):
                fout.writelines(
                    [
                        str(data[k][i][j]),
                        "\t",
                    ]
                )
            fout.writelines(
                [
                    str(data[k][i][num_cols - 1]),
                    "\n",
                ]
            )
        if k != (num_blocks - 1):
            fout.writelines(["\n\n"])

    fout.close()

    if verbose:
        print(f"Finished writing data to file: '{filename}'")


def save_graf_file(
    filename,
    project_name,
    data,
    mnemonics,
    units,
    well_or_group_name,
    col1,
    col2,
    verbose,
):
    # read history data
    if verbose:
        print(f"Writing data to file: '{filename}'")

    # write data to file
    fout = open(filename, "w")

    # write graf header
    fout.writelines(["ORIGIN\t", project_name])
    fout.writelines(["\n", str(mnemonics[0]), "\t", str(mnemonics[1])])
    fout.writelines(["\n", str(units[0]), "\t", str(units[1])])
    fout.writelines(["\n", str(well_or_group_name), "\n\n"])

    # Loop over lines to extract variables of interest
    # Loop over lines to extract variables of interest
    num_blocks = len(data)
    for k in range(0, num_blocks):
        num_rows = len(data[k])
        for i in range(0, num_rows):
            fout.writelines([str(data[k][i][col1]), "\t", str(data[k][i][col2]), "\n"])

    fout.close()

    if verbose:
        print(f"Finished writing data to file: '{filename}'")


def load_rock_and_fluid_data(filename, verbose):
    # default values for core and fluid data

    # -----------------------
    # core characteristics
    # -----------------------

    # length [ cm ]

    length = np.float64(10.0)
    diameter = np.float64(4.0)
    radius_centre = np.float64(0.0)
    depth = np.float64(0.0)

    # -----------------------
    # rock properties
    # -----------------------

    # porosity [ Vp/Vb ]
    # permeability [ mD, 1mD = 10^-3 darcy = 10^-12 m^2  ]
    # compressibility [ 1/atm ]

    porosity = np.float64(0.25)
    permeability = np.float64(100.0)
    rock_compressibility = np.float64(1.0e-15)

    # -----------------------
    # fluid properties
    # -----------------------

    # density   [ gm/cc, 1 g/cc = 10^-3 kg/m^3 ]
    # viscosity [ cP, 1cP = 10^-3 Pa*s ]
    # gravity constant [ cm^2 atm /gm, g = 0.000968 cm^2 atm /gm ]

    density_water = np.float64(1.0)
    viscosity_water = np.float64(1.0)
    viscosibility_water = np.float64(0.0)

    density_oil = np.float64(0.8)
    viscosity_oil = np.float64(5.0)
    viscosibility_oil = np.float64(0.0)

    # -----------------------
    # initial conditions
    # -----------------------

    # pressure ( absolute )  [ 1 atma ]
    # pressure (difference ) [ 1 atm, 1bars = 0.986923 atm, 1 psi = 0.068046 atm ]
    # liquid surface rate [ scc ]

    sw_init = np.float64(0.0)

    # read rock and fluid data
    if verbose:
        print(f"Reading data from file: '{filename}'")

    # open input file
    fin = open(filename, "r")

    # Loop over lines to extract variables of interest
    comment_symbol = "#"
    for line in fin:
        # read line
        line = line.strip()
        line = line.replace(",", ".")
        line = line.replace("=", "")
        columns = line.split()
        clen = len(columns)

        if clen > 0:
            if columns[0][0] != comment_symbol:
                # -----------------------
                # fluid and rock propeties
                # -----------------------
                rock_compressibility = np.float64(1.0e-15)
                if columns[0] == "length":
                    length = np.float64(columns[1])
                elif columns[0] == "diameter":
                    diameter = np.float64(columns[1])
                elif columns[0] == "radius-centre":
                    radius_centre = np.float64(columns[1])
                elif columns[0] == "depth":
                    depth = np.float64(columns[1])
                elif columns[0] == "porosity":
                    porosity = np.float64(columns[1])
                elif columns[0] == "permeability":
                    permeability = np.float64(columns[1])
                elif columns[0] == "rock-compressibility":
                    rock_compressibility = np.float64(columns[1])
                elif columns[0] == "brine-density":
                    density_water = np.float64(columns[1])
                elif columns[0] == "brine-viscosity":
                    viscosity_water = np.float64(columns[1])
                elif columns[0] == "brine-viscosibility":
                    viscosibility_water = np.float64(columns[1])
                elif columns[0] == "oil-density":
                    density_oil = np.float64(columns[1])
                elif columns[0] == "oil-viscosity":
                    viscosity_oil = np.float64(columns[1])
                elif columns[0] == "oil-viscosibility":
                    viscosibility_oil = np.float64(columns[1])
                elif columns[0] == "initial-saturation":
                    sw_init = np.float64(columns[1])

    fin.close()

    if verbose:
        print(f"Finished reading data from file: '{filename}'")

    return (
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
    )


def load_control_and_observed_data(
    simcontrol_datafile, obs_datafile, duration_time, verbose
):
    # collect time data
    time_set = []

    # read simulator control data
    simcontrol_data_vec = load(simcontrol_datafile, verbose)

    # read simulator control data
    simcontrol_data = []
    section = -1
    current_const_value = []
    num_entries = int(len(simcontrol_data_vec))
    for i in range(0, num_entries):
        # time
        t = np.float64(simcontrol_data_vec[i][0])

        # control data
        if t < duration_time:
            val = []
            for j in range(1, len(simcontrol_data_vec[i])):
                val.append(np.float64(simcontrol_data_vec[i][j]))
            if set(val).symmetric_difference(current_const_value) != set():
                section += 1
                current_const_value = val.copy()
                time_set.append(set())
                simcontrol_data.append([])
                simcontrol_data[section].append(val)
                if section != 0:
                    simcontrol_data[section - 1].append(t)  # end of previous section
            simcontrol_data[section].append(t)
            time_set[section].add(t)

            del val

        if (i == num_entries - 1) or (t > duration_time):
            last_entry = len(simcontrol_data[section]) - 1
            if simcontrol_data[section][last_entry] < duration_time:
                simcontrol_data[section].append(duration_time)
                val = [duration_time]
                for j in range(1, len(simcontrol_data_vec[i])):
                    val.append(np.float64(simcontrol_data_vec[i][j]))
                simcontrol_data_vec.append(val)
                del val

            break

    # define number of different section
    num_sections = len(simcontrol_data)

    # read observation data
    ref_data_vec = load_and_average(obs_datafile, verbose)

    # read observation data
    ref_data = []
    section = -1
    current_end_time = np.float64(-1.0)
    for i in range(0, len(ref_data_vec)):
        # time
        t = np.float64(ref_data_vec[i][0])

        # observed data
        if t <= duration_time:
            val = []
            for j in range(0, len(ref_data_vec[i])):
                val.append(np.float64(ref_data_vec[i][j]))
            if (t >= current_end_time) and (section != (num_sections - 1)):
                section += 1
                # if verbose :
                #     print('section = ', section )
                current_end_time = simcontrol_data[section][
                    len(simcontrol_data[section]) - 1
                ]
                ref_data.append([])
            # if verbose:
            #     print('time = ', t, ', current end time = ', current_end_time)
            ref_data[section].append(val)
            time_set[section].add(t)
        else:
            break

    last_section = len(time_set) - 1
    time_set[last_section].add(duration_time)

    # sort time data
    time_data = []
    for i in range(0, len(time_set)):
        time_data.append(sorted(time_set[i]))
    del time_set

    return time_data, simcontrol_data_vec, simcontrol_data, ref_data_vec, ref_data


def save_data_to_vtk_file(
    filename_header,
    problemname,
    propertyname,
    pxyz,
    cell_points,
    cells,
    data,
    is_time_data=False,
    verbose=False,
):
    # read history data
    if verbose:
        print("Writing data to VTK file: '{filename_header}'")

    # VTU grid characteristics
    VTK_HEXAHEDRON = int(12)
    HEXA_NODES = int(8)
    hexa_map = [0, 1, 3, 2, 4, 5, 7, 6]

    # grid characteristics
    num_points = len(pxyz)
    num_cells = len(cells)

    num_files = int(1)
    if is_time_data:
        num_files = len(data)

    for fid in range(0, num_files):
        fname = filename_header + "_" + str(fid) + ".vtu"

        # write data to file
        fout = open(fname, "w")

        # write XML header
        fout.writelines(['<?xml version="1.0"?>\n'])
        fout.writelines(["<!-- \n"])
        fout.writelines([problemname, "\n"])
        fout.writelines(["-->\n"])

        fout.writelines(["\n"])

        # write VTK file header
        fout.writelines(
            [
                '<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian">\n'
            ]
        )

        # start Unstructured Grid section
        fout.writelines(["\t<UnstructuredGrid>\n"])

        if is_time_data:
            # start Piece section
            fout.writelines(["\t\t<FieldData>\n"])
            fout.writelines(
                [
                    '\t\t\t<DataArray type="Float32" Name="Time" NumberOfTuples="1" format="ascii">\n'
                ]
            )
            fout.writelines(["\t\t\t\t", str(data[fid][0]), "\n"])
            fout.writelines(["\t\t\t</DataArray>\n"])
            fout.writelines(["\t\t</FieldData>\n"])

        # start Piece section
        fout.writelines(
            [
                '\t\t<Piece NumberOfPoints="',
                str(num_points),
                '" NumberOfCells="',
                str(num_cells),
                '">\n',
            ]
        )

        # start Points section
        fout.writelines(["\t\t\t<Points>\n"])
        fout.writelines(
            [
                '\t\t\t\t<DataArray type="Float32" Name="Position" NumberOfComponents="3" format="ascii">\n'
            ]
        )
        for i in range(0, num_points):
            fout.writelines(
                [
                    "\t\t\t\t\t",
                    str(pxyz[i][0]),
                    "\t",
                    str(pxyz[i][1]),
                    "\t",
                    str(pxyz[i][2]),
                    "\n",
                ]
            )
        fout.writelines(["\t\t\t\t</DataArray>\n"])
        # end Points section
        fout.writelines(["\t\t\t</Points>\n"])

        # start Cells section
        fout.writelines(["\t\t\t<Cells>\n"])
        # connectivity
        fout.writelines(
            [
                '\t\t\t\t<DataArray type="Int32" Name="connectivity" NumberOfComponents="1" format="ascii">\n'
            ]
        )
        for i in range(0, num_cells):
            cid = cells[i]
            fout.writelines(["\t\t\t\t"])
            for j in range(0, HEXA_NODES):
                fout.writelines(["\t", str(cell_points[cid][hexa_map[j]])])
            fout.writelines(["\n"])
        fout.writelines(["\t\t\t\t</DataArray>\n"])
        # offsets
        fout.writelines(
            [
                '\t\t\t\t<DataArray type="Int32" Name="offsets" NumberOfComponents="1" format="ascii">\n'
            ]
        )
        offset = int(0)
        for i in range(0, num_cells):
            offset += HEXA_NODES
            fout.writelines(["\t\t\t\t\t", str(offset), "\n"])
        fout.writelines(["\t\t\t\t</DataArray>\n"])
        # types
        fout.writelines(
            [
                '\t\t\t\t<DataArray type="UInt8" Name="types" NumberOfComponents="1" format="ascii">\n'
            ]
        )
        for i in range(0, num_cells):
            fout.writelines(["\t\t\t\t\t", str(VTK_HEXAHEDRON), "\n"])
        fout.writelines(["\t\t\t\t</DataArray>\n"])
        # end Cells section
        fout.writelines(["\t\t\t</Cells>\n"])

        # start Cell Data section
        fout.writelines(["\t\t\t<CellData>\n"])
        # start Data section
        fout.writelines(
            [
                '\t\t\t\t<DataArray type="Float32" Name="',
                propertyname,
                '" NumberOfComponents="1" format="ascii">\n',
            ]
        )
        if is_time_data:
            for i in range(0, num_cells):
                fout.writelines(["\t\t\t\t\t", str(data[fid][cells[i] + 1]), "\n"])
        else:
            for i in range(0, num_cells):
                fout.writelines(["\t\t\t\t\t", str(data[cells[i]]), "\n"])
        fout.writelines(["\t\t\t\t</DataArray>\n"])
        # end Cell Data section
        fout.writelines(["\t\t\t</CellData>\n"])

        # end Piece section
        fout.writelines(["\t\t</Piece>\n"])

        # end Unstructured Grid section
        fout.writelines(["\t</UnstructuredGrid>\n"])

        fout.writelines(["</VTKFile>"])

        fout.close()

    if verbose:
        print(f"Finished writing data to VTK file: '{filename_header}'")
