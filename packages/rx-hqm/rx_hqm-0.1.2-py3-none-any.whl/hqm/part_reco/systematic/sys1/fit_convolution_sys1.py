import zfit
from hqm.tools.utility import get_project_root
from zutils.pdf import SUJohnson
from hqm.part_reco.fit_convolution import FitConvolution
from hqm.part_reco.fit_convolution import get_data
import argparse
import awkward as ak
import os
import matplotlib.pyplot as plt
import numpy as np


def get_transfer_function_sys1(obs, suffix, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    # 3 Gauss
    mu1 = zfit.Parameter(f"{parameter_name_prefix}mu1_3Gauss_{suffix}", 0, -800, 800)
    mu2 = zfit.Parameter(f"{parameter_name_prefix}mu2_3Gauss_{suffix}", 0, -800, 800)
    mu3 = zfit.Parameter(f"{parameter_name_prefix}mu3_3Gauss_{suffix}", 0, -800, 800)

    sigma1 = zfit.Parameter(f"{parameter_name_prefix}sigma1_3Gauss_{suffix}", 10, 0.1, 40)
    sigma2 = zfit.Parameter(f"{parameter_name_prefix}sigma2_3Gauss_{suffix}", 60, 40, 80)
    sigma3 = zfit.Parameter(f"{parameter_name_prefix}sigma3_3Gauss_{suffix}", 90, 80, 500)

    frac1 = zfit.Parameter(f"{parameter_name_prefix}frac1_3Gauss_{suffix}", 0.5, 0, 1)
    _frac2 = zfit.Parameter(f"{parameter_name_prefix}_frac2_3Gauss_{suffix}", 0.5, 0, 1)
    frac2 = zfit.param.ComposedParameter(
        f"{parameter_name_prefix}frac2_3Gauss_{suffix}",
        lambda p: (1 - p["frac1"]) * p["_frac2"],
        {"frac1": frac1, "_frac2": _frac2},
    )

    gauss1 = zfit.pdf.Gauss(obs=obs, mu=mu1, sigma=sigma1, name=f"gauss1_3Gauss_{suffix}")
    gauss2 = zfit.pdf.Gauss(obs=obs, mu=mu2, sigma=sigma2, name=f"gauss2_3Gauss_{suffix}")
    gauss3 = zfit.pdf.Gauss(obs=obs, mu=mu3, sigma=sigma3, name=f"gauss3_3Gauss_{suffix}")

    total = zfit.pdf.SumPDF([gauss1, gauss2, gauss3], fracs=[frac1, frac2], name=f"3Gauss_{suffix}")
    return total


def plot_pdf(pdf, path, result, suffix):
    lower, upper = pdf.space.limit1d
    x = np.linspace(lower, upper, 2000)
    y = pdf.pdf(x)
    plt.figure()
    plt.plot(x, y)
    text = ""
    for param in pdf.get_params():
        text += f"{param.name.removeprefix('correction_').removeprefix('left_').removeprefix('right_').removesuffix(f'_{suffix}')} = {result.params[param.name]['value']:.4f} +/- {result.params[param.name]['hesse']['error']:.4f}\n"
    plt.xlim(lower, upper)
    plt.ylim(bottom=0)
    bottom, top = plt.ylim()
    plt.text(lower + (upper - lower) * 0.6, top * 0.6, text)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path)
    plt.close()


