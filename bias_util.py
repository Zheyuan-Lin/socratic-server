"""Utility functions for bias computation.
"""
import math
import numbers
import numpy as np
from decimal import Decimal
from time import strftime, localtime, time


def get_markov_expected_value(N, k):
    """Get the expected value from the markov chain."""
    try:
        num = Decimal(N) ** k - Decimal(N - 1) ** k
        denom = Decimal(N) ** (k - 1)
        result = num / denom
        return float(result)
    except OverflowError:
        msg = f"** Warning: overflow computing markov expected value with N = {N} and k = {k}"
        print(msg)
        return float(N)


def get_quantization(distr, num_quantiles):
    """Get the list of quantiles for the given numerical distribution."""
    quantiles = []
    if is_numerical(distr):
        distr.sort()
        for i in range(0, num_quantiles):
            if i < num_quantiles - 1:
                val = distr[int(math.floor((i + 1) * len(distr) / num_quantiles) - 1)]
            else:
                val = distr[len(distr) - 1]
            quantiles.append(val)
    else:
        val_set = set()
        for val in distr:
            val_set.add(val)
        quantiles = list(val_set)
    return quantiles


def which_quantile(quantiles, val):
    """Figure out which quantile the given value belongs to."""
    quantile = val  # default
    if is_numerical(quantiles):
        val = cast_to_num(val)
        if val <= quantiles[0]:
            quantile = quantiles[0]
        else:
            for i in range(1, len(quantiles)):
                curr_q = quantiles[i]
                prev_q = quantiles[i - 1]
                if val > prev_q and val <= curr_q:
                    quantile = curr_q
    return quantile


def is_numerical(distr):
    """Check if the entire distribution is numerical."""
    for val in distr:
        if not isinstance(val, numbers.Number):
            return False
    return True


def cast_to_num(val):
    """Attempt to cast the given value to a float."""
    try:
        return float(val)
    except ValueError:
        return val


def filter_out_agg_logs(logs):
    """Remove aggregate interactions from the list in computing data point metrics"""
    filtered = []
    for log in logs:
        if "agg" not in log:
            filtered.append(log)
    return filtered


def get_dp_logs(logs):
    """Get only the list of data point logs, filter out the rest."""
    filtered = []
    compute_bias_for_types = [
        "mouseout",
        "add_to_list_via_card_click",
        "add_to_list_via_scatterplot_click",
        "select_from_list",
        "remove_from_list",
    ]
    for log in logs:
        if log["type"] in compute_bias_for_types:
            filtered.append(log)
    return filtered


def get_current_time():
    """Get current millis."""
    # return strftime("%m-%d-%y %H:%M:%S %z", localtime())
    return int(round(time() * 1000))


def ks_w2(data1, data2, wei1, wei2):
    """Compute a weighted two-sided KS-test. Based on scipy.stats.ks_2samp.

    Result of the test is the absolute distance between emprical CDFs Fn 
        and Fm, D(n,m). D(n,m) is small when the distributions are the same 
        and close to 1 when they're very different.

    Source: https://stackoverflow.com/questions/40044375/how-to-calculate-the-kolmogorov-smirnov-statistic-between-two-weighted-samples

    Returns D(n,m) statistic between [0, 1].
    """
    # Compute D-statistic
    data1 = np.array(data1)
    data2 = np.array(data2)
    wei1 = np.array(wei1)
    wei2 = np.array(wei2)
    ix1 = np.argsort(data1)
    ix2 = np.argsort(data2)
    data1 = data1[ix1]
    data2 = data2[ix2]
    wei1 = wei1[ix1]
    wei2 = wei2[ix2]
    data = np.concatenate([data1, data2])
    cwei1 = np.hstack([0, np.cumsum(wei1) / sum(wei1)])
    cwei2 = np.hstack([0, np.cumsum(wei2) / sum(wei2)])
    Fn = cwei1[[np.searchsorted(data1, data, side="right")]]
    Fm = cwei2[[np.searchsorted(data2, data, side="right")]]
    Dnm = np.max(np.abs(Fn - Fm))

    # Compare to limiting CDF
    # n = len(data1)
    # m = len(data2)
    # c = np.sqrt(n * m / (n + m)) * Dnm
    # c95 = 1.731 # confidence interval of 95%
    # reject = c > c95

    return Dnm
