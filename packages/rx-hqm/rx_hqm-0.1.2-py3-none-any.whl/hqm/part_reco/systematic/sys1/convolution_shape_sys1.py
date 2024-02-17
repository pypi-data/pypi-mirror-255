import zfit
from zutils.pdf import SUJohnson
from hqm.tools.utility import get_project_root
from hqm.part_reco.fit_convolution import get_data
from hqm.part_reco.convolution_shape import get_cmb_mm_shape
from hqm.part_reco.convolution_shape import load_pdf
from hqm.part_reco.convolution_shape import convolution_shape
from hqm.part_reco.convolution_shape import plot
from hqm.part_reco.systematic.sys1.fit_convolution_sys1 import get_transfer_function_sys1

import argparse


def get_convolution_shape_sys1(kind, year, trigger, parameter_name_prefix="", *, plot_cmb=None):
    pickle_path = f"data/part_reco/fit_convolution/latest/sys1/latest/{kind}/{year}_{trigger}/fit_result.pickle"
    obs = zfit.Space("B_M", limits=(4000, 6000))
    name = f"{kind}_{year}_{trigger}"
    if kind == "psi2S_high":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="psi2")
        obs_kernel = zfit.Space("B_M", limits=(-800, 1200))
        correction_function = get_transfer_function_sys1(
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
        correction_function = get_transfer_function_sys1(
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
    elif kind == "psi2S_Jpsi":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="psi2")
        obs_kernel = zfit.Space("B_M", limits=(-1200, 800))
        correction_function = get_transfer_function_sys1(
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
    elif kind == "Jpsi_psi2S":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="jpsi")
        obs_kernel = zfit.Space("B_M", limits=(-800, 1200))
        correction_function = get_transfer_function_sys1(
            obs_kernel, suffix=name, parameter_name_prefix=parameter_name_prefix
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
    elif kind == "Jpsi_Jpsi":
        mm_data = get_data(kind="data", trigger="MTOS", year=year, q2="jpsi")
        obs_kernel = zfit.Space("B_M", limits=(-1000, 1000))
        correction_function = get_transfer_function_sys1(
            obs_kernel, suffix=name, parameter_name_prefix=parameter_name_prefix
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
    plot_path = project_root + f"output/part_reco/convolution_shape/latest/sys1/latest/{kind}/{year}_{trigger}/"
    shape, ratio, part_reco_hist = get_convolution_shape_sys1(kind, year, trigger, plot_cmb=f"{plot_path}")
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
