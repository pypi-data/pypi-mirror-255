def find_precision(x):
    prec = int(0)
    while x != round(x, prec):
        prec += 1
    return prec


def interpolate(x, data, argument, value, verbose):
    """
    Interpolate data

    Parameters
    ----------
    x : float
        Value
    data : array-like
        Data
    argument : str
        Column which corresponds to the argument of function
    value : str
        Column which corresponds to the function value
    verbose : boolean
        Verbose mode
    """

    if x <= data[0][argument]:
        return data[0][value]

    num_rows = len(data)
    for i in range(0, num_rows - 1):
        if (x > data[i][argument]) and (x <= data[i + 1][argument]):
            return data[i][value] + (x - data[i][argument]) * (
                data[i + 1][value] - data[i][value]
            ) / (data[i + 1][argument] - data[i][argument])

    if x > data[num_rows - 1][argument]:
        return data[num_rows - 1][value]


def calc_rms(data, ref_data, ref_data_id, weights, default_rms, verbose):
    # number of observations( number of columns - time - weights )
    num_obsr_cols = len(ref_data[0][0]) - 2
    if verbose:
        print(f"\nNumber of observation parameters = {num_obsr_cols}")

    # index of weights data (per observation point)
    wi = int(len(ref_data[0][0]) - 1)

    num_calc_rows = len(data)
    if num_calc_rows == 0:
        return float(default_rms)

    diff = []
    rms = []
    total_rms = float(0.0)
    total_rms_prime = float(0.0)

    for k in range(0, num_obsr_cols):
        # index of observation data (0th column is time)
        ri = int(k + 1)
        # index of solution data
        di = int(ref_data_id[k])
        diff.append([])
        rms.append([])
        rms[k].append(float(0.0))
        # sol_obsrv_weight = weights[di-1]
        sol_obsrv_weight = weights[k]
        if verbose:
            print(f"\nobservation parameter[{k + 1}], weight = {sol_obsrv_weight}")
        if sol_obsrv_weight != 0.0:
            rms_prime = float(0.0)
            for m in range(0, len(ref_data)):
                num_obsr_rows = len(ref_data[m])
                rms[k].append(float(0.0))
                rms_prime_i = float(0.0)
                for i in range(0, num_obsr_rows):
                    x = ref_data[m][i][0]
                    val = 1.0e10
                    if x <= data[0][0]:
                        val = data[0][di]
                    elif x > data[num_calc_rows - 1][0]:
                        val = data[num_calc_rows - 1][di]
                    else:
                        for j in range(0, num_calc_rows - 1):
                            if (x > data[j][0]) and (x <= data[j + 1][0]):
                                val = data[j][di] + (x - data[j][0]) * (
                                    data[j + 1][di] - data[j][di]
                                ) / (data[j + 1][0] - data[j][0])
                                break
                    # if verbose:
                    #     print(f" time = {str(ref_data[m][i][0])}, "
                    #           f"observed = {str(ref_data[m][i][di])}, "
                    #           f"calculated = {str(val)})")
                    diff2 = val
                    diff2 -= ref_data[m][i][ri]
                    rms_prime_i += diff2
                    diff[k].append([float(x), float(diff2)])
                    # diff2 /= ref_data[i][di]
                    diff2 *= diff2
                    diff2 *= ref_data[m][i][wi]
                    rms[k][m + 1] += diff2
                rms_prime_i /= float(num_obsr_rows)
                rms_prime += rms_prime_i
                rms[k][m + 1] /= float(num_obsr_rows)
                rms[k][0] += rms[k][m + 1]
            rms[k][0] = rms[k][0] * sol_obsrv_weight
            rms_prime = rms_prime * sol_obsrv_weight
            total_rms += rms[k][0]
            total_rms_prime += rms_prime

    if verbose:
        output_text = "total RMS = " + str(total_rms)
        print(output_text)

    return total_rms, total_rms_prime, rms.copy(), diff.copy()


def write_rms(filename, total_rms, rms, parameters, verbose):
    # read history data
    if verbose:
        output_text = "Writing data to file: " + filename
        print(output_text)

    # write rms data
    fout = open(filename, "w")
    fout.writelines(["rms = ", str(total_rms), "\n"])

    # Loop over lines to extract variables of interest
    fout.write("parameters:")
    for key, value in parameters.items():
        fout.writelines(["\t", str(key), " = ", str(value)])

    # write rms data for each data set
    if isinstance(rms, list):
        for k in range(0, len(rms)):
            fout.writelines(["\nobserved data[", str(k), "]:"])
            fout.writelines(["\ttotal_rms = ", str(float(rms[k][0]))])
            for i in range(1, len(rms[k])):
                fout.writelines(["\ndata set[", str(i), "] : rms = ", str(rms[k][i])])
        fout.close()
    else:
        fout.writelines(["\nobserved data[", str(0), "]:"])
        fout.writelines(["\ttotal_rms = ", str(float(rms))])
        fout.writelines(["\ndata set[", str(0), "] : rms = ", str(rms)])
        fout.close()

    if verbose:
        print("Finished writing data to file: '{filename}'")


def read_rms(filename, default_rms, verbose):
    # read history data
    if verbose:
        output_text = "Reading rms from file: " + filename
        print(output_text)

    # write rms data
    fin = open(filename, "r")
    rms = default_rms

    # Loop over lines to extract variables of interest
    for line in fin:
        # read line
        line = line.strip()
        line = line.replace(",", ".")
        line = line.replace("=", "")
        columns = line.split()

        if columns[0] == "rms":
            rms = float(columns[1])
            break

    fin.close()

    if verbose:
        print("Finished reading rms from file: '{filename}'\n rms = {str(rms)}\n")

    return rms
