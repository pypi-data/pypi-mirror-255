# get the signal shape of rare decay Bu->Kmm by fitting the MC sample

import zfit
from hqm.tools.fit import fit
from hqm.tools.Cut import Cut
from hqm.tools.utility import get_project_root
from hqm.tools.utility import read_root
from hqm.tools.selection import selection
from hqm.tools.utility import get_lumi
import awkward as ak
import argparse
import numpy as np


class fit_Bu2Kmm_MC(fit):
    def __init__(self, year="2018"):
        self._year = year

        obs = zfit.Space("B_mass", limits=(5180, 5600))

        if year == "r1":
            years = ["2011", "2012"]
        elif year == "r2p1":
            years = ["2015", "2016"]
        elif year == "all":
            years = ["2011", "2012", "2015", "2016", "2017", "2018"]
        else:
            years = [year]

        bdt_cmb = selection["mm"]["bdt_cmb"]["MTOS"]
        bdt_prc = selection["mm"]["bdt_prc"]["MTOS"]
        bdt = bdt_cmb & bdt_prc
        jpsi_misid = selection["mm"]["jpsi_misid"]
        total_cut = jpsi_misid & bdt

        all_arrays = []
        all_lumi = []
        for _year in years:
            data_path = f"{get_project_root()}/root_sample/v6/sign/v10.21p2/{_year}_MTOS/high_nomass.root"
            data_array = read_root(data_path, "MTOS")
            data_array = total_cut.apply(data_array)
            all_arrays.append(data_array)

            all_lumi += [get_lumi(_year)] * len(data_array)

        self._total_data = ak.concatenate(all_arrays)

        all_lumi = np.array(all_lumi)
        all_lumi = all_lumi / np.sum(all_lumi) * len(self._total_data)
        if len(years) == 1:
            data = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(self._total_data["B_M"]))
        else:
            zfit.run.set_autograd_mode(False)
            data = zfit.Data.from_numpy(obs=obs, array=ak.to_numpy(self._total_data["B_M"]), weights=all_lumi)

        super().__init__(obs=obs, data=data)

    def _build_model(self):
        # DSCB
        mu = zfit.Parameter(f"mu_DSCB_mm_{self._year}_MTOS", 5250, 5180, 5600)
        sigma = zfit.Parameter(f"sigma_DSCB_mm_{self._year}_MTOS", 30, 0, 100)
        alphal = zfit.Parameter(f"alphal_DSCB_mm_{self._year}_MTOS", 1, 0, 10)
        nl = zfit.Parameter(f"nl_DSCB_mm_{self._year}_MTOS", 1, 0, 100)
        alphar = zfit.Parameter(f"alphar_DSCB_mm_{self._year}_MTOS", 1, 0, 10)
        nr = zfit.Parameter(f"nr_DSCB_mm_{self._year}_MTOS", 1, 0, 100)
        DSCB_mm = zfit.pdf.DoubleCB(
            obs=self.obs,
            mu=mu,
            sigma=sigma,
            alphal=alphal,
            nl=nl,
            alphar=alphar,
            nr=nr,
            name=f"DSCB_mm_{self._year}_MTOS",
        )

        self.add_pdf(DSCB_mm)

    def _save_result(self, systematic=None):
        project_root = get_project_root()

        dir_name = systematic + "/latest/" if systematic is not None else ""

        self.dump_result(f"{project_root}data/signal_shape_mm/latest/{dir_name}fit_Bu2Kmm_MC_{self._year}_MTOS.pickle")

        plot_dir = f"{project_root}output/signal_shape_mm/latest/{dir_name}"
        self.plot(plot_dir + f"fit_Bu2Kmm_MC_{self._year}_MTOS.pdf", leg={"Data": "MC"})
        self.plot(plot_dir + f"fit_Bu2Kmm_MC_log_{self._year}_MTOS.pdf", ylog=True, leg={"Data": "MC"})

    def run(self, systematic=None):
        self._build_model()
        self.fit_data()
        self._save_result(systematic=systematic)


def main(year):
    fitter = fit_Bu2Kmm_MC(year)
    fitter.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", type=str, default="2018", help="year")
    args = parser.parse_args()
    main(args.year)
