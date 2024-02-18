from numpy.ma.core import concatenate
import zfit
from hqm.tools.utility import get_project_root
from hqm.tools.utility import load_pickle
from hqm.tools.utility import read_root
from hqm.tools.utility import get_shape
from hqm.tools.utility import cache_json
from hqm.tools.selection import selection
from hqm.tools.Cut import Cut
from monitor.ms_reader import ms_reader
import os
from logzero import logger
import pandas as pd
from stats.average import average
import numpy as np


class CacheMSReader:
    scales = None
    rdr = None

    def __init__(self):
        if CacheMSReader.scales is None:
            json_path = "signal_scales.json"

            @cache_json(json_path)
            def _get_scales():
                try:
                    caldir = os.environ["CASDIR"]
                except KeyError:
                    os.environ["CASDIR"] = "/publicfs/lhcb/user/campoverde/Data/cache"

                if CacheMSReader.rdr is None:
                    CacheMSReader.rdr = ms_reader(version="v4")

                scale_name = ["mu", "sg", "br"]
                all_scales = {}
                for scale in scale_name:
                    scale_df = CacheMSReader.rdr.get_scales(scale, avg_dset=True)
                    if scale in ["mu", "sg"]:
                        categories = ["MTOS", "ETOS", "GTIS"]
                        all_values = {}
                        for category in categories:
                            v = scale_df[f"v_{category}"].to_numpy()
                            e = scale_df[f"e_{category}"].to_numpy()
                            v_all, e_all, _ = average(v, e)
                            all_values[f"v_{category}"] = v_all
                            all_values[f"e_{category}"] = e_all
                            all_row = pd.Series(all_values)
                        scale_df.loc["all"] = all_row

                    else:
                        categories = ["0", "1", "2"]
                        triggers = ["MTOS", "ETOS", "GTIS"]
                        for trigger in triggers:
                            rows = [f"{trigger}_2018", f"{trigger}_2017", f"{trigger}_r1", f"{trigger}_r2p1"]
                            _scale_df = scale_df.loc[rows]
                            index_name = f"{trigger}_all"
                            all_values = {}
                            for category in categories:
                                v = _scale_df[f"v_{category}"].to_numpy()
                                e = _scale_df[f"e_{category}"].to_numpy()
                                v_all, e_all, _ = average(v, e)
                                all_values[f"v_{category}"] = v_all
                                all_values[f"e_{category}"] = e_all
                                all_row = pd.Series(all_values)
                            scale_df.loc[index_name] = all_row

                    all_scales[scale] = scale_df.to_dict(orient="tight")

                return all_scales

            all_scales = _get_scales()
            CacheMSReader.scales = {}
            for scale in all_scales:
                CacheMSReader.scales[scale] = pd.DataFrame.from_dict(all_scales[scale], orient="tight")

    def get_scale(self, scale):
        return CacheMSReader.scales[scale]


def load_pdf(pickle_path, pdf, parameter_name_prefix, parameter_list=None):
    json_path = pickle_path.replace("/", "_").removesuffix("pickle") + "json"
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    @cache_json(json_path)
    def _get_params():
        _pickle_path = get_project_root() + pickle_path
        obj = load_pickle(_pickle_path)
        fit_result = obj["result"]
        params_value = dict(fit_result.params)

        return params_value

    params_value = _get_params()
    if parameter_list is None:
        params = pdf.get_params()
    else:
        params = parameter_list
    for param in params:
        param_name = param.name.removeprefix(parameter_name_prefix)
        param_value = params_value[param_name]["value"]
        param.set_value(param_value)

    return pdf


