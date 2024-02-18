import numpy as np


def parseSunrise(dfd, rdict):
    """Parse a data frame from a Sunrise plate reader into a dict."""
    rdict["OD"] = []
    # extract times of measurements
    t = (
        np.array([float(str(ts).split("s")[0]) for ts in dfd.to_numpy()[0]])
        / 3600
    )
    t = t[~np.isnan(t)]
    # extract data
    for x in np.arange(1, 13):
        for y in "ABCDEFGH":
            well = y + str(x)
            if well in dfd["Well positions"].values:
                data = dfd[dfd["Well positions"] == well].iloc[:, :-1].values
                data = data.reshape(data.size)
                for i, tv in enumerate(t):
                    rdict["time"].append(tv)
                    rdict["well"].append(well)
                    rdict["OD"].append(data[i])
    return rdict
