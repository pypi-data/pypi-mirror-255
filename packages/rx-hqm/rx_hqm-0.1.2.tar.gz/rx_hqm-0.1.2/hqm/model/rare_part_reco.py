from .KDE_shape import get_KDE_shape as get_rare_KDE_shape
import zfit


def _get_rare_part_reco_shape(dataset="2018", trigger="ETOS", pdf_name="", kind="bpks", bts_index=0):
    mass_window = (4500, 6000)
    obs = zfit.Space("B_M", limits=mass_window)
    rare_part_reco_shape = get_rare_KDE_shape(
        obs, kind, "high", bandwidth=None, dataset=dataset, trigger=trigger, pdf_name=pdf_name, bts_index=bts_index
    )
    return rare_part_reco_shape


def get_Bd2Ksee_shape(dataset="2018", trigger="ETOS", bts_index=0):
    return _get_rare_part_reco_shape(
        dataset=dataset, trigger=trigger, pdf_name="Bd2Ksee", kind="bdks", bts_index=bts_index
    )


def get_Bu2Ksee_shape(dataset="2018", trigger="ETOS", bts_index=0):
    return _get_rare_part_reco_shape(
        dataset=dataset, trigger=trigger, pdf_name="Bu2Ksee", kind="bpks", bts_index=bts_index
    )


def get_Bs2phiee_shape(dataset="2018", trigger="ETOS", bts_index=0):
    return _get_rare_part_reco_shape(
        dataset=dataset, trigger=trigger, pdf_name="Bs2phiee", kind="bsphi", bts_index=bts_index
    )


def get_Bu2K1ee_shape(dataset="2018", trigger="ETOS", bts_index=0):
    return _get_rare_part_reco_shape(
        dataset=dataset, trigger=trigger, pdf_name="Bu2K1ee", kind="bpk1", bts_index=bts_index
    )


def get_Bu2K2ee_shape(dataset="2018", trigger="ETOS", bts_index=0):
    return _get_rare_part_reco_shape(
        dataset=dataset, trigger=trigger, pdf_name="Bu2K2ee", kind="bpk2", bts_index=bts_index
    )