def get_CB_ee_sys1(brem_category, obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix):
    parameter_name_prefix = parameter_name_prefix + "_sys1_" if parameter_name_prefix != "" else "sys1_"

    mu = zfit.Parameter(f"{parameter_name_prefix}mu_CB_ee_{suffix}", 5200, 5000, 5600)
    sigma = zfit.Parameter(f"{parameter_name_prefix}sigma_CB_ee_{suffix}", 10, 0.1, 500)
    _mu = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}mu_CB_{suffix}", lambda p: p["mu"] + p["dmu"], params={"mu": mu, "dmu": dmu}
    )
    _sigma = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}sigma_CB_{suffix}",
        lambda p: p["sigma"] * p["ssg"],
        params={"sigma": sigma, "ssg": ssg},
    )
    alpha = zfit.Parameter(f"{parameter_name_prefix}alpha_CB_ee_{suffix}", 1, 0, 10)
    n = zfit.Parameter(f"{parameter_name_prefix}n_CB_ee_{suffix}", 1, 0, 10)

    cb = zfit.pdf.CrystalBall(obs=obs, mu=_mu, sigma=_sigma, alpha=alpha, n=n, name=f"{pdf_name}_{suffix}")

    pickle_name = f"fit_Bu2Kee_MC_{brem_category}_{dataset}_{trigger}.pickle"
    pickle_path = f"data/signal_shape_ee/latest/sys1/latest/{pickle_name}"
    parameter_list = [mu, sigma, alpha, n]
    cb = load_pdf(pickle_path, cb, parameter_name_prefix.removesuffix("_"), parameter_list)

    for param in parameter_list:
        param.floating = False
    return cb


def get_3Gauss_ee_sys1(brem_category, obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix):
    parameter_name_prefix = parameter_name_prefix + "_sys1_" if parameter_name_prefix != "" else "sys1_"

    mu1 = zfit.Parameter(f"{parameter_name_prefix}mu1_3Gauss_ee_{suffix}", 5200, 5000, 5600)
    sigma1 = zfit.Parameter(f"{parameter_name_prefix}sigma1_3Gauss_ee_{suffix}", 10, 0.1, 100)
    _mu1 = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}mu_3Gauss_ee_{suffix}", lambda p: p["mu"] + p["dmu"], params={"mu": mu1, "dmu": dmu}
    )
    _sigma1 = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}sigma_3Gauss_ee_{suffix}",
        lambda p: p["sigma"] * p["ssg"],
        params={"sigma": sigma1, "ssg": ssg},
    )

    mu2 = zfit.Parameter(f"{parameter_name_prefix}mu2_3Gauss_ee_{suffix}", 5200, 5000, 5600)
    mu3 = zfit.Parameter(f"{parameter_name_prefix}mu3_3Gauss_ee_{suffix}", 5200, 5000, 5600)

    sigma2 = zfit.Parameter(f"{parameter_name_prefix}sigma2_3Gauss_ee_{suffix}", 110, 100, 150)
    sigma3 = zfit.Parameter(f"{parameter_name_prefix}sigma3_3Gauss_ee_{suffix}", 160, 150, 500)

    frac1 = zfit.Parameter(f"{parameter_name_prefix}frac1_3Gauss_ee_{suffix}", 0.5, 0, 1)
    _frac2 = zfit.Parameter(f"{parameter_name_prefix}_frac2_3Gauss_ee_{suffix}", 0.5, 0, 1)
    frac2 = zfit.param.ComposedParameter(
        f"{parameter_name_prefix}frac2_3Gauss_ee_{suffix}",
        lambda p: (1 - p["frac1"]) * p["_frac2"],
        params={"frac1": frac1, "_frac2": _frac2},
    )

    gauss1 = zfit.pdf.Gauss(obs=obs, mu=_mu1, sigma=_sigma1, name=f"gauss1_3Gauss_ee_{suffix}")
    gauss2 = zfit.pdf.Gauss(obs=obs, mu=mu2, sigma=sigma2, name=f"gauss2_3Gauss_ee_{suffix}")
    gauss3 = zfit.pdf.Gauss(obs=obs, mu=mu3, sigma=sigma3, name=f"gauss3_3Gauss_ee_{suffix}")

    total_pdf = zfit.pdf.SumPDF([gauss1, gauss2, gauss3], fracs=[frac1, frac2], name=f"{pdf_name}_{suffix}")

    pickle_name = f"fit_Bu2Kee_MC_{brem_category}_{dataset}_{trigger}.pickle"
    pickle_path = f"data/signal_shape_ee/latest/sys1/latest/{pickle_name}"
    parameter_list = [mu1, sigma1, mu2, mu3, sigma2, sigma3, frac1, _frac2]
    total_pdf = load_pdf(pickle_path, total_pdf, parameter_name_prefix.removesuffix("_"), parameter_list)

    for param in parameter_list:
        param.floating = False
    return total_pdf


