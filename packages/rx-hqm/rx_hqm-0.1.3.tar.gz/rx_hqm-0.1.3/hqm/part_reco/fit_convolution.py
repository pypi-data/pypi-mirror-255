import zfit
from hqm.tools.fit import fit
from hqm.tools.utility import get_project_root
from hqm.tools.utility import read_root
from hqm.tools.utility import cache_json
from hqm.tools.selection import selection
import argparse
import awkward as ak
import os
import matplotlib.pyplot as plt
import numpy as np
import hist
import mplhep
import matplotlib.pyplot as plt


def get_correction_DSCB(obs, suffix):
    mu = zfit.Parameter(f"correction_DSCB_mu_{suffix}", 0, -100, 100)
    sigma = zfit.Parameter(f"correction_DSCB_sigma_{suffix}", 40, 0.1, 100)
    al = zfit.Parameter(f"correction_DSCB_al_{suffix}", 1.5, 0.001, 10)
    nl = zfit.Parameter(f"correction_DSCB_nl_{suffix}", 1, 0.001, 110)
    ar = zfit.Parameter(f"correction_DSCB_ar_{suffix}", 1.5, 0.001, 10)
    nr = zfit.Parameter(f"correction_DSCB_nr_{suffix}", 1, 0.001, 110)

    correction_DSCB = zfit.pdf.DoubleCB(
        obs=obs, mu=mu, sigma=sigma, alphal=al, nl=nl, alphar=ar, nr=nr, name=f"correction_DSCB_{suffix}"
    )
    return correction_DSCB


def get_correction_left_CB(obs, suffix):
    mu = zfit.Parameter(f"correction_left_CB_mu_{suffix}", -100, -500, 0)
    sigma = zfit.Parameter(f"correction_left_CB_sigma_{suffix}", 5, 0.001, 100)
    alpha = zfit.Parameter(f"correction_left_CB_alpha_{suffix}", 0.5, 0.001, 2)
    n = zfit.Parameter(f"correction_left_CB_n_{suffix}", 50, 0.1, 110)

    correction_left_CB = zfit.pdf.CrystalBall(
        obs=obs, mu=mu, sigma=sigma, alpha=alpha, n=n, name=f"correction_left_CB_{suffix}"
    )
    return correction_left_CB


def get_correction_right_CB(obs, suffix):
    mu = zfit.Parameter(f"correction_right_CB_mu_{suffix}", 100, 0, 500)
    sigma = zfit.Parameter(f"correction_right_CB_sigma_{suffix}", 5, 0.001, 100)
    alpha = zfit.Parameter(f"correction_right_CB_alpha_{suffix}", -0.5, -2, -0.001)
    n = zfit.Parameter(f"correction_right_CB_n_{suffix}", 50, 0.1, 110)

    correction_right_CB = zfit.pdf.CrystalBall(
        obs=obs, mu=mu, sigma=sigma, alpha=alpha, n=n, name=f"correction_right_CB_{suffix}"
    )
    return correction_right_CB


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


class FitConvolution:
    def __init__(self, original_shape, target_data, correction_function, kind, year, trigger):
        self._original_shape = original_shape
        self._target_data = target_data
        self._correction_function = correction_function
        self._kind = kind
        self._year = year
        self._trigger = trigger

    def _get_convolution(self):
        model = zfit.pdf.FFTConvPDFV1(
            func=self._original_shape,
            kernel=self._correction_function,
            n=500,
            name=f"convolution_{self._kind}_{self._year}_{self._trigger}",
        )
        return model

    def _plot_original_shape(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        lower, upper = self._original_shape.space.limit1d
        data = zfit.run(self._original_shape._data)
        data_yield = len(data)
        data_hist = hist.Hist.new.Regular(100, lower, upper, overflow=False, name="B_M").Double()
        data_hist.fill(data)

        plt.figure()
        mplhep.histplot(data_hist, yerr=True, color="black", histtype="errorbar", label="MC")
        x = np.linspace(lower, upper, 2000)
        y = self._original_shape.pdf(x) * data_yield * (upper - lower) / 100
        plt.plot(x, y, label="KDE")
        plt.xlim(lower, upper)
        plt.ylim(bottom=0)
        plt.legend()
        plt.savefig(path)
        plt.close()

    def fit(self, systematic=None):
        model = self._get_convolution()

        dir_name = systematic + "/latest/" if systematic is not None else ""

        project_root = get_project_root()
        plot_kde_path = (
            project_root
            + f"output/part_reco/fit_convolution/latest/{dir_name}{self._kind}/{self._year}_{self._trigger}/kde.pdf"
        )
        self._plot_original_shape(plot_kde_path)

        fitter = fit(obs=self._original_shape.space, data=self._target_data)
        fitter.add_pdf(model)
        fitter.fit_data()

        plot_path = (
            project_root
            + f"output/part_reco/fit_convolution/latest/{dir_name}{self._kind}/{self._year}_{self._trigger}/fit_plot.pdf"
        )
        fitter.plot(plot_path=plot_path, leg={"Data": "ee MC"})

        pickle_path = (
            project_root
            + f"data/part_reco/fit_convolution/latest/{dir_name}{self._kind}/{self._year}_{self._trigger}/fit_result.pickle"
        )
        fitter.dump_result(pickle_path)

        return fitter.result


def get_data(kind, trigger, year, q2):
    @cache_json(f"get_data_{kind}_{trigger}_{year}_{q2}.json")
    def _get_data():
        if trigger in ["ETOS", "GTIS"]:
            category = "ee"
        elif trigger in ["MTOS"]:
            category = "mm"
        else:
            raise

        project_root = get_project_root()
        BDT_cmb = selection[category]["bdt_cmb"][trigger]
        BDT_prc = selection[category]["bdt_prc"][trigger]
        BDT = BDT_cmb & BDT_prc
        path = project_root + f"root_sample/v6/{kind}/v10.21p2/{year}_{trigger}/{q2}_nomass.root"
        data_array = read_root(path, trigger)
        data_array = BDT.apply(data_array)
        _data_array = {"B_M": ak.to_list(data_array.B_M)}
        return _data_array

    data = _get_data()
    data_ak = ak.zip(data)
    return data_ak


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
        correction_function = get_correction_right_CB(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit()

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
        correction_function = get_correction_DSCB(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit()

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
        correction_function = get_correction_DSCB(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit()

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
        correction_function = get_correction_DSCB(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit()

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
        correction_function = get_correction_DSCB(obs=obs_kernel, suffix=name)

        fit_obj = FitConvolution(
            original_shape=original_shape,
            target_data=target_data,
            correction_function=correction_function,
            kind=kind,
            year=year,
            trigger=trigger,
        )
        result = fit_obj.fit()
    else:
        raise

    plot_path = (
        get_project_root()
        + f"output/part_reco/fit_convolution/latest/{kind}/{year}_{trigger}/transfer_function_plot.pdf"
    )
    plot_pdf(pdf=correction_function, path=plot_path, result=result, suffix=name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", type=str, required=True)
    parser.add_argument("--year", type=str, required=True)
    parser.add_argument("--trigger", type=str, required=True)
    args = parser.parse_args()
    main(args.kind, args.year, args.trigger)
