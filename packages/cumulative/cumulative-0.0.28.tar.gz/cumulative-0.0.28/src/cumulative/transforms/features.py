import numpy as np
import pandas as pd
import scipy
from tsfel.feature_extraction.features import (
    abs_energy,
    auc,
    autocorr,
    average_power,
    calc_centroid,
    calc_max,
    calc_mean,
    calc_median,
    calc_min,
    calc_std,
    calc_var,
    distance,
    entropy,
    fundamental_frequency,
    human_range_energy,
    interq_range,
    kurtosis,
    max_frequency,
    max_power_spectrum,
    mean_abs_deviation,
    mean_abs_diff,
    mean_diff,
    median_abs_deviation,
    median_abs_diff,
    median_diff,
    median_frequency,
    negative_turning,
    neighbourhood_peaks,
    pk_pk_distance,
    positive_turning,
    rms,
    skewness,
    slope,
    spectral_centroid,
    spectral_decrease,
    spectral_distance,
    spectral_entropy,
    spectral_kurtosis,
    spectral_positive_turning,
    spectral_skewness,
    spectral_slope,
    spectral_spread,
    spectral_variation,
    sum_abs_diff,
    zero_cross,
)

from cumulative.transforms.transform import Transform


def feature_peaks(signal):
    attrs = {}
    peaks = scipy.signal.find_peaks(signal)
    attrs["peaks.count"] = peaks[0].shape[0]

    if peaks[0].shape[0] > 0:
        peaks_prominence = scipy.signal.peak_prominences(signal, peaks[0])
        peaks_width = scipy.signal.peak_widths(signal, peaks[0])
        attrs["peaks.value.avg"] = signal[peaks[0]].mean()
        attrs["peaks.prominence.avg"] = np.mean(peaks_prominence[0])
        attrs["peaks.prominence.sum"] = np.sum(peaks_prominence[0])
        attrs["peaks.width.avg"] = np.mean(peaks_width[0])
    else:
        attrs["peaks.value.avg"] = 0
        attrs["peaks.prominence.avg"] = 0
        attrs["peaks.prominence.sum"] = 0
        attrs["peaks.width.avg"] = 0

    return attrs


def feature_stats(signal):
    return {
        "len": signal.shape[0],
        "max": signal.max(),
        "min": signal.min(),
        "std": signal.std(),
        "mean": signal.mean(),
        "median": np.median(signal),
    }


def feature_tsfel(signal):

    # Features from tsfel. Some features have been ignored due to:
    # - more than one value returned (more work required for integration)
    # - not defined in some cases
    #
    # power_bandwidth
    # spectral_roll_off
    # mfcc
    # wavelet_abs_mean
    # wavelet_energy
    # wavelet_entropy
    # wavelet_std
    # wavelet_var
    # ecdf
    # ecdf_percentile
    # ecdf_percentile_count
    # ecdf_slope
    # fft_mean_coeff
    # hist
    # lpcc

    fs = 1
    return {
        "tsfel_abs_energy": abs_energy(signal),
        "tsfel_auc": auc(signal, fs),
        "tsfel_autocorr": autocorr(signal),
        "tsfel_average_power": average_power(signal, fs),
        "tsfel_calc_centroid": calc_centroid(signal, fs),
        "tsfel_calc_max": calc_max(signal),
        "tsfel_calc_mean": calc_mean(signal),
        "tsfel_calc_median": calc_median(signal),
        "tsfel_calc_min": calc_min(signal),
        "tsfel_calc_std": calc_std(signal),
        "tsfel_calc_var": calc_var(signal),
        "tsfel_distance": distance(signal),
        "tsfel_entropy": entropy(signal),
        "tsfel_fundamental_frequency": fundamental_frequency(signal, fs),
        "tsfel_human_range_energy": human_range_energy(signal, fs),
        "tsfel_interq_range": interq_range(signal),
        "tsfel_kurtosis": kurtosis(signal),
        "tsfel_max_frequency": max_frequency(signal, fs),
        "tsfel_max_power_spectrum": max_power_spectrum(signal, fs),
        "tsfel_mean_abs_deviation": mean_abs_deviation(signal),
        "tsfel_mean_abs_diff": mean_abs_diff(signal),
        "tsfel_mean_diff": mean_diff(signal),
        "tsfel_median_abs_deviation": median_abs_deviation(signal),
        "tsfel_median_abs_diff": median_abs_diff(signal),
        "tsfel_median_diff": median_diff(signal),
        "tsfel_median_frequency": median_frequency(signal, fs),
        "tsfel_negative_turning": negative_turning(signal),
        "tsfel_neighbourhood_peaks": neighbourhood_peaks(signal),
        "tsfel_pk_pk_distance": pk_pk_distance(signal),
        "tsfel_positive_turning": positive_turning(signal),
        "tsfel_rms": rms(signal),
        "tsfel_skewness": skewness(signal),
        "tsfel_slope": slope(signal),
        "tsfel_spectral_centroid": spectral_centroid(signal, fs),
        "tsfel_spectral_decrease": spectral_decrease(signal, fs),
        "tsfel_spectral_distance": spectral_distance(signal, fs),
        "tsfel_spectral_entropy": spectral_entropy(signal, fs),
        "tsfel_spectral_kurtosis": spectral_kurtosis(signal, fs),
        "tsfel_spectral_positive_turning": spectral_positive_turning(signal, fs),
        "tsfel_spectral_skewness": spectral_skewness(signal, fs),
        "tsfel_spectral_slope": spectral_slope(signal, fs),
        "tsfel_spectral_spread": spectral_spread(signal, fs),
        "tsfel_spectral_variation": spectral_variation(signal, fs),
        "tsfel_sum_abs_diff": sum_abs_diff(signal),
        "tsfel_zero_cross": zero_cross(signal),
    }


class Features(Transform):
    def transform_row(self, row, src):

        signal = row[f"{src}.y"]
        attrs = {}
        attrs.update(feature_stats(signal))
        attrs.update(feature_peaks(signal))
        attrs.update(feature_tsfel(signal))

        return pd.Series(attrs)
