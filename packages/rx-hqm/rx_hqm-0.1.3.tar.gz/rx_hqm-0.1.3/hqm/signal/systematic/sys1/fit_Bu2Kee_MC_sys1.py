import zfit

from hqm.signal.fit_Bu2Kee_MC import fit_Bu2Kee_MC
import argparse


def get_CB_ee_sys1(obs, suffix, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    mu = zfit.Parameter(f"{parameter_name_prefix}mu_CB_ee_{suffix}", 5200, 5000, 5600)
    sigma = zfit.Parameter(f"{parameter_name_prefix}sigma_CB_ee_{suffix}", 10, 0.1, 500)
    alpha = zfit.Parameter(f"{parameter_name_prefix}alpha_CB_ee_{suffix}", 1, 0, 10)
    n = zfit.Parameter(f"{parameter_name_prefix}n_CB_ee_{suffix}", 1, 0, 10)

    cb = zfit.pdf.CrystalBall(obs=obs, mu=mu, sigma=sigma, alpha=alpha, n=n, name=f"CB_ee_{suffix}")
    return cb


def get_3Gauss_ee_sys1(obs, suffix, parameter_name_prefix=""):
    parameter_name_prefix = parameter_name_prefix + "_" if parameter_name_prefix != "" else ""

    mu1 = zfit.Parameter(f"{parameter_name_prefix}mu1_3Gauss_ee_{suffix}", 5200, 5000, 5600)
    mu2 = zfit.Parameter(f"{parameter_name_prefix}mu2_3Gauss_ee_{suffix}", 5200, 5000, 5600)
    mu3 = zfit.Parameter(f"{parameter_name_prefix}mu3_3Gauss_ee_{suffix}", 5200, 5000, 5600)

    sigma1 = zfit.Parameter(f"{parameter_name_prefix}sigma1_3Gauss_ee_{suffix}", 10, 0.1, 100)
    sigma2 = zfit.Parameter(f"{parameter_name_prefix}sigma2_3Gauss_ee_{suffix}", 110, 100, 150)
    sigma3 = zfit.Parameter(f"{parameter_name_prefix}sigma3_3Gauss_ee_{suffix}", 160, 150, 500)

    frac1 = zfit.Parameter(f"{parameter_name_prefix}frac1_3Gauss_ee_{suffix}", 0.5, 0, 1)
    _frac2 = zfit.Parameter(f"_{parameter_name_prefix}frac2_3Gauss_ee_{suffix}", 0.5, 0, 1)
    frac2 = zfit.param.ComposedParameter(
        f"{parameter_name_prefix}frac2_3Gauss_ee_{suffix}",
        lambda p: (1 - p["frac1"]) * p["_frac2"],
        {"frac1": frac1, "_frac2": _frac2},
    )

    gauss1 = zfit.pdf.Gauss(obs=obs, mu=mu1, sigma=sigma1, name=f"gauss1_3Gauss_ee_{suffix}")
    gauss2 = zfit.pdf.Gauss(obs=obs, mu=mu2, sigma=sigma2, name=f"gauss2_3Gauss_ee_{suffix}")
    gauss3 = zfit.pdf.Gauss(obs=obs, mu=mu3, sigma=sigma3, name=f"gauss3_3Gauss_ee_{suffix}")

    total = zfit.pdf.SumPDF([gauss1, gauss2, gauss3], fracs=[frac1, frac2], name=f"3Gauss_ee_{suffix}")
    return total


class fit_Bu2Kee_MC_sys1(fit_Bu2Kee_MC):
    def __init__(self, category, version, year, q2, mass, trigger):
        super().__init__(category, version, year, q2, mass, trigger)

    def build_model(self):
        suffix = f"{self._category}_{self._year}_{self._trigger}"

        if self._category == 0:
            self.add_pdf(get_CB_ee_sys1(self.obs, suffix, parameter_name_prefix=""))
        else:
            self.add_pdf(get_3Gauss_ee_sys1(self.obs, suffix, parameter_name_prefix=""))


def main(args):
    fitter = fit_Bu2Kee_MC_sys1(
        args.category, version="v10.21p2", year=args.year, q2="high", mass="normal", trigger=args.trigger
    )
    fitter.run(systematic="sys1")


def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--category", help="bremsstrahlung category", type=int)
    parser.add_argument("-y", "--year", type=str, default="2018", help="year")
    parser.add_argument("-t", "--trigger", type=str, default="ETOS", help="trigger")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main(get_arg())