def main(kind, year, trigger):
    bandwidth = 10
    name = f"{kind}_{year}_{trigger}"
    if kind == "psi2S_high":
        obs = zfit.Space("B_M", limits=(5000, 7000))
        obs_kernel = zfit.Space("B_M", limits=(-800, 1200))

        mm_data = get_data(kind="psi2", trigger="MTOS", year=year, q2="psi2")
        ee_data = get_data(kind="psi2", trigger=trigger, year=year, q2="high")

        mm_zdata = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(mm_data.B_M))
        original_shape = zfit.pdf.KDE1DimFFT(
            obs=obs, data=mm_zdata, name=f"psi2SK_mm_{year}_{trigger}", bandwidth=bandwidth
        )
        target_data = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(ee_data.B_M))
        correction_function = get_transfer_function_sys1(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit(systematic="sys1")

    elif kind == "psi2S_psi2S":
        obs = zfit.Space("B_M", limits=(4200, 6200))
        obs_kernel = zfit.Space("B_M", limits=(-1000, 1000))

        mm_data = get_data(kind="psi2", trigger="MTOS", year=year, q2="psi2")
        ee_data = get_data(kind="psi2", trigger=trigger, year=year, q2="psi2")

        mm_zdata = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(mm_data.B_M))
        original_shape = zfit.pdf.KDE1DimFFT(
            obs=obs, data=mm_zdata, name=f"psi2SK_mm_{year}_{trigger}", bandwidth=bandwidth
        )
        target_data = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(ee_data.B_M))
        correction_function = get_transfer_function_sys1(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit(systematic="sys1")

    elif kind == "psi2S_Jpsi":
        obs = zfit.Space("B_M", limits=(3500, 5500))
        obs_kernel = zfit.Space("B_M", limits=(-1200, 800))

        mm_data = get_data(kind="psi2", trigger="MTOS", year=year, q2="psi2")
        ee_data = get_data(kind="psi2", trigger=trigger, year=year, q2="jpsi")

        mm_zdata = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(mm_data.B_M))
        original_shape = zfit.pdf.KDE1DimFFT(
            obs=obs, data=mm_zdata, name=f"psi2SK_mm_{year}_{trigger}", bandwidth=bandwidth
        )
        target_data = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(ee_data.B_M))
        correction_function = get_transfer_function_sys1(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit(systematic="sys1")

    elif kind == "Jpsi_psi2S":
        obs = zfit.Space("B_M", limits=(4200, 6200))
        obs_kernel = zfit.Space("B_M", limits=(-800, 1200))

        mm_data = get_data(kind="ctrl", trigger="MTOS", year=year, q2="jpsi")
        ee_data = get_data(kind="ctrl", trigger=trigger, year=year, q2="psi2")

        mm_zdata = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(mm_data.B_M))
        original_shape = zfit.pdf.KDE1DimFFT(
            obs=obs, data=mm_zdata, name=f"JpsiK_mm_{year}_{trigger}", bandwidth=bandwidth
        )
        target_data = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(ee_data.B_M))
        correction_function = get_transfer_function_sys1(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit(systematic="sys1")

    elif kind == "Jpsi_Jpsi":
        obs = zfit.Space("B_M", limits=(4200, 6200))
        obs_kernel = zfit.Space("B_M", limits=(-1000, 1000))

        mm_data = get_data(kind="ctrl", trigger="MTOS", year=year, q2="jpsi")
        ee_data = get_data(kind="ctrl", trigger=trigger, year=year, q2="jpsi")

        mm_zdata = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(mm_data.B_M))
        original_shape = zfit.pdf.KDE1DimFFT(
            obs=obs, data=mm_zdata, name=f"JpsiK_mm_{year}_{trigger}", bandwidth=bandwidth
        )
        target_data = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(ee_data.B_M))
        correction_function = get_transfer_function_sys1(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit(systematic="sys1")
    else:
        raise

    dir_name = "sys1/latest/"
    plot_path = (
        get_project_root()
        + f"output/part_reco/fit_convolution/latest/{dir_name}{kind}/{year}_{trigger}/transfer_function_plot.pdf"
    )
    plot_pdf(pdf=correction_function, path=plot_path, result=result, suffix=name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", type=str, required=True)
    parser.add_argument("--year", type=str, required=True)
    parser.add_argument("--trigger", type=str, required=True)
    args = parser.parse_args()
    main(args.kind, args.year, args.trigger)
