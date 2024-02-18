import zfit
from hqm.tools.fit import fit
from hqm.tools.utility import get_project_root
from hqm.tools.utility import read_root
from hqm.tools.Cut import Cut
from hqm.tools.selection import selection
from hqm.tools.utility import get_lumi
import argparse
import awkward as ak
import numpy as np
from logzero import logger


class fit_Bu2Kee_MC(fit):
    def __init__(self, category, version, year, q2, mass, trigger):
        self._category = category
        self._version = version
        self._year = year
        self._q2 = q2
        self._mass = mass
        self._trigger = trigger
        self._project_root = get_project_root()

        obs = zfit.Space("B_mass", limits=(4300, 6000))

        if year == "r1":
            years = ["2011", "2012"]
        elif year == "r2p1":
            years = ["2015", "2016"]
        elif year == "all":
            years = ["2011", "2012", "2015", "2016", "2017", "2018"]
        else:
            years = [year]

        bdt_cmb = selection["ee"]["bdt_cmb"][self._trigger]
        bdt_prc = selection["ee"]["bdt_prc"][self._trigger]
        bdt = bdt_cmb & bdt_prc
        if self._category < 2:
            cut = Cut(lambda x: x.L1_BremMultiplicity + x.L2_BremMultiplicity == self._category)
        elif self._category == 2:
            cut = Cut(lambda x: x.L1_BremMultiplicity + x.L2_BremMultiplicity >= 2)
        else:
            raise
        total_cut = bdt & cut

        all_arrays = []
        all_lumi = []
        for _year in years:
            root_path = f"{self._project_root}/root_sample/v6/sign/{self._version}/{_year}_{self._trigger}/{self._q2}_{self._mass}.root"
            data_array = read_root(root_path, self._trigger)
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

        logger.debug(f"{np.where(~np.isfinite(ak.to_numpy(self._total_data['B_M'])))}")
        super().__init__(obs, data)

    def build_model(self):
        # DSCB
        suffix = f"{self._category}_{self._year}_{self._trigger}"
        mu = zfit.Parameter(f"mu_DSCB_{suffix}", 5200, 5000, 5600)
        sigma = zfit.Parameter(f"sigma_DSCB_{suffix}", 10, 0.1, 500)
        alphal = zfit.Parameter(f"alphal_DSCB_{suffix}", 1, 0, 10)
        nl = zfit.Parameter(f"nl_DSCB_{suffix}", 1, 0, 150)
        alphar = zfit.Parameter(f"alphar_DSCB_{suffix}", 1, 0, 10)
        nr = zfit.Parameter(f"nr_DSCB_{suffix}", 1, 0, 120)

        dscb = zfit.pdf.DoubleCB(
            mu=mu,
            sigma=sigma,
            alphal=alphal,
            nl=nl,
            alphar=alphar,
            nr=nr,
            obs=self.obs,
            name=f"DSCB_ee_{suffix}",
        )
        self.add_pdf(dscb)

    def run(self, systematic=None):
        self.build_model()
        self.fit_data()
        project_root = get_project_root()
        dir_name = systematic + "/latest/" if systematic is not None else ""
        self.dump_result(
            f"{project_root}data/signal_shape_ee/latest/{dir_name}fit_Bu2Kee_MC_{self._category}_{self._year}_{self._trigger}.pickle"
        )
        self.plot(
            f"{project_root}output/signal_shape_ee/latest/{dir_name}fit_Bu2Kee_MC_{self._category}_{self._year}_{self._trigger}.pdf"
        )
        self.plot(
            f"{project_root}output/signal_shape_ee/latest/{dir_name}fit_Bu2Kee_MC_{self._category}_{self._year}_{self._trigger}_log.pdf",
            ylog=True,
        )


def main(args):
    fitter = fit_Bu2Kee_MC(
        args.category, version="v10.21p2", year=args.year, q2="high", mass="normal", trigger=args.trigger
    )
    fitter.run()


def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--category", help="bremsstrahlung category", type=int)
    parser.add_argument("-y", "--year", type=str, default="2018", help="year")
    parser.add_argument("-t", "--trigger", type=str, default="ETOS", help="trigger")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main(get_arg())
