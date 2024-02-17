import logging
import warnings
from functools import partial
from itertools import combinations
from math import factorial

import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.interpolate import PchipInterpolator
from scipy.optimize import curve_fit
from scipy.special import betainc

from cumulative.options import options
from cumulative.transforms.transform import Transform
from cumulative.utils import warn

log = logging.getLogger(__name__)


class FitWarning(UserWarning):
    pass


class ExceptionInvalidMethod(Exception):
    pass


def fit_xy_cdf(idx, x, y, distribution_name="beta", loc=0, scale=1, optimize_loc_scale=True, map_params=None):
    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    distribution = getattr(st, distribution_name)

    p0 = [1] * len(distribution._shape_info())
    if optimize_loc_scale:
        p0 += [loc, scale]

    def cdf(x, *args):
        if optimize_loc_scale:
            param_loc = args[-2]
            param_scale = args[-1]
            params = args[:-2]
        else:
            param_loc = loc
            param_scale = scale
            params = args
        return distribution.cdf(x, *params, loc=param_loc, scale=param_scale)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        popt, _ = curve_fit(
            cdf,
            tuple(x),
            tuple(y),
            check_finite=True,
            nan_policy="raise",
            p0=p0,
            maxfev=options.get("transforms.fit.curve_fit.maxfev"),
        )

    attrs = {}
    if map_params:
        for k, v in zip(map_params, popt):
            attrs[f"model.params.{k}"] = v
    else:
        attrs["model.params"] = popt
    attrs["model.name"] = "cdf"
    attrs["model.distribution"] = distribution_name
    attrs["model.size"] = len(popt)
    return attrs, lambda x: cdf(x, *popt)


def fit_xy_interp(idx, x, y, k=2):

    # Percentile-based Linear Interpolation (PLI)
    x_model = np.linspace(0, 1, num=k + 2)
    y_model = np.interp(x_model, x, y)

    def f(x):
        return np.interp(x, x_model, y_model)

    attrs = {}
    attrs["model.name"] = "interp"
    attrs["model.params"] = (x_model, y_model)
    attrs["model.size"] = k

    return attrs, f


def fit_xy_pchip0(idx, x, y):
    """
    PCHIP 1-D monotonic cubic interpolation on all data points.
    """

    # possible source of warnings for PCHIP:
    # https://stackoverflow.com/questions/14461346/python-pchip-warnings

    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    attrs = {}
    attrs["model.name"] = "pchip0"
    attrs["model.size"] = (len(x) - 2) * 2

    return attrs, PchipInterpolator(x, y)


def fit_xy_pchip1(idx, x, y, k=1):
    """
    PCHIP 1-D monotonic cubic interpolation on k data points with equi-distant indexes.

    k=1 utilises a memory budget of 2 values.
    """

    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    # Take `k+2` equidistant indexes with no duplicates including extremes [0,N].
    # With k=1, we obtain [0, median_index, N].
    indexes = np.unique(np.round(np.linspace(0, len(x) - 1, k + 2)).astype(int))

    # With k=1, x_model and x_model will include the median index with X and Y values.
    # These two values are the model budget (extremes are always [0,1]->[0,1] and don't utilise any memory budget).
    # Therefore, with k=1, pchip1 utilises the same memory budget of the Beta distribution with parameters (a,b).
    x_model = x[indexes]
    y_model = y[indexes]

    attrs = {}
    attrs["model.name"] = "pchip1"

    attrs["model.params"] = (x_model, y_model)
    attrs["model.size"] = (len(x_model) - 2) * 2

    return attrs, PchipInterpolator(x_model, y_model)


