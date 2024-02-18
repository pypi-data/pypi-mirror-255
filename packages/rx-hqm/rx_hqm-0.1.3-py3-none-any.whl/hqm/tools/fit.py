import zfit
import pickle
from fitter import zfitter
from zutils.plot import plot as zfp
import matplotlib.pyplot as plt
import os
import pandas as pd
from hqm.tools.utility import get_project_root
import logzero


class fit_plot(zfp):
    def __init__(self, fit_obj, suffix=""):
        super().__init__(fit_obj.data, fit_obj.total_model, fit_obj.result, suffix)


class fit:
    def __init__(self, obs: zfit.Space, data: zfit.Data):
        self.data: zfit.Data = data
        self.component_list = []
        self.fracs = []
        self.obs = obs
        self.total_model: zfit.pdf.SumPDF | None = None
        self.result = None
        self._pre_fit_result = None
        self.covariance_matrix_df = None
        self.correlation_matrix_df = None
        self.fitobj = None

        self._gauss_constraint = {}

        self._log = logzero.logger
        self._project_root = get_project_root()

    def add_pdf(self, pdf, frac=None):
        self.component_list.append(pdf)
        if frac is not None:
            self.fracs.append(frac)

    def add_constraint(self, cons):
        self._gauss_constraint.update(cons)

    def _fit_setup(self):
        if len(self.fracs) == 0:
            self.total_model = (
                zfit.pdf.SumPDF(self.component_list, name="Total fit")
                if len(self.component_list) >= 2
                else self.component_list[0]
            )
        elif (len(self.fracs) == len(self.component_list)) or (len(self.fracs) == len(self.component_list) - 1):
            self.total_model = zfit.pdf.SumPDF(self.component_list, self.fracs, name="Total_fit")
        else:
            raise

    def _fit_data(self):
        if self.total_model.is_extended:
            nll = zfit.loss.ExtendedUnbinnedNLL(model=self.total_model, data=self.data)
        else:
            nll = zfit.loss.UnbinnedNLL(model=self.total_model, data=self.data)

        minimizer = zfit.minimize.Minuit()
        self.result = minimizer.minimize(nll)

        # if self.result.status != 0:
        #     return
        params_list = list(self.result.params.keys())
        params_name_list = [x.name for x in params_list]

        print(self.result)
        try:
            self.result.hesse()
            covariance_matrix_np = self.result.covariance()
            self.covariance_matrix_df = pd.DataFrame(
                covariance_matrix_np, columns=params_name_list, index=params_name_list
            )
            self._log.info("covariance matrix:")
            print(self.covariance_matrix_df)

            correlation_matrix_np = self.result.correlation()
            self.correlation_matrix_df = pd.DataFrame(
                correlation_matrix_np, columns=params_name_list, index=params_name_list
            )
            self._log.info("correlation matrix:")
            print(self.correlation_matrix_df)
        except:
            self._log.warning("Hesse failed")

        self._log.info("fit result:")
        print(self.result)

    def fit_data(self):
        self._fit_setup()
        self._fit_data()

    def _pre_fit(self, limits, pdf):
        """
        pre-fit the pdf in the given range
        """
        logzero.logger.info(f"pre-fit with {pdf.name} in range {limits}")
        values = zfit.z.unstack_x(self.data)
        pre_fit_obs = zfit.Space(self.obs.obs[0], limits=limits)
        pre_fit_data = zfit.Data.from_tensor(obs=pre_fit_obs, tensor=values)
        with pdf.set_norm_range(pre_fit_obs):
            pre_fit_minimizer = zfit.minimize.Minuit()
            pre_fit_nll = zfit.loss.UnbinnedNLL(model=pdf, data=pre_fit_data)
            pre_fit_result = pre_fit_minimizer.minimize(pre_fit_nll)

        logzero.logger.info("pre-fit result:")
        print(pre_fit_result)
        self._pre_fit_result = pre_fit_result

    def plot(self, plot_path, suffix="", ylog=False, leg={}):
        plotter = fit_plot(self, suffix)
        plotter.plot(plot_range=self.data.data_range.limit1d, d_leg=leg)

        pull_ax = plotter.axs[1]
        x = [plotter.lower, plotter.upper]
        pull_ax.plot(x, [0, 0], linestyle="--", color="black", linewidth=1)
        pull_ax.plot(x, [-5, -5], linestyle="--", color="red", linewidth=1)
        pull_ax.plot(x, [5, 5], linestyle="--", color="red", linewidth=1)

        if ylog:
            plotter.axs[0].set_yscale("log")
            plotter.axs[0].set_ylim(bottom=0.1)

        os.makedirs(os.path.dirname(plot_path), exist_ok=True)

        self._log.info(f"Saving plot to {plot_path}")
        plt.savefig(plot_path)
        plt.close()

    def dump_result(self, path, protocal=pickle.DEFAULT_PROTOCOL):
        self.result.freeze()
        self.result.covariance_matrix = self.covariance_matrix_df
        self.result.correlation_matrix = self.correlation_matrix_df

        os.makedirs(os.path.dirname(path), exist_ok=True)

        if self._pre_fit_result is not None:
            self._pre_fit_result.freeze()
            dump_obj = {"result": self.result, "pre_fit_result": self._pre_fit_result}
        else:
            dump_obj = {"result": self.result}

        self._log.info(f"Dumping result to {path}")
        with open(path, "wb") as f:
            pickle.dump(
                dump_obj,
                f,
                protocol=protocal,
            )
