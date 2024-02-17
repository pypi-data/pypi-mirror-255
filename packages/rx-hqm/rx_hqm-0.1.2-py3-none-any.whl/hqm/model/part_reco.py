from hqm.part_reco.convolution_shape import get_convolution_shape
from hqm.part_reco.systematic.sys1.convolution_shape_sys1 import get_convolution_shape_sys1
from .KDE_shape import get_KDE_shape
from hqm.tools.utility import get_lumi
from logzero import logger
import zfit


def get_shape(dataset, trigger, func, *, parameter_name_prefix="", pdf_name="", **kwargs):
    if dataset in ["2017", "2018"]:
        return_value = func(
            year=dataset, trigger=trigger, parameter_name_prefix=parameter_name_prefix, pdf_name=pdf_name, **kwargs
        )
    else:
        if dataset == "r1":
            years = ["2011", "2012"]
        elif dataset == "r2p1":
            years = ["2015", "2016"]
        elif dataset == "all":
            years = ["2011", "2012", "2015", "2016", "2017", "2018"]
        else:
            logger.error(f"Invalid dataset: {dataset}")
            raise

        values = [
            func(year=year, trigger=trigger, parameter_name_prefix=parameter_name_prefix, pdf_name=pdf_name, **kwargs)
            for year in years
        ]
        lumis = [get_lumi(year) for year in years]
        sum_lumis = sum(lumis)
        frac = [lumi / sum_lumis for lumi in lumis[:-1]]

        pdfs = []
        ratios = []
        for i, value in enumerate(values):
            pdf, ratio = value
            pdfs.append(pdf)
            ratios.append(ratio * lumis[i])
        total_pdf = zfit.pdf.SumPDF(pdfs, fracs=frac, name=f"{pdf_name}_{dataset}_{trigger}")
        average_ratio = sum(ratios) / sum_lumis
        return_value = (total_pdf, average_ratio)

    return return_value


def _get_part_reco(year="2018", trigger="ETOS", parameter_name_prefix="", pdf_name="", systematic="nom"):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""
    suffix = f"{year}_{trigger}"

    if systematic == "nom":
        psi2S_part_reco_shape, psi2S_ratio, _ = get_convolution_shape(
            kind="psi2S_high",
            year=year,
            trigger=trigger,
            parameter_name_prefix=parameter_name_prefix.removesuffix("_"),
        )
    elif systematic == "sys1":
        psi2S_part_reco_shape, psi2S_ratio, _ = get_convolution_shape_sys1(
            kind="psi2S_high",
            year=year,
            trigger=trigger,
            parameter_name_prefix=parameter_name_prefix.removesuffix("_"),
        )
    else:
        raise ValueError(f"Invalid systematic: {systematic}")

    for param in psi2S_part_reco_shape.get_params():
        param.floating = False

    mass_window = (4500, 6000)

    psi2S_ratio *= psi2S_part_reco_shape.integrate(mass_window)[0]

    return psi2S_part_reco_shape, psi2S_ratio


def get_part_reco(dataset="2018", trigger="ETOS", parameter_name_prefix="", systematic="nom", bts_index=0):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""
    part_reco_shape, ratio = get_shape(
        dataset,
        trigger,
        _get_part_reco,
        parameter_name_prefix=parameter_name_prefix,
        pdf_name="part_reco",
        systematic=systematic,
    )

    mass_window = (4500, 6000)
    binning = zfit.binned.RegularBinning(100, 4500, 6000, name="B_M")
    binned_obs = zfit.Space(obs="B_M", limits=mass_window, binning=binning)
    part_reco_shape_binned = part_reco_shape.to_binned(binned_obs)

    part_reco_shape_hist = part_reco_shape_binned.to_hist()
    part_reco_shape_hist_pdf = zfit.pdf.HistogramPDF(part_reco_shape_hist, extended=False)

    obs = zfit.Space("B_M", limits=(4500, 6000))
    part_reco_shape_hist_pdf_unbinned = zfit.pdf.SplinePDF(part_reco_shape_hist_pdf, obs=obs)

    psi2SK_shape = get_KDE_shape(
        obs, "psi2", "high", bandwidth=None, dataset=dataset, trigger=trigger, pdf_name="psi2SK", bts_index=bts_index
    )
    ratio /= psi2SK_shape.integrate(mass_window)[0]

    suffix = f"{dataset}_{trigger}_{systematic}_{bts_index}"
    psi2S_ratio_param = zfit.Parameter(f"{parameter_name_prefix}psi2S_ratio_{suffix}", ratio, 0.1, 10)
    frac = zfit.param.ComposedParameter(
        f"{parameter_name_prefix}frac_{suffix}", lambda p: p / (p + 1), psi2S_ratio_param
    )

    total_pdf = zfit.pdf.SumPDF(
        [part_reco_shape_hist_pdf_unbinned, psi2SK_shape], fracs=[frac], name=f"part_reco_{suffix}"
    )

    return total_pdf, {psi2S_ratio_param.name: [zfit.run(ratio), zfit.run(ratio) * 0.1]}
