import matplotlib.pyplot as plt
import pandas as pd

import om_code.admin as admin
import om_code.omstats as omstats
from om_code.omfitderiv import fitderiv


def runfitderiv(
    self,
    t,
    d,
    fitvar,
    derivname,
    experiment,
    condition,
    strain,
    bd=False,
    cvfn="matern",
    empirical_errors=False,
    noruns=10,
    exitearly=True,
    noinits=100,
    nosamples=100,
    logs=False,
    iskip=False,
    figs=True,
    findareas=False,
    plotlocalmax=True,
    showpeakproperties=False,
    linalgmax=5,
    **kwargs,
):
    """
    Run fitderiv to smooth and estimate time derivatives for a single data set.

    Parameters
    ----------
    t: array
        An array of times.
    d: array
        An array of measurements of the variable to be fit.
    fitvar: string
        The name of the variable to be fit.
    derivname: string
        The name of the first time derivative of the variable.
    experiment: string
        The name of the experiment of interest.
    condition: string
        The condition of interest.
    strain: string
        The strain of interest.
    ylabels: list of strings
        The labels for the y-axis
    bd: dictionary, optional
        The bounds on the hyperparameters for the Gaussian process.
        For example, bd= {1: [-2,0])} fixes the bounds on the
        hyperparameter controlling flexibility to be 1e-2 and 1e0.
        The default for a Matern covariance function
        is {0: (-5,5), 1: (-4,4), 2: (-5,2)},
        where the first element controls amplitude, the second controls
        flexibility, and the third determines the magnitude of the
        measurement error.
    cvfn: string, optional
        The covariance function used in the Gaussian process, either
        'matern' or 'sqexp' or 'nn'.
    empirical_errors: boolean, optional
        If True, measurement errors are empirically estimated from the
        variance across replicates at each time point and so vary with
        time.
        If False, the magnitude of the measurement error is fit from the
        data assuming that this magnitude is the same at all time points.
    noruns: integer, optional
        The number of attempts made for each fit. Each attempt is made
        with random initial estimates of the hyperparameters within their
        bounds.
    exitearly: boolean, optional
        If True, stop at the first successful fit.
        If False, use the best fit from all successful fits.
    noinits: integer, optional
        The number of random attempts to find a good initial condition
        before running the optimization.
    nosamples: integer, optional
        The number of samples used to calculate errors in statistics by
        bootstrapping.
    logs: boolean, optional
        If True, find the derivative of the log of the data and should be
        True to determine the specific growth rate when dtype= 'OD'.
    iskip: integer, optional
        Use only every iskip'th data point to increase speed.
    figs: boolean, optional
        If True, plot both the fits and inferred derivative.
    findareas: boolean, optional
        If True, find the area under the plot of gr vs OD and the area
        under the plot of OD vs time. Setting to True can make getstats
        slow.
    plotlocalmax: boolean, optional
        If True, mark the highest local maxima found, which is used to
        calculate statistics, on any plots.
    showpeakproperties: boolean, optional
        If True, show properties of any local peaks that have found by
        scipy's find_peaks. Additional properties can be specified as
        kwargs and are passed to find_peaks.
    linalgmax: int, optional
        The number of linear algebra errors to tolerate.
    """
    print(f"\nFitting {fitvar} for {experiment}: {strain} in {condition}")
    # define statnames
    statnames = [
        f"min_{fitvar}",
        f"max_{fitvar}",
        f"range_{fitvar}",
        f"max_{derivname}",
        f"time_of_max_{derivname}",
    ]
    if derivname == "gr":
        # special names when estimating specific growth rate
        statnames += ["doubling_time", "lag_time"]
    else:
        statnames += [
            f"doubling_time_from_{derivname}",
            f"lag_time_from_{derivname}",
        ]
    # call fitderiv
    f = fitderiv(
        t,
        d,
        cvfn=cvfn,
        logs=logs,
        noruns=noruns,
        noinits=noinits,
        exitearly=exitearly,
        bd=bd,
        empirical_errors=empirical_errors,
        linalgmax=linalgmax,
        iskip=iskip,
    )
    if f.success:
        if figs:
            plt.figure()
            plt.subplot(2, 1, 1)
            f.plotfit(
                "f",
                ylabel=fitvar,
                figtitle=f"{experiment}: {strain} in {condition}",
            )
            axgr = plt.subplot(2, 1, 2)
            f.plotfit("df", ylabel=derivname)
            plt.tight_layout()
        else:
            axgr = None
        # find summary statistics
        (df_for_s, dict_for_sc, warning,) = omstats.findsummarystats(
            fitvar,
            derivname,
            statnames,
            nosamples,
            f,
            t,
            experiment,
            condition,
            strain,
            findareas,
            figs,
            plotlocalmax,
            axgr,
            showpeakproperties,
            **kwargs,
        )
        # store GP parameters
        dict_for_sc[f"logmaxlikehood_for_{derivname}"] = f.logmaxlike
        dict_for_sc["gp_for_" + derivname] = cvfn
        for j, val in enumerate(f.lth):
            dict_for_sc[f"log_hyperparameter_{j}_for_{derivname}"] = val
        # add time series to s dataframe
        admin.add_to_s(self, derivname, df_for_s)
        # create or add summary stats to sc dataframe
        df_for_sc = pd.DataFrame(dict_for_sc, index=pd.RangeIndex(0, 1, 1))
        admin.add_to_sc(self, df_for_sc)
        if figs:
            plt.show(block=False)
        return f, warning
    else:
        return f, None