def fit_xy_pchip2(idx, x, y, k=1, max_combinations=1000, strict=True):
    """
    PCHIP 1-D monotonic cubic interpolation on k optimal data points, found by brute-forcing
    all combinations an picking the combination with the lowest RMSE.
    Similar to PCHIP1, but with an optimal selection of the data points.

    Improvement from PCHIP1: We ignore easy-to-fit data points,
    allocating the memory budget to the most demanding regions.

    k=1 utilises a memory budget of 2 values.
    """

    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    # Given a budget of k values, we want to determine which are the best k/2 data points to memorise (x,y pairs).

    # The number of combinations for large k becomes quickly intractable. With k sufficiently low, it is always
    # guaranteed to not contain too many combinations. As a solution, we lower k s.t. we bound the maximum number
    # of combinations we test.

    # Number of combinations of sets of K non-repeating characters out of N characters in order: N!/((N-k)!)
    n = len(x)
    n_combinations = factorial(n) / factorial(n - k)
    if k > 1 and n_combinations > max_combinations:
        # If k == 1, attempt to run on all combinations.
        if strict:
            raise RuntimeError(f"{__name__}: idx={idx}: too many combinations for k={k} ({n_combinations})")
        else:
            warn(
                f"idx={idx}: too many combinations for k={k} ({n_combinations}), reducing to k={k - 1}",
                category=FitWarning,
                stacklevel=1,
            )
            return fit_xy_pchip2(idx, x, y, k=k - 1, max_combinations=max_combinations, strict=strict)

    # List of all subsets of indexes, including first and last, with k intermediate indexes
    z = [[0] + list(a) + [x.shape[0] - 1] for a in list(combinations(range(1, x.shape[0] - 1), k))]

    if len(z) == 0:
        if strict:
            # If there are no viable combinations (eg, sequences of length 2 where x=[0,1] and y=[0,1]),
            # either we raise an exception of fall back to use all the data points we have as best effort approach.
            raise RuntimeError(f"{__name__}: idx={idx}: not enough data points for k={k}")
        else:
            z = [list(range(x.shape[0]))]
            warn(
                f"sequence idx={idx} length is {x.shape[0]} and k={k} (not enough data points), falling back to z={z}",
                category=FitWarning,
                stacklevel=1,
            )

    # Let's find the best performing combination by testing them all.
    best_rmse = None
    for i in z:
        x_ = x[i]
        y_ = y[i]
        rmse = np.sqrt(np.mean((PchipInterpolator(x_, y_)(x) - y) ** 2))
        if not best_rmse or rmse < best_rmse:
            best_rmse = rmse
            best_i = i

    x_model = x[best_i]
    y_model = y[best_i]

    attrs = {}
    attrs["model.name"] = "pchip2"
    attrs["model.params"] = (x_model, y_model)
    attrs["model.params.index"] = best_i
    attrs["model.size"] = (len(x_model) - 2) * 2

    return attrs, PchipInterpolator(x_model, y_model)


def fit_xy_pchip3(idx, x, y, k=2, percentiles=None, store_percentiles=False):
    """
    PCHIP 1-D monotonic cubic interpolation on k equi-distant (or custom) percentiles.
    1. First, we fit a PCHIP model with all data points (x,y).
    2. We then extract the (x_hat,y_hat) pairs at percentiles x_hat (with k: equi-distant).
    3. We fit a new PCHIP model on (x_hat,y_hat), and return it.

    k=2 utilises a memory budget of 2 values.

    Improvement from PCHIP2: It does not suffer from the explosion of
    possible combinations of selected data points, it relies on a
    PCHIP model that passes thru all the data points (x,y),
    it provides equi-distant percentiles controlled by k using all memory budget for Y values,
    it produces easier-to-compare models (all models are aligned on the same X percentiles).
    Further, it allows to specify in which areas of the curve to invest more memory budget
    (eg., specifying percentiles=[.8,.9], we use these two X values to fit the final PCHIP model.)
    Compared to PCHIP2, it does not necessarily pass thru any of the input data points.
    """

    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    m = PchipInterpolator(x, y)

    if percentiles:
        # use explicit list of percentiles, giving control on which area we want higher accuracy.
        x_model = [0] + percentiles + [1]
    else:
        # +2 to account for extreme values, that don't utilise memory budget [0,1] -> [0,1].
        x_model = np.linspace(0, 1, k + 2)
    y_model = m(x_model)

    attrs = {}
    attrs["model.name"] = "pchip3"
    attrs["model.params.x"] = x_model
    attrs["model.params.y"] = y_model
    attrs["model.size"] = (len(x_model) - 2) * 2

    if store_percentiles:
        for p in range(101):
            attrs[f"model.p{p}"] = m(p / 100)

    # np.random.uniform(low=0, high=1, size=len(x_model)
    return attrs, PchipInterpolator(x_model, y_model)


