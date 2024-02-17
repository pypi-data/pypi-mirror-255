from hqm.tools.Cut import Cut
import numpy as np

# cut on awkward array
selection = {
    "ee": {
        "bdt_cmb": {
            "ETOS": Cut(lambda x: x.BDT_cmb > 0.977),
            "GTIS": Cut(lambda x: x.BDT_cmb > 0.977),
            "MTOS": Cut(lambda x: x.BDT_cmb > 0.977),
        },
        "bdt_prc": {
            "ETOS": Cut(lambda x: x.BDT_prc > 0.480751),
            "GTIS": Cut(lambda x: x.BDT_prc > 0.480751),
            "MTOS": Cut(lambda x: x.BDT_prc > 0.480751),
        },
        "pid": Cut(lambda x: (x.H_ProbNNk > 0.200) & (x.H_PIDe < 0.000) & (x.L1_PIDe > 3.000) & (x.L2_PIDe > 3.000)),
    },
    "mm": {
        "bdt_cmb": {
            "ETOS": Cut(lambda x: x.BDT_cmb > 0.831497),
            "GTIS": Cut(lambda x: x.BDT_cmb > 0.858292),
            "MTOS": Cut(lambda x: x.BDT_cmb > 0.831497),
        },
        "bdt_prc": {
            "ETOS": Cut(lambda x: x.BDT_prc > 0.480751),
            "GTIS": Cut(lambda x: x.BDT_prc > 0.480751),
            "MTOS": Cut(lambda x: x.BDT_prc > 0.480751),
        },
        "jpsi_misid": Cut(lambda x: (np.abs(x.kl_M_k2l - 3097.0) > 60) & (np.abs(x.kl_M_k2l - 3686.0) > 60)),
    },
}

# cut on awkward array
selection_v1 = {
    "ee": {
        "bdt_cmb": {
            "ETOS": Cut(lambda x: x.BDT_cmb > 0.831497),
            "GTIS": Cut(lambda x: x.BDT_cmb > 0.858292),
            "MTOS": Cut(lambda x: x.BDT_cmb > 0.831497),
        },
        "bdt_prc": {
            "ETOS": Cut(lambda x: x.BDT_prc > 0.480751),
            "GTIS": Cut(lambda x: x.BDT_prc > 0.480751),
            "MTOS": Cut(lambda x: x.BDT_prc > 0.480751),
        },
        "pid": Cut(lambda x: (x.H_ProbNNk > 0.200) & (x.H_PIDe < 0.000) & (x.L1_PIDe > 3.000) & (x.L2_PIDe > 3.000)),
    },
    "mm": {
        "bdt_cmb": {
            "ETOS": Cut(lambda x: x.BDT_cmb > 0.831497),
            "GTIS": Cut(lambda x: x.BDT_cmb > 0.858292),
            "MTOS": Cut(lambda x: x.BDT_cmb > 0.831497),
        },
        "bdt_prc": {
            "ETOS": Cut(lambda x: x.BDT_prc > 0.480751),
            "GTIS": Cut(lambda x: x.BDT_prc > 0.480751),
            "MTOS": Cut(lambda x: x.BDT_prc > 0.480751),
        },
        "jpsi_misid": Cut(lambda x: (np.abs(x.kl_M_k2l - 3097.0) > 60) & (np.abs(x.kl_M_k2l - 3686.0) > 60)),
    },
}
