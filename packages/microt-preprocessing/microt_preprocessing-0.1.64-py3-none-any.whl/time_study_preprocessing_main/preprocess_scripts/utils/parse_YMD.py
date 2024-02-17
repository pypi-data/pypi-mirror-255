

def parse_YMD(YMD_series):
    sample = YMD_series[0]
    if "-" in sample:
        sep = "-"
    else:
        sep = " "

    y_list = []
    m_list = []
    d_list = []
    for ymd in YMD_series:
        y = ymd.split(sep)[0]
        m = ymd.split(sep)[1]
        d = ymd.split(sep)[2]

        y_list.append(y)
        m_list.append(m)
        d_list.append(d)
    return y_list, m_list, d_list