def fit_xy_pchip4(idx, x, y, k=1):
    """
    PCHIP 1-D monotonic cubic interpolation on k optimized percentiles.
    1. First, we fit a PCHIP model with all data points (x,y).
    2. We find the optimal values for x_hat.
    3. We fit a new PCHIP model on (x_hat,y_hat), and return it.

    k=1 utilises a memory budget of 2 values: x_hat, y_hat.

    Improvement from PCHIP3: x_hat is not fixed anymore, but optimized as well.
    We lose some flexibility, in some cases this translates to higher accuracy.
    This doesn't always results in better performance, likely due to limitations
    of the current optimization process that is constrained and causes
    some issues to curve_
    Compared to PCHIP2, it does not necessarily pass thru any of the input data points.
    """

    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    m = PchipInterpolator(x, y)

    def valid_xmodel(x_model):
        # PchipInterpolator accepts as input only distinct, increasing values.
        # Further, we append the two percentiles at [0,1].
        return sorted(set([0] + list(x_model) + [1]))

    def f(x, *x_model):
        x_model = valid_xmodel(x_model)
        y_model = m(x_model)
        return PchipInterpolator(x_model, y_model)(x)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        popt, _ = curve_fit(
            f,
            tuple(x),
            tuple(y),
            check_finite=True,
            nan_policy="raise",
            method=None,
            p0=np.random.uniform(0, 1, size=k),
            bounds=[[0] * k, [1] * k],
            maxfev=options.get("transforms.fit.curve_fit.maxfev"),
        )
        x_model = valid_xmodel(popt)
        y_model = m(x_model)

    attrs = {}
    attrs["model.name"] = "pchip4"
    attrs["model.params"] = (x_model, y_model)
    attrs["model.size"] = (len(x_model) - 2) * 2

    return attrs, PchipInterpolator(x_model, y_model)


def fit_xy_beta_pchip(idx, x, y, k=1, **kwargs):
    """
    PCHIP 1-D monotonic cubic interpolation on k equi-distant (or custom) percentiles.
    1. We fit the Beta
    2. We fit using pchip3 on the residuals
    3. We combine the Beta and the pchip3 fit, taking care of returning a monotonic increasing curve.

    Benefits: It relies on the Beta to capture the high-level trend, then relying on PCHIP
    to deformate the Beta in the regions with the highest errors.

    The curve might not be always smooth, with points where the curve remains constant if the sum with
    the residuals would have resulted in a decreasing curve.

    k=2 utilises a memory budget of 4 values (2 for Beta, and 2 for pchip3).
    """

    beta_attrs, beta_fit = fit_xy_betainc(idx, x, y)
    beta_residuals = y - beta_fit(x)
    pchip_attrs, pchip_fit = fit_xy_pchip3(idx, x, beta_residuals, **kwargs)

    def model(x):
        if k == 0:
            return beta_fit(x)
        else:
            return np.maximum.accumulate(beta_fit(x) + pchip_fit(x))

    attrs = {}
    attrs["model.name"] = "beta_pchip"
    attrs["model.params.a"] = beta_attrs["model.a"]
    attrs["model.params.b"] = beta_attrs["model.b"]
    attrs["model.size"] = beta_attrs["model.size"] + pchip_attrs["model.size"]
    return attrs, model


def fit_xy_betainc(idx, x, y, percentage=None, errors="raise", bounds=None):

    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    if bounds is None:
        # Set bounds to defaults as defined in curve_fit
        bounds = (-np.inf, np.inf)

    try:
        # Handle the special case of all `y` values equal to a constant
        # by raising an exception.
        if len(set(y)) == 1:
            raise RuntimeError("All y values are equal")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            popt, _ = curve_fit(
                lambda x, a, b: betainc(a, b, x),
                tuple(x),
                tuple(y),
                check_finite=True,
                nan_policy="raise",
                method=None,
                bounds=bounds,
                maxfev=options.get("transforms.fit.curve_fit.maxfev"),
            )
            a = popt[0]
            b = popt[1]
    except RuntimeError as e:
        if errors == "diagonal":
            warn(
                f'idx={idx}: Beta fit failed to converge and errors="diagonal", defaulting to a=1 b=1',
                category=FitWarning,
                stacklevel=1,
            )
            a = 1
            b = 1
        else:
            raise e

    if percentage is not None:
        a = 1 + percentage * (a - 1)
        b = 1 + percentage * (b - 1)

    attrs = {}
    attrs["model.name"] = "betainc"
    attrs["model.a"] = a
    attrs["model.b"] = b
    attrs["model.ab_ratio"] = (a + 1) / (b + 1)
    attrs["model.ab_equal"] = 1 / (1 + np.abs(a - b))
    attrs["model.size"] = 2

    return attrs, partial(betainc, a, b)