def get_DSCB_ee_nom(brem_category, obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    mu = zfit.Parameter(f"{parameter_name_prefix}mu_DSCB_{suffix}", 5200, 5000, 5600)
    _mu = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}mu_DSCB_{suffix}", lambda p: p["mu"] + p["dmu"], params={"mu": mu, "dmu": dmu}
    )
    sigma = zfit.Parameter(f"{parameter_name_prefix}sigma_DSCB_{suffix}", 10, 0.1, 500)
    _sigma = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}sigma_DSCB_{suffix}",
        lambda p: p["sigma"] * p["ssg"],
        params={"sigma": sigma, "ssg": ssg},
    )
    alphal = zfit.Parameter(f"{parameter_name_prefix}alphal_DSCB_{suffix}", 1, 0, 20)
    nl = zfit.Parameter(f"{parameter_name_prefix}nl_DSCB_{suffix}", 1, 0, 150)
    alphar = zfit.Parameter(f"{parameter_name_prefix}alphar_DSCB_{suffix}", 1, 0, 20)
    nr = zfit.Parameter(f"{parameter_name_prefix}nr_DSCB_{suffix}", 1, 0, 120)

    dscb = zfit.pdf.DoubleCB(
        mu=_mu,
        sigma=_sigma,
        alphal=alphal,
        nl=nl,
        alphar=alphar,
        nr=nr,
        obs=obs,
        name=f"{pdf_name}_{suffix}",
    )

    pickle_name = f"fit_Bu2Kee_MC_{brem_category}_{dataset}_{trigger}.pickle"
    pickle_path = f"data/signal_shape_ee/latest/{pickle_name}"
    parameter_list = [mu, sigma, alphal, nl, alphar, nr]
    dscb = load_pdf(pickle_path, dscb, parameter_name_prefix.removesuffix("_"), parameter_list)

    for param in parameter_list:
        param.floating = False

    return dscb


def load_signal_ee_brem(brem_category, obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, systematic):
    suffix = f"{brem_category}_{dataset}_{trigger}"

    if systematic == "nom":
        pdf = get_DSCB_ee_nom(brem_category, obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix)
    elif systematic == "sys1":
        if brem_category == 0:
            pdf = get_CB_ee_sys1(
                brem_category, obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix
            )
        else:
            pdf = get_3Gauss_ee_sys1(
                brem_category, obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix
            )
    else:
        raise ValueError(f"Systematic {systematic} not recognized")
    return pdf


