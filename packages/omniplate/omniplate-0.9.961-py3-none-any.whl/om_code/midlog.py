# Find and analyse mid-log growth
import matplotlib.pylab as plt
import numpy as np
from nunchaku import Nunchaku

import om_code.admin as admin
import om_code.sunder as sunder
import om_code.omgenutils as gu


def find_midlog_stats(
    self,
    stats,
    min_duration,
    max_num,
    prior,
    use_smoothed,
    figs,
    exps,
    cons,
    strs,
    **kwargs,
):
    """Find the stat of all variables in the s dataframe for mid-log growth."""
    stats = gu.makelist(stats)
    for e in exps:
        for c in cons:
            for s in strs:
                select = (
                    (self.s.experiment == e)
                    & (self.s.condition == c)
                    & (self.s.strain == s)
                )
                # get OD data
                if use_smoothed:
                    try:
                        Y = self.s[select]["smoothed_log_OD"].values
                        t = self.s[select]["time"].values
                        sd = self.s[select]["smoothed_log_OD_err"].values
                    except KeyError:
                        print(
                            f"Warning: smoothed ODs do not exist for {e}:{s}"
                            " in {c}"
                        )
                        continue
                else:
                    res = sunder.extractwells(
                        self.r, self.s, e, c, s, ["time", "OD"]
                    )
                    t, od = res[0], res[1]
                    if np.any(t):
                        t = np.median(t, axis=1)
                        od[od < 0] = np.finfo(float).eps
                        Y = np.log(od.T)
                    else:
                        Y = []
                if len(Y):
                    print(f"\nFinding mid-log growth for {e} : {s} in {c}")
                    # run nunchaku on log(OD)
                    if use_smoothed:
                        # use standard deviation from GP
                        err = sd
                    else:
                        # estimate standard deviation from replicates
                        err = None
                    nc = Nunchaku(t, Y, err=err, prior=prior, **kwargs)
                    num_segs, evidence = nc.get_number(num_range=max_num)
                    bds, bds_std = nc.get_iboundaries(num_segs)
                    res_df = nc.get_info(bds)
                    # pick midlog segment
                    t_st, t_en = pick_midlog(res_df, min_duration)
                    if np.isnan(t_st) or np.isnan(t_en):
                        print(
                            f"\nError finding midlog data for {e}: {s} in {c}."
                        )
                        return None
                    # plot nunchaku's results
                    if figs:
                        nc.plot(res_df, hlmax=None)
                        for tv in [t_st, t_en]:
                            iv = np.argmin((t - tv) ** 2)
                            if use_smoothed:
                                y_med = Y
                            else:
                                y_med = np.mean(Y, axis=0)
                            plt.plot(
                                tv,
                                y_med[iv],
                                "ks",
                                markersize=10,
                            )
                        plt.xlabel("time")
                        plt.ylabel("log(OD)")
                        plt.title(f"mid-log growth for {e} : {s} in {c}")
                        plt.show(block=False)
                    # find statistics over mid-log growth
                    sdf = self.s[select]
                    midlog_sdf = sdf[(sdf.time >= t_st) & (sdf.time <= t_en)]
                    midlog_sdf = midlog_sdf.dropna(axis=1, how="all").dropna()
                    for stat in stats:
                        # store results in dict
                        res_dict = {col: np.nan for col in self.s.columns}
                        res_dict["experiment"] = e
                        res_dict["condition"] = c
                        res_dict["strain"] = s
                        stat_res = getattr(midlog_sdf, stat)(numeric_only=True)
                        for key, value in zip(stat_res.index, stat_res.values):
                            res_dict[key] = value
                        # add "midlog" to data names
                        res_dict = {
                            (
                                f"{stat}_midlog_{k}"
                                if k
                                not in [
                                    "experiment",
                                    "condition",
                                    "strain",
                                ]
                                else k
                            ): v
                            for k, v in res_dict.items()
                        }
                        # add to sc dataframe
                        admin.add_to_sc(self, res_dict)


def pick_midlog(res_df, min_duration):
    """Find midlog from nunchaku's results dataframe."""
    # midlog had a minimal duration and positive growth rate
    sdf = res_df[(res_df["delta x"] > min_duration) & (res_df.gradient > 0)]
    if sdf.empty:
        return np.nan, np.nan
    else:
        # find mid-log growth - maximal specific growth rate
        ibest = sdf.index[sdf.gradient.argmax()]
        t_st, t_en = sdf["x range"][ibest]
        return t_st, t_en