def fit_xy_curvefit(idx, x, y, func=None, map_params=None, p0=None, bounds=None):

    # Seed the random number generator for reproducibility
    np.random.seed(options.get("reproducibility.random_seed"))

    if func is None:

        def func(x, a, b):
            return betainc(a, b, x)

    if bounds is None:
        # Set bounds to defaults as defined in curve_fit
        bounds = (-np.inf, np.inf)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        popt, _ = curve_fit(
            func,
            tuple(x),
            tuple(y),
            check_finite=True,
            nan_policy="raise",
            method=None,
            bounds=bounds,
            p0=p0,
            maxfev=options.get("transforms.fit.curve_fit.maxfev"),
        )

    attrs = {}
    attrs["model.name"] = "curvefit"
    attrs["model.func"] = func.__name__
    if map_params:
        for k, v in zip(map_params, popt):
            attrs[f"model.params.{k}"] = v
    else:
        attrs["model.params"] = popt
    attrs["model.size"] = len(popt)

    return attrs, lambda x: func(x, *popt)


def fit_xy(idx, x, y, method="betainc", **method_kwargs):  # noqa

    try:
        if method == "betainc":
            return fit_xy_betainc(idx, x, y, **method_kwargs)
        if method == "curvefit":
            return fit_xy_curvefit(idx, x, y, **method_kwargs)
        elif method == "cdf":
            return fit_xy_cdf(idx, x, y, **method_kwargs)
        elif method == "interp":
            return fit_xy_interp(idx, x, y, **method_kwargs)
        elif method == "pchip0":
            return fit_xy_pchip0(idx, x, y, **method_kwargs)
        elif method == "pchip1":
            return fit_xy_pchip1(idx, x, y, **method_kwargs)
        elif method == "pchip2":
            return fit_xy_pchip2(idx, x, y, **method_kwargs)
        elif method == "pchip3":
            return fit_xy_pchip3(idx, x, y, **method_kwargs)
        elif method == "pchip4":
            return fit_xy_pchip4(idx, x, y, **method_kwargs)
        elif method == "beta_pchip":
            return fit_xy_beta_pchip(idx, x, y, **method_kwargs)
        else:
            raise ExceptionInvalidMethod(f"No valid method: '{method}'")
    except (RuntimeError, TypeError, ValueError) as e:
        warn(f"{__name__}: idx={idx}: {e.__class__.__name__}: {e}", category=FitWarning, stacklevel=1)
        attrs = {}
        attrs["model.name"] = method
        return attrs, lambda x: np.full(x.shape, np.nan)


class Fit(Transform):
    def transform_row(self, row, src, method="interp", n_samples=1000, **method_kwargs):

        attrs, func = fit_xy(row["idx"], row[f"{src}.x"], row[f"{src}.y"], method, **method_kwargs)

        attrs["x"] = np.linspace(0, 1, num=n_samples, endpoint=True)
        attrs["y"] = func(attrs["x"])
        attrs["y_scale"] = func(row[f"{src}.x"])
        attrs["error.y"] = attrs["y_scale"] - row[f"{src}.y"]
        attrs["error.rmse"] = np.sqrt(np.mean((attrs["error.y"]) ** 2))
        attrs["error.abs.y"] = np.abs(attrs["error.y"])

        attrs["diagonal_dist.abs"] = pd.Series(attrs["y"] - attrs["x"]).abs().mean()

        for prefix in ["error.abs", "error"]:
            # Calculate statistics on error distribution, absolute and signed residuals.
            attrs[f"{prefix}.mean"] = np.mean(attrs[f"{prefix}.y"])
            attrs[f"{prefix}.sum"] = np.sum(attrs[f"{prefix}.y"])
            attrs[f"{prefix}.median"] = np.median(attrs[f"{prefix}.y"])
            attrs[f"{prefix}.std"] = attrs["x"][np.argmax(attrs["y"] > 0.75)]
            attrs[f"{prefix}.min"] = np.min(attrs[f"{prefix}.y"])
            attrs[f"{prefix}.max"] = np.max(attrs[f"{prefix}.y"])
            attrs[f"{prefix}.p25"] = np.percentile(attrs[f"{prefix}.y"], 25)
            attrs[f"{prefix}.p50"] = np.percentile(attrs[f"{prefix}.y"], 50)
            attrs[f"{prefix}.p75"] = np.percentile(attrs[f"{prefix}.y"], 75)

        attrs["p05"] = attrs["x"][np.argmax(attrs["y"] > 0.05)]
        attrs["p25"] = attrs["x"][np.argmax(attrs["y"] > 0.25)]
        attrs["p50"] = attrs["x"][np.argmax(attrs["y"] > 0.50)]
        attrs["p75"] = attrs["x"][np.argmax(attrs["y"] > 0.75)]
        attrs["p95"] = attrs["x"][np.argmax(attrs["y"] > 0.95)]

        return pd.Series(attrs)
