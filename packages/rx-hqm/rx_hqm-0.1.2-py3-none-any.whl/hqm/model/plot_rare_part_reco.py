from hqm.model.rare_part_reco import get_Bu2Ksee_shape
from hqm.model.rare_part_reco import get_Bd2Ksee_shape
from hqm.tools.utility import get_project_root
import os
import matplotlib.pyplot as plt
import zfit
import hist
import mplhep
import numpy as np


def plot_KDE(pdf, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lower, upper = pdf.space.limit1d
    data = zfit.run(pdf._data)
    data_yield = len(data)
    data_hist = hist.Hist.new.Regular(100, lower, upper, overflow=False, name="B_M").Double()
    data_hist.fill(data)

    plt.figure()
    mplhep.histplot(data_hist, yerr=True, color="black", histtype="errorbar", label="MC")
    x = np.linspace(lower, upper, 2000)
    y = pdf.pdf(x) * data_yield * (upper - lower) / 100
    plt.plot(x, y, label="KDE")
    plt.xlim(lower, upper)
    plt.ylim(bottom=0)
    plt.legend()
    plt.savefig(path)
    plt.close()


def main():
    Bu2Ksee_shape = get_Bu2Ksee_shape()
    plot_path = get_project_root() + "output/rare_part_reco/Bu2Ksee_shape_2018_ETOS.pdf"
    plot_KDE(Bu2Ksee_shape, plot_path)

    Bd2Ksee_shape = get_Bd2Ksee_shape()
    plot_path = get_project_root() + "output/rare_part_reco/Bd2Ksee_shape_2018_ETOS.pdf"
    plot_KDE(Bd2Ksee_shape, plot_path)


if __name__ == "__main__":
    main()
