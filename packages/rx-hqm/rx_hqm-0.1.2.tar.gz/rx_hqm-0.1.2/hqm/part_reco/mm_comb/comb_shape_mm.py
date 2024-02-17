# get the shape of the combinatorial background in the mm channel by inverting the BDT_cmb cut

import zfit
from hqm.tools.utility import get_project_root
import awkward as ak
from hqm.tools.fit import fit
import argparse
from logzero import logger
from hqm.tools.Cut import Cut
from hqm.tools.utility import read_root
from hqm.tools.selection import selection
from zutils.pdf import SUJohnson


class fit_invert_BDT_mm(fit):
    def __init__(self, output_dir_suffix="_mm", **kwargs):
        super().__init__(**kwargs)
        self._output_dir_suffix = output_dir_suffix

    def run(self, output_dirname):
        self.fit_data()
        plot_dir = self._project_root + f"output/part_reco/comb{self._output_dir_suffix}/latest/{output_dirname}/"
        pickle_dir = self._project_root + f"data/part_reco/comb{self._output_dir_suffix}/latest/{output_dirname}/"

        self.plot(plot_dir + f"{output_dirname}_fit_plot.pdf")
        self.plot(plot_dir + f"{output_dirname}_fit_plot_log.pdf", ylog=True)

        self.dump_result(pickle_dir + f"{output_dirname}_fit_result.pickle")


class comb_shape_mm:
    _project_root = get_project_root()

    def __init__(self, q2, year, mass_variable, obs=None, with_bdt_prc=True):
        self._q2 = q2
        self._year = year
        self._mass_variable = mass_variable
        self._with_bdt_prc = with_bdt_prc

        if obs is None:
            self._obs = zfit.Space(mass_variable, limits=(4000, 6000))
        else:
            self._obs = obs

    def _get_bdt_cut(self):
        bdt_prc_cut = selection["mm"]["bdt_prc"]["MTOS"]
        invert_bdt_cmb_cut = Cut(lambda x: x.BDT_cmb < 0.2)
        if self._with_bdt_prc:
            total_bdt_cut = bdt_prc_cut & invert_bdt_cmb_cut
        else:
            total_bdt_cut = invert_bdt_cmb_cut
        return total_bdt_cut

    def _get_cut(self):
        cut = self._get_bdt_cut()
        return cut

    def _get_data(self):
        path = self._project_root + f"root_sample/v6/data/v10.21p2/{self._year}_MTOS/{self._q2}_nomass.root"
        data_array = read_root(path, "MTOS")
        cut = self._get_cut()
        data_array = cut.apply(data_array)
        return data_array

    def _get_comb(self):
        # SUJohnson for combinatorial background
        name = f"{self._year}_{self._q2}"
        mu_cmb = zfit.Parameter(f"cmb_mm_mu_{name}", 4000, 3500, 5000)
        scale_cmb = zfit.Parameter(f"cmb_mm_scale_{name}", 10, 0.1, 100)
        a = zfit.Parameter(f"cmb_mm_a_{name}", -10, -20, 0)
        b = zfit.Parameter(f"cmb_mm_b_{name}", 1, 0, 10)
        comb_mm = SUJohnson(obs=self._obs, mu=mu_cmb, lm=scale_cmb, gamma=a, delta=b, name=f"comb_mm_{name}")

        return comb_mm

    def _get_signal(self):
        # gaussian for signal
        name = f"{self._year}_{self._q2}"
        mu = zfit.Parameter(f"B_mass_{name}", 5250, 5200, 5300)
        sigma = zfit.Parameter(f"sigma_{name}", 10, 0, 50)
        signal = zfit.pdf.Gauss(obs=self._obs, mu=mu, sigma=sigma, name=f"signal_{name}")
        return signal

    def _get_model(self):
        comb_mm = self._get_comb()
        signal = self._get_signal()

        name = f"{self._year}_{self._q2}"
        f = zfit.Parameter(f"f_sig_{name}", 0.5, 0.001, 1)
        model = zfit.pdf.SumPDF([signal, comb_mm], fracs=f, name=f"model_{name}")
        return model

    def fit(self):
        data_array = self._get_data()
        data = zfit.Data.from_numpy(obs=self._obs, array=ak.to_numpy(data_array[self._mass_variable]))
        model = self._get_model()

        fitter = fit_invert_BDT_mm(obs=self._obs, data=data)
        fitter.add_pdf(model)
        fitter.run(
            f"{self._q2}_{self._year}_{self._mass_variable}_{'withBDTprc' if self._with_bdt_prc else 'NoBDTprc'}"
        )


def main(q2, year, mass_variable, with_bdt_prc):
    logger.info(f"q2: {q2}, year: {year}, mass_variable: {mass_variable}, with_bdt_prc: {with_bdt_prc}")
    obj = comb_shape_mm(q2, year, mass_variable, with_bdt_prc=with_bdt_prc)
    obj.fit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--q2", type=str, help="Specify q2 bin")
    parser.add_argument("--year", type=str, help="Specify year")
    parser.add_argument("--mass-variable", type=str, help="Specify mass variable")
    parser.add_argument("--with-bdt-prc", action="store_true", help="Specify whether to use BDT_prc")
    args = parser.parse_args()
    main(args.q2, args.year, args.mass_variable, args.with_bdt_prc)