def get_signal_ee(dataset, trigger, parameter_name_prefix="", pdf_name="signal_ee", systematic="nom"):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else parameter_name_prefix

    scale_reader = CacheMSReader()

    all_mu = scale_reader.get_scale("mu")
    dmu_value = all_mu.loc[f"{dataset}", f"v_{trigger}"]
    dmu_error = all_mu.loc[f"{dataset}", f"e_{trigger}"]

    all_sg = scale_reader.get_scale("sg")
    ssg_value = all_sg.loc[f"{dataset}", f"v_{trigger}"]
    ssg_error = all_sg.loc[f"{dataset}", f"e_{trigger}"]

    all_br = scale_reader.get_scale("br")
    r0_value = all_br.loc[f"{trigger}_{dataset}", "v_0"]
    r0_error = all_br.loc[f"{trigger}_{dataset}", "e_0"]
    r1_value = all_br.loc[f"{trigger}_{dataset}", "v_1"]
    r1_error = all_br.loc[f"{trigger}_{dataset}", "e_1"]
    r2_value = all_br.loc[f"{trigger}_{dataset}", "v_2"]
    r2_error = all_br.loc[f"{trigger}_{dataset}", "e_2"]

    suffix = f"{dataset}_{trigger}"
    dmu = zfit.Parameter(f"{systematic}_{parameter_name_prefix}dmu_ee_{suffix}", dmu_value, -100, 100)
    ssg = zfit.Parameter(f"{systematic}_{parameter_name_prefix}ssg_ee_{suffix}", ssg_value, 0.01, 3)
    r0 = zfit.Parameter(f"{systematic}_{parameter_name_prefix}r0_ee_{suffix}", r0_value, 0.01, 3)
    r1 = zfit.Parameter(f"{systematic}_{parameter_name_prefix}r1_ee_{suffix}", r1_value, 0.01, 3)
    r2 = zfit.Parameter(f"{systematic}_{parameter_name_prefix}r2_ee_{suffix}", r2_value, 0.01, 3)

    constraints = {
        dmu.name: [dmu_value, dmu_error],
        ssg.name: [ssg_value, ssg_error],
        r0.name: [r0_value, r0_error],
        r1.name: [r1_value, r1_error],
        r2.name: [r2_value, r2_error],
    }

    obs = zfit.Space("B_M", limits=(4500, 6000))

    dscbs = []
    for brem_category in range(3):
        dscb = load_signal_ee_brem(
            brem_category,
            obs,
            dataset,
            trigger,
            dmu,
            ssg,
            parameter_name_prefix.removesuffix("_"),
            pdf_name,
            systematic,
        )
        dscbs.append(dscb)

    MC_brem_fraction_json_path = f"MC_brem_fraction_{dataset}_{trigger}.json"

    @cache_json(MC_brem_fraction_json_path)
    def _get_MC_brem_fraction():
        def _get_MC_brem_fraction_year():
            bdt_cmb = selection["ee"]["bdt_cmb"][trigger]
            bdt_prc = selection["ee"]["bdt_prc"][trigger]
            bdt = bdt_cmb & bdt_prc
            sign_MC_path = get_project_root() + f"root_sample/v6/sign/v10.21p2/{year}_{trigger}/high_normal.root"
            sign_MC = read_root(sign_MC_path, trigger)
            sign_MC = bdt.apply(sign_MC)

            total_n = len(sign_MC)
            brem_0 = Cut(lambda x: x.L1_BremMultiplicity + x.L2_BremMultiplicity == 0)
            brem_1 = Cut(lambda x: x.L1_BremMultiplicity + x.L2_BremMultiplicity == 1)
            brem_2 = Cut(lambda x: x.L1_BremMultiplicity + x.L2_BremMultiplicity >= 2)

            f0 = brem_0.get_entries(sign_MC) / total_n
            f1 = brem_1.get_entries(sign_MC) / total_n
            f2 = brem_2.get_entries(sign_MC) / total_n

            return f0, f1, f2

        if dataset == "all":
            years = ["2011", "2012", "2015", "2016", "2017", "2018"]
        elif dataset == "r1":
            years = ["2011", "2012"]
        elif dataset == "r2p1":
            years = ["2015", "2016"]
        else:
            years = [dataset]
        all_f0 = []
        all_f1 = []
        all_f2 = []
        for year in years:
            f0, f1, f2 = _get_MC_brem_fraction_year()
            all_f0.append(f0)
            all_f1.append(f1)
            all_f2.append(f2)

        f0 = sum(all_f0) / len(all_f0)
        f1 = sum(all_f1) / len(all_f1)
        f2 = sum(all_f2) / len(all_f2)

        all_fs = {"f0": f0, "f1": f1, "f2": f2}
        return all_fs

    all_fs = _get_MC_brem_fraction()
    f0 = all_fs["f0"]
    f1 = all_fs["f1"]
    f2 = all_fs["f2"]

    f0_corrected = zfit.param.ComposedParameter(
        f"{systematic}_{parameter_name_prefix}f0_corrected_{suffix}",
        lambda p: f0 * p["r0"] / (f0 * p["r0"] + f1 * p["r1"] + f2 * p["r2"]),
        params={"r0": r0, "r1": r1, "r2": r2},
    )
    f1_corrected = zfit.param.ComposedParameter(
        f"{systematic}_{parameter_name_prefix}f1_corrected_{suffix}",
        lambda p: f1 * p["r1"] / (f0 * p["r0"] + f1 * p["r1"] + f2 * p["r2"]),
        params={"r0": r0, "r1": r1, "r2": r2},
    )

    total_ee_shape = zfit.pdf.SumPDF(dscbs, [f0_corrected, f1_corrected], name=f"{pdf_name}_{dataset}_{trigger}")
    return total_ee_shape, constraints


