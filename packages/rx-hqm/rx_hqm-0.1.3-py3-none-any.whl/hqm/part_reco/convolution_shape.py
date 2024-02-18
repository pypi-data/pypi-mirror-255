import zfit
from zutils.pdf import SUJohnson
from hqm.tools.utility import load_pickle
from hqm.tools.utility import get_project_root
from hqm.tools.utility import cache_json
from hqm.tools.Cut import Cut
from hqm.part_reco.fit_convolution import get_data
import hist
from logzero import logger

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import mplhep


def get_correction_DSCB(obs, suffix, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    mu = zfit.Parameter(f"{parameter_name_prefix}correction_DSCB_mu_{suffix}", 0, -100, 100)
    sigma = zfit.Parameter(f"{parameter_name_prefix}correction_DSCB_sigma_{suffix}", 40, 0.1, 100)
    al = zfit.Parameter(f"{parameter_name_prefix}correction_DSCB_al_{suffix}", 1.5, 0.001, 10)
    nl = zfit.Parameter(f"{parameter_name_prefix}correction_DSCB_nl_{suffix}", 1, 0.001, 110)
    ar = zfit.Parameter(f"{parameter_name_prefix}correction_DSCB_ar_{suffix}", 1.5, 0.001, 10)
    nr = zfit.Parameter(f"{parameter_name_prefix}correction_DSCB_nr_{suffix}", 1, 0.001, 110)

    correction_DSCB = zfit.pdf.DoubleCB(
        obs=obs,
        mu=mu,
        sigma=sigma,
        alphal=al,
        nl=nl,
        alphar=ar,
        nr=nr,
        name=f"{parameter_name_prefix}correction_DSCB_{suffix}",
    )
    return correction_DSCB


def get_correction_left_CB(obs, suffix, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""
    mu = zfit.Parameter(f"{parameter_name_prefix}correction_left_CB_mu_{suffix}", -100, -500, 0)
    sigma = zfit.Parameter(f"{parameter_name_prefix}correction_left_CB_sigma_{suffix}", 5, 0.001, 100)
    alpha = zfit.Parameter(f"{parameter_name_prefix}correction_left_CB_alpha_{suffix}", 0.5, 0.001, 2)
    n = zfit.Parameter(f"{parameter_name_prefix}correction_left_CB_n_{suffix}", 50, 1, 110)

    correction_left_CB = zfit.pdf.CrystalBall(
        obs=obs, mu=mu, sigma=sigma, alpha=alpha, n=n, name=f"{parameter_name_prefix}correction_left_CB_{suffix}"
    )
    return correction_left_CB


def get_correction_right_CB(obs, suffix, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""
    mu = zfit.Parameter(f"{parameter_name_prefix}correction_right_CB_mu_{suffix}", 100, 0, 500)
    sigma = zfit.Parameter(f"{parameter_name_prefix}correction_right_CB_sigma_{suffix}", 5, 0.001, 100)
    alpha = zfit.Parameter(f"{parameter_name_prefix}correction_right_CB_alpha_{suffix}", -0.5, -2, -0.001)
    n = zfit.Parameter(f"{parameter_name_prefix}correction_right_CB_n_{suffix}", 50, 1, 110)

    correction_right_CB = zfit.pdf.CrystalBall(
        obs=obs, mu=mu, sigma=sigma, alpha=alpha, n=n, name=f"{parameter_name_prefix}correction_right_CB_{suffix}"
    )
    return correction_right_CB


def load_pdf(pickle_path: str, pdf, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    json_path = pickle_path.replace("/", "_").removesuffix("pickle") + "json"

    @cache_json(json_path)
    def _get_params():
        _pickle_path = get_project_root() + pickle_path
        obj = load_pickle(_pickle_path)
        fit_result = obj["result"]
        params_value = dict(fit_result.params)

        return params_value

    params_value = _get_params()
    params = pdf.get_params()
    for param in params:
        param_name = param.name.removeprefix(parameter_name_prefix)
        param_value = params_value[param_name]["value"]
        param.set_value(param_value)

    return pdf


def plot_cmb_and_data(plot_cmb, data_array, cmb_shape, cmb_total_yield, mass_window, ratio):
    lower, upper = mass_window
    data_hist = hist.Hist.new.Regular(100, lower, upper, flow=False, name="B_M").Double()
    data_hist.fill(data_array.B_M)

    plt.figure()
    mplhep.histplot(data_hist, yerr=True, color="black", label="data")
    x = np.linspace(lower, upper, 2000)
    cmb_shape_y = cmb_shape.pdf(x) * cmb_total_yield * (upper - lower) / 100
    plt.plot(x, cmb_shape_y, label="cmb")
    plt.axvline(x=5180, color="red", linestyle="--")
    bottom, top = plt.ylim()
    plt.text(lower + (upper - lower) * 0.2, top * 0.6, f"ratio: {ratio:.5f}")
    plt.legend()
    plt.xlim(mass_window[0], mass_window[1])
    plot_path = plot_cmb + "cmb_and_data.pdf"
    logger.info(f"saving plot to {plot_path}")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    plt.close()


def get_hist_and_ratio(data_array, cmb_shape, plot_cmb):
    cmb_normalisation_region = (5500, 6000)
    mass_window = (4000, 6000)
    split_point = 5180

    cmb_normalisation_region_cut = Cut(
        lambda x: (x.B_M > cmb_normalisation_region[0]) & (x.B_M < cmb_normalisation_region[1])
    )
    mass_window_cut = Cut(lambda x: (x.B_M > mass_window[0]) & (x.B_M < mass_window[1]))
    split_point_cut = Cut(lambda x: x.B_M < split_point)
    part_reco_cut = mass_window_cut & split_point_cut
    sig_cut = mass_window_cut & ~split_point_cut

    cmb_total_yield = (
        cmb_normalisation_region_cut.get_entries(data_array)
        / cmb_shape.integrate(cmb_normalisation_region, norm=mass_window)[0]
    )
    part_reco_yield = (
        part_reco_cut.get_entries(data_array)
        - cmb_total_yield * cmb_shape.integrate((mass_window[0], split_point), norm=mass_window)[0]
    )
    sig_yield = (
        sig_cut.get_entries(data_array)
        - cmb_total_yield * cmb_shape.integrate((split_point, mass_window[1]), norm=mass_window)[0]
    )

    ratio = part_reco_yield / sig_yield

    # logger.info(f"cmb_total_yield: {cmb_total_yield}")
    # logger.info(f"part_reco_yield: {part_reco_yield}")
    # logger.info(f"sig_yield: {sig_yield}")
    if plot_cmb is not None:
        plot_cmb_and_data(plot_cmb, data_array, cmb_shape, cmb_total_yield, mass_window, ratio)

    nbins = 50
    bin_width = (split_point - mass_window[0]) / nbins
    hist_lower = mass_window[0] - bin_width * 10
    hist_upper = split_point + bin_width * 10
    nbins += 20
    part_reco_region_data = part_reco_cut.apply(data_array)
    part_reco_region_hist = hist.Hist.new.Regular(nbins, hist_lower, hist_upper, flow=False, name="B_M").Double()
    part_reco_region_hist.fill(part_reco_region_data.B_M)

    binning = zfit.binned.RegularBinning(nbins, mass_window[0], split_point, name="B_M")
    binned_obs = zfit.Space("B_M", binning=binning)
    binned_pdf = cmb_shape.to_binned(binned_obs)
    cmb_hist = binned_pdf.to_hist()

    cmb_hist = (
        cmb_hist
        / cmb_hist.sum().value
        * zfit.run(cmb_total_yield * cmb_shape.integrate((mass_window[0], split_point), norm=mass_window)[0])
    )

    part_reco_hist = part_reco_region_hist - cmb_hist

    return part_reco_hist, ratio


def convolution_shape(cmb_shape, data_array, correction_function, name, plot_cmb):
    part_reco_hist, ratio = get_hist_and_ratio(data_array, cmb_shape, plot_cmb)
    part_reco_pdf = zfit.pdf.HistogramPDF(part_reco_hist)
    part_reco_unbinned = zfit.pdf.SplinePDF(part_reco_pdf, obs=zfit.Space("B_M", limits=(3000, 7000)))
    convolution_shape = zfit.pdf.FFTConvPDFV1(
        func=part_reco_unbinned,
        kernel=correction_function,
        name=f"convolution_shape_{name}",
        n=1000,
    )

    return convolution_shape, ratio, part_reco_hist


class CacheCmbShape:
    _all_cmb_shapes = {}

    @classmethod
    def __call__(cls, q2, year, pdf=None):
        name = f"{year}_{q2}"
        if pdf is None:
            if name in cls._all_cmb_shapes:
                return cls._all_cmb_shapes[name]
            else:
                return None
        else:
            cls._all_cmb_shapes[name] = pdf


def get_cmb_mm_shape(q2, obs, year):
    cached_shape = CacheCmbShape()
    comb_mm = cached_shape(q2, year)
    if comb_mm is None:
        name = f"{year}_{q2}"
        mu_cmb = zfit.Parameter(f"cmb_mm_mu_{name}", 4000, 3500, 5000)
        scale_cmb = zfit.Parameter(f"cmb_mm_scale_{name}", 10, 0.1, 100)
        a = zfit.Parameter(f"cmb_mm_a_{name}", -10, -20, 0)
        b = zfit.Parameter(f"cmb_mm_b_{name}", 1, 0, 10)
        comb_mm = SUJohnson(obs=obs, mu=mu_cmb, lm=scale_cmb, gamma=a, delta=b, name=f"comb_mm_{name}")
        pickle_path = (
            f"data/part_reco/comb_mm/latest/{q2}_{year}_B_M_NoBDTprc/{q2}_{year}_B_M_NoBDTprc_fit_result.pickle"
        )
        comb_mm = load_pdf(pickle_path, comb_mm)
        cached_shape(q2, year, comb_mm)
    return comb_mm


def plot(shape, hist, hist_y_upper, path_dir):
    os.makedirs(path_dir, exist_ok=True)
    # plot hist
    plt.figure()
    hist.plot()
    plt.xlim(4000, 6000)
    plt.ylim(0, hist_y_upper / (6000 - 4500) * (5180 - 4500))
    logger.info(f"saving plot to {path_dir}hist.pdf")
    plt.savefig(path_dir + "hist.pdf")
    plt.close()

    # plot shape
    plt.figure()
    x = np.linspace(3000, 7000, 2000)
    plt.plot(x, shape.pdf(x), label=shape.name)
    logger.info(f"saving plot to {path_dir}")
    plt.xlim(3000, 7000)
    plt.ylim(bottom=0)
    plt.axvline(x=4500, color="red", linestyle="--")
    plt.axvline(x=6000, color="red", linestyle="--")
    logger.info(f"saving plot to {path_dir}shape.pdf")
    plt.savefig(path_dir + "shape.pdf")
    plt.close()


def get_convolution_shape(kind, year, trigger, parameter_name_prefix="", *, plot_cmb=None):
    pickle_path = f"data/part_reco/fit_convolution/latest/{kind}/{year}_{trigger}/fit_result.pickle"
    obs = zfit.Space("B_M", limits=(4000, 6000))
    name = f"{kind}_{year}_{trigger}"
    if kind == "psi2S_high":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="psi2")
        obs_kernel = zfit.Space("B_M", limits=(-800, 1200))
        correction_function = get_correction_right_CB(
            obs_kernel, suffix=name, parameter_name_prefix=parameter_name_prefix
        )
        correction_function = load_pdf(pickle_path, correction_function, parameter_name_prefix)
        cmb_shape = get_cmb_mm_shape(q2="psi2", obs=obs, year=year)
        return convolution_shape(
            cmb_shape=cmb_shape,
            data_array=mm_data,
            correction_function=correction_function,
            name=name,
            plot_cmb=plot_cmb,
        )
    elif kind == "psi2S_psi2S":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="psi2")
        obs_kernel = zfit.Space("B_M", limits=(-1000, 1000))
        correction_function = get_correction_DSCB(obs_kernel, suffix=name, parameter_name_prefix=parameter_name_prefix)
        correction_function = load_pdf(pickle_path, correction_function, parameter_name_prefix)
        cmb_shape = get_cmb_mm_shape(q2="psi2", obs=obs, year=year)
        return convolution_shape(
            cmb_shape=cmb_shape,
            data_array=mm_data,
            correction_function=correction_function,
            name=name,
            plot_cmb=plot_cmb,
        )
    elif kind == "psi2S_Jpsi":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="psi2")
        obs_kernel = zfit.Space("B_M", limits=(-1200, 800))
        correction_function = get_correction_DSCB(obs_kernel, suffix=name, parameter_name_prefix=parameter_name_prefix)
        correction_function = load_pdf(pickle_path, correction_function, parameter_name_prefix)
        cmb_shape = get_cmb_mm_shape(q2="psi2", obs=obs, year=year)
        return convolution_shape(
            cmb_shape=cmb_shape,
            data_array=mm_data,
            correction_function=correction_function,
            name=name,
            plot_cmb=plot_cmb,
        )
    elif kind == "Jpsi_psi2S":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="jpsi")
        obs_kernel = zfit.Space("B_M", limits=(-800, 1200))
        correction_function = get_correction_DSCB(obs_kernel, suffix=name, parameter_name_prefix=parameter_name_prefix)
        correction_function = load_pdf(pickle_path, correction_function, parameter_name_prefix)
        cmb_shape = get_cmb_mm_shape(q2="jpsi", obs=obs, year=year)
        return convolution_shape(
            cmb_shape=cmb_shape,
            data_array=mm_data,
            correction_function=correction_function,
            name=name,
            plot_cmb=plot_cmb,
        )
    elif kind == "Jpsi_Jpsi":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="jpsi")
        obs_kernel = zfit.Space("B_M", limits=(-1000, 1000))
        correction_function = get_correction_DSCB(
            obs_kernel, suffix=name, parameter_name_prefix=parameter_name_parameter
        )
        correction_function = load_pdf(pickle_path, correction_function, parameter_name_prefix)
        cmb_shape = get_cmb_mm_shape(q2="jpsi", obs=obs, year=year)
        return convolution_shape(
            cmb_shape=cmb_shape,
            data_array=mm_data,
            correction_function=correction_function,
            name=name,
            plot_cmb=plot_cmb,
        )
    else:
        raise


def main(kind, year, trigger):
    project_root = get_project_root()
    plot_path = project_root + f"output/part_reco/convolution_shape/latest/{kind}/{year}_{trigger}/"
    shape, ratio, part_reco_hist = get_convolution_shape(kind, year, trigger, plot_cmb=f"{plot_path}")
    if kind.startswith("psi2S"):
        hist_y_upper = 14100
    else:
        hist_y_upper = 161000
    plot(shape, part_reco_hist, hist_y_upper, plot_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get convolution shape")
    parser.add_argument("--kind", type=str, help="kind of sample")
    parser.add_argument("--year", type=str, help="year")
    parser.add_argument("--trigger", type=str, help="trigger")
    args = parser.parse_args()
    main(args.kind, args.year, args.trigger)
