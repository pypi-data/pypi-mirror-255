from hqm.model import get_part_reco
from hqm.model import get_Bu2Ksee_shape
from hqm.model import get_Bd2Ksee_shape
from hqm.model import get_Bs2phiee_shape
from hqm.model import get_Bu2K1ee_shape
from hqm.model import get_Bu2K2ee_shape
from hqm.model import get_signal_shape

from hqm.tools.utility import get_project_root
from logzero           import logger

import zutils.utils      as zut
import matplotlib.pyplot as plt
import numpy             as np
import os
import zfit
import hist
import mplhep

all_datasets   = ["all"]
all_ee_trigger = ["ETOS"] 
n_bts_index    = 2

#---------------------------------------------
def get_rare_shape(name, dataset=None, trigger=None, bts=None):
    if   name == 'Bu2Ksee':
        pdf = get_Bu2Ksee_shape(dataset=dataset, trigger=trigger, bts_index=bts)
    elif name == 'Bd2Ksee':
        pdf = get_Bd2Ksee_shape(dataset=dataset, trigger=trigger, bts_index=bts)
    elif name == 'Bs2phiee':
        pdf = get_Bs2phiee_shape(dataset=dataset, trigger=trigger, bts_index=bts)
    elif name == 'Bu2K1ee':
        pdf = get_Bu2K1ee_shape(dataset=dataset, trigger=trigger, bts_index=bts)
    elif name == 'Bu2K2ee':
        pdf = get_Bu2K2ee_shape(dataset=dataset, trigger=trigger, bts_index=bts)
    else:
        log.error(f'Invalid rare PDF: {name}')
        raise

    return pdf
#---------------------------------------------
def plot(sampler, shape, label, mass_window=(4500, 6000)):
    if sampler is not None:
        toy_data = zfit.run(sampler.unstack_x())
        data_hist = hist.Hist.new.Regular(100, mass_window[0], mass_window[1], overflow=False, name="B_M").Double()
        data_hist.fill(toy_data)
        mplhep.histplot(data_hist, yerr=True, color="black", histtype="errorbar", label="toy data")
        ndata = len(toy_data)
    else:
        ndata = 1

    x = np.linspace(mass_window[0], mass_window[1], 200)
    y = shape.pdf(x) * ndata * (mass_window[1] - mass_window[0]) / 100
    plt.plot(x, y, label=label)
#---------------------------------------------
def test_part_reco_nom():
    for dataset in all_datasets:
        for trigger in all_ee_trigger:
            logger.info(f"part_reco: dataset: {dataset}, trigger: {trigger}")
            pdf, constraints = get_part_reco(
                dataset              = dataset,
                trigger              = trigger,
                parameter_name_prefix= f"test_{dataset}",
                bts_index            =     0,
                systematic           = 'nom',
            )

            sampler   = pdf.create_sampler(n=5000, fixed_params=False)
            plot(sampler, pdf, f"part_reco_{dataset}_{trigger}")

            root_path = get_project_root()
            plot_path = f'{root_path}/output/tests/latest/test_part_reco_nom/part_reco_{dataset}_{trigger}.png'
            logger.info(f"saving plot to {plot_path}")
            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
            plt.savefig(plot_path)
            plt.close()

            list_path = plot_path.replace('.png', '.txt')
            zut.print_pdf(pdf, d_const=constraints, txt_path=list_path)

def test_part_reco_sys():
    for dataset in all_datasets:
        for trigger in all_ee_trigger:
            root_path = get_project_root()
            plot_path = f'{root_path}/output/tests/latest/test_part_reco_syst/part_reco_{dataset}_{trigger}.png'

            for setting in ["nom", "sys1", 0, 1]:
                bts_index = setting if isinstance(setting, int) else 0
                sys       = setting if isinstance(setting, str) else 'nom' 

                logger.info(f"part_reco: dataset: {dataset}, trigger: {trigger}, setting: {setting}")
                pdf, constraints = get_part_reco(
                    dataset                  = dataset,
                    trigger                  = trigger,
                    parameter_name_prefix    = f'test_{dataset}_{setting}_{sys}',
                    bts_index                = bts_index,
                    systematic               = sys)

                sampler = None 
                plot(sampler, pdf, f"cpr_{dataset}_{trigger}_{setting}")

                list_path = plot_path.replace('.png', f'_{setting}.txt')
                zut.print_pdf(pdf, d_const=constraints, txt_path=list_path)

            logger.info(f"saving plot to {plot_path}")
            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
            plt.legend()
            plt.savefig(plot_path)
            plt.close()