def get_DSCB_mm_nom(obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    mu = zfit.Parameter(f"{parameter_name_prefix}mu_DSCB_mm_{suffix}", 5250, 5180, 5600)
    sigma = zfit.Parameter(f"{parameter_name_prefix}sigma_DSCB_mm_{suffix}", 30, 0, 100)
    _mu = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}mu_DSCB_mm_{suffix}", lambda p: p["mu"] + p["dmu"], params={"mu": mu, "dmu": dmu}
    )

    _sigma = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}sigma_DSCB_mm_{suffix}",
        lambda p: p["sigma"] * p["ssg"],
        params={"sigma": sigma, "ssg": ssg},
    )

    alphal = zfit.Parameter(f"{parameter_name_prefix}alphal_DSCB_mm_{suffix}", 1, 0, 10)
    nl = zfit.Parameter(f"{parameter_name_prefix}nl_DSCB_mm_{suffix}", 1, 0, 100)
    alphar = zfit.Parameter(f"{parameter_name_prefix}alphar_DSCB_mm_{suffix}", 1, 0, 10)
    nr = zfit.Parameter(f"{parameter_name_prefix}nr_DSCB_mm_{suffix}", 1, 0, 100)
    DSCB_mm = zfit.pdf.DoubleCB(
        obs=obs,
        mu=_mu,
        sigma=_sigma,
        alphal=alphal,
        nl=nl,
        alphar=alphar,
        nr=nr,
        name=f"{pdf_name}_{dataset}_{trigger}",
    )

    pickle_name = f"fit_Bu2Kmm_MC_{dataset}_{trigger}.pickle"
    pickle_path = f"data/signal_shape_mm/latest/{pickle_name}"

    parameter_list = [mu, sigma, alphal, nl, alphar, nr]
    DSCB_mm = load_pdf(pickle_path, DSCB_mm, parameter_name_prefix.removesuffix("_"), parameter_list)

    for param in parameter_list:
        param.floating = False
    return DSCB_mm


