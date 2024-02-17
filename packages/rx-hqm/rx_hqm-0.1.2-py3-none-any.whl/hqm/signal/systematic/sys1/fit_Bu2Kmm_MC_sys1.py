# get the signal shape of rare decay Bu->Kmm by fitting the MC sample

import zfit

from hqm.signal.fit_Bu2Kmm_MC import fit_Bu2Kmm_MC
import argparse


def get_2Gauss_mm(obs, suffix, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    mu1 = zfit.Parameter(f"{parameter_name_prefix}mu1_2Gauss_mm_{suffix}", 5250, 5180, 5600)
    mu2 = zfit.Parameter(f"{parameter_name_prefix}mu2_2Gauss_mm_{suffix}", 5250, 5180, 5600)

    sigma1 = zfit.Parameter(f"{parameter_name_prefix}sigma1_2Gauss_mm_{suffix}", 10, 0.1, 30)
    sigma2 = zfit.Parameter(f"{parameter_name_prefix}sigma2_2Gauss_mm_{suffix}", 40, 30, 50)

    frac1 = zfit.Parameter(f"{parameter_name_prefix}frac1_2Gauss_mm_{suffix}", 0.5, 0, 1)

    gauss1 = zfit.pdf.Gauss(obs=obs, mu=mu1, sigma=sigma1, name=f"gauss1_2Gauss_mm_{suffix}")
    gauss2 = zfit.pdf.Gauss(obs=obs, mu=mu2, sigma=sigma2, name=f"gauss2_2Gauss_mm_{suffix}")

    total = zfit.pdf.SumPDF([gauss1, gauss2], fracs=[frac1], name=f"2Gauss_mm_{suffix}")
    return total


class fit_Bu2Kmm_MC_sys1(fit_Bu2Kmm_MC):
    def __init__(self, year="2018"):
        super().__init__(year)

    def _build_model(self):
        suffix = f"{self._year}_MTOS"

        # 3 Gauss
        total = get_2Gauss_mm(self.obs, suffix)
        self.add_pdf(total)


def main(year):
    fitter = fit_Bu2Kmm_MC_sys1(year)
    fitter.run(systematic="sys1")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", type=str, default="2018", help="year")
    args = parser.parse_args()
    main(args.year)