#---------------------------------------------
def test_rare_nom():
    for dataset in all_datasets:
        for trigger in all_ee_trigger:
            for rare in ['Bu2Ksee', 'Bd2Ksee', 'Bs2phiee', 'Bu2K1ee', 'Bu2K2ee']:
                pdf           = get_rare_shape(rare, dataset=dataset, trigger=trigger, bts=0)
                sampler       = pdf.create_sampler(n=5000)
                root_path     = get_project_root()
                plot_path     = f"{root_path}/output/tests/latest/test_rare_nom/{rare}_{dataset}_{trigger}_nom.png"
                plot(sampler, pdf, f"{rare}_{dataset}_{trigger}")

                logger.info(f"saving plot to {plot_path}")
                os.makedirs(os.path.dirname(plot_path), exist_ok=True)
                plt.savefig(plot_path)
                plt.close('all')

def test_rare_sys():
    for dataset in all_datasets:
        for trigger in all_ee_trigger:
            for rare in ['Bu2Ksee', 'Bd2Ksee', 'Bs2phiee', 'Bu2K1ee', 'Bu2K2ee']:
                for bts in range(n_bts_index):
                    pdf           = get_rare_shape(rare, dataset=dataset, trigger=trigger, bts=bts)
                    sampler       = None 
                    plot(sampler, pdf, f"{rare}_{dataset}_{trigger}_{bts}")

                root_path     = get_project_root()
                plot_path     = f"{root_path}/output/tests/latest/test_rare_sys/{rare}_{dataset}_{trigger}_sys.png"
                logger.info(f"saving plot to {plot_path}")
                os.makedirs(os.path.dirname(plot_path), exist_ok=True)
                plt.legend()
                plt.savefig(plot_path)
                plt.close('all')
#---------------------------------------------
def test_signal_shape_mm_nom():
    for dataset in all_datasets:
        pdf, constraints = get_signal_shape(
                dataset=dataset, trigger="MTOS", parameter_name_prefix="test", systematic='nom')
        sampler   = pdf.create_sampler(n=5000)
        plot_path = get_project_root() + f"output/tests/latest/test_signal_shape/mm_{dataset}_nom.png"
        plot(sampler, pdf, f"signal_shape_mm_{dataset}_nom", (5180, 5600))
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        logger.info(f"saving plot to {plot_path}")
        plt.savefig(plot_path)
        plt.close('all')

        list_path = plot_path.replace('.png', '.txt')
        zut.print_pdf(pdf, d_const=constraints, txt_path=list_path)

def test_signal_shape_mm_sys():
    for dataset in all_datasets:
        plot_path = get_project_root() + f"output/tests/latest/test_signal_shape/mm_{dataset}_sys.png"
        for sys in ["nom", "sys1"]:
            pdf, constraints = get_signal_shape(dataset=dataset, trigger="MTOS", parameter_name_prefix=f"test_{sys}", systematic=sys)
            list_path        = plot_path.replace('_sys.png', f'_{sys}.txt')
            zut.print_pdf(pdf, d_const=constraints, txt_path=list_path)

            plot(None, pdf, f"signal_shape_mm_{dataset}_{sys}", (5180, 5600))

        logger.info(f"saving plot to {plot_path}")
        plt.legend()
        plt.savefig(plot_path)
        plt.close('all')
#---------------------------------------------
def test_signal_shape_ee_nom():
    for dataset in all_datasets:
        for trigger in all_ee_trigger:
            pdf, constraints = get_signal_shape(dataset=dataset, trigger=trigger, parameter_name_prefix="test", systematic='nom')
            sampler          = pdf.create_sampler(n=5000)
            root_path        = get_project_root()
            plot_path        = f"{root_path}/output/tests/latest/test_signal_shape/ee_{dataset}_{trigger}_nom.png"
            plot(sampler, pdf, f"signal_shape_ee_{dataset}_{trigger}", (4500, 6000))

            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
            logger.info(f"saving plot to {plot_path}")
            plt.savefig(plot_path)
            plt.close('all')

            list_path = plot_path.replace('.png', '.txt')
            zut.print_pdf(pdf, d_const=constraints, txt_path=list_path)

def test_signal_shape_ee_sys():
    for dataset in all_datasets:
        for trigger in all_ee_trigger:
            root_path = get_project_root()
            plot_path = f"{root_path}/output/tests/latest/test_signal_shape/ee_{dataset}_{trigger}_sys.png"
            for sys in ["nom", "sys1"]:
                pdf, constraints = get_signal_shape(dataset=dataset, trigger=trigger, parameter_name_prefix=f"test_{sys}", systematic=sys)
                plot(None, pdf, f"signal_shape_ee_{dataset}_{trigger}_{sys}", (4500, 6000))
                list_path        = plot_path.replace('_sys.png', f'_{sys}.txt')
                zut.print_pdf(pdf, d_const=constraints, txt_path=list_path)

            logger.info(f"saving plot to {plot_path}")
            plt.legend()
            plt.savefig(plot_path)
            plt.close('all')
#---------------------------------------------
def main():
    test_signal_shape_ee_sys()
    test_signal_shape_ee_nom()
    test_signal_shape_mm_sys()
    test_signal_shape_mm_nom()
    test_part_reco_nom()
    test_part_reco_sys()
    test_rare_nom()
    test_rare_sys()
#---------------------------------------------
if __name__ == "__main__":
    main()