def get_2Gauss_mm_sys1(obs, dataset, trigger, dmu, ssg, parameter_name_prefix, pdf_name, suffix):
    parameter_name_prefix = parameter_name_prefix + "_sys1_" if parameter_name_prefix != "" else "sys1_"

    mu1 = zfit.Parameter(f"{parameter_name_prefix}mu1_2Gauss_mm_{suffix}", 5250, 5180, 5600)
    sigma1 = zfit.Parameter(f"{parameter_name_prefix}sigma1_2Gauss_mm_{suffix}", 10, 0.1, 30)
    _mu1 = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}mu_2Gauss_mm_{suffix}", lambda p: p["mu"] + p["dmu"], params={"mu": mu1, "dmu": dmu}
    )

    _sigma1 = zfit.param.ComposedParameter(
        f"_{parameter_name_prefix}sigma_DSCB_mm_{suffix}",
        lambda p: p["sigma"] * p["ssg"],
        params={"sigma": sigma1, "ssg": ssg},
    )

    mu2 = zfit.Parameter(f"{parameter_name_prefix}mu2_2Gauss_mm_{suffix}", 5250, 5180, 5600)
    sigma2 = zfit.Parameter(f"{parameter_name_prefix}sigma2_2Gauss_mm_{suffix}", 40, 30, 50)

    frac1 = zfit.Parameter(f"{parameter_name_prefix}frac1_2Gauss_mm_{suffix}", 0.5, 0, 1)

    gauss1 = zfit.pdf.Gauss(obs=obs, mu=_mu1, sigma=_sigma1, name=f"gauss1_2Gauss_mm_{suffix}")
    gauss2 = zfit.pdf.Gauss(obs=obs, mu=mu2, sigma=sigma2, name=f"gauss2_2Gauss_mm_{suffix}")

    total = zfit.pdf.SumPDF([gauss1, gauss2], fracs=[frac1], name=f"{pdf_name}_{suffix}")

    pickle_name = f"fit_Bu2Kmm_MC_{dataset}_{trigger}.pickle"
    pickle_path = f"data/signal_shape_mm/latest/sys1/latest/{pickle_name}"

    parameter_list = [mu1, sigma1, mu2, sigma2, frac1]
    total = load_pdf(pickle_path, total, parameter_name_prefix.removesuffix("_"), parameter_list)

    for param in parameter_list:
        param.floating = False
    return total


def get_signal_mm(dataset, trigger, parameter_name_prefix="", pdf_name="", systematic="nom"):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    scale_reader = CacheMSReader()
    all_mu = scale_reader.get_scale("mu")
    dmu_value = all_mu.loc[f"{dataset}", f"v_{trigger}"]
    dmu_error = all_mu.loc[f"{dataset}", f"e_{trigger}"]
    all_sg = scale_reader.get_scale("sg")
    ssg_value = all_sg.loc[f"{dataset}", f"v_{trigger}"]
    ssg_error = all_sg.loc[f"{dataset}", f"e_{trigger}"]

    suffix = f"{dataset}_{trigger}"
    dmu = zfit.Parameter(f"{systematic}_{parameter_name_prefix}dmu_mm_{suffix}", dmu_value, -100, 100)
    ssg = zfit.Parameter(f"{systematic}_{parameter_name_prefix}ssg_mm_{suffix}", ssg_value, 0.01, 3)

    constraints = {dmu.name: [dmu_value, dmu_error], ssg.name: [ssg_value, ssg_error]}

    obs = zfit.Space("B_M", limits=(5180, 5600))
    if systematic == "nom":
        pdf = get_DSCB_mm_nom(
            obs, dataset, trigger, dmu, ssg, parameter_name_prefix.removesuffix("_"), pdf_name, suffix
        )
    elif systematic == "sys1":
        pdf = get_2Gauss_mm_sys1(
            obs, dataset, trigger, dmu, ssg, parameter_name_prefix.removesuffix("_"), pdf_name, suffix
        )
    else:
        raise ValueError(f"Systematic {systematic} not recognized")

    return pdf, constraints


def get_signal_shape(dataset="2018", trigger="ETOS", parameter_name_prefix="", systematic="nom"):
    if trigger in ["ETOS", "GTIS"]:
        return get_signal_ee(
            dataset, trigger, parameter_name_prefix=parameter_name_prefix, pdf_name="signal_ee", systematic=systematic
        )
    elif trigger == "MTOS":
        return get_signal_mm(
            dataset, trigger, parameter_name_prefix=parameter_name_prefix, pdf_name="signal_mm", systematic=systematic
        )
    else:
        raise ValueError(f"Unknown trigger: {trigger}")
