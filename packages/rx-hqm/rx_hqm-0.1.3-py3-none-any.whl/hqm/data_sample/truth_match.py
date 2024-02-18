from hqm.tools.Cut import Cut


class truth_match:
    Jpsi_id = 443
    psi2S_id = 100443
    Bd_id = 511
    Bu_id = 521
    Bs_id = 531
    e_id = 11
    mu_id = 13
    Kp_id = 321
    Ks0_id = 313
    Ksp_id = 323
    K1p_id = 10323
    phi_id = 333
    pip_id = 211

    ee = Cut(lambda x: (abs(x.L1_TRUEID) == truth_match.e_id) & (abs(x.L2_TRUEID) == truth_match.e_id))
    mm = Cut(lambda x: (abs(x.L1_TRUEID) == truth_match.mu_id) & (abs(x.L2_TRUEID) == truth_match.mu_id))

    Jpsi = Cut(lambda x: abs(x.Jpsi_TRUEID) == truth_match.Jpsi_id)
    psi2S = Cut(lambda x: abs(x.Jpsi_TRUEID) == truth_match.psi2S_id)
    Bu = Cut(lambda x: abs(x.B_TRUEID) == truth_match.Bu_id)
    Bd = Cut(lambda x: abs(x.B_TRUEID) == truth_match.Bd_id)
    Bs = Cut(lambda x: abs(x.B_TRUEID) == truth_match.Bs_id)
    Kp = Cut(lambda x: abs(x.H_TRUEID) == truth_match.Kp_id)
    Ks0 = Cut(lambda x: abs(x.H_MC_MOTHER_ID) == truth_match.Ks0_id)
    Ksp = Cut(lambda x: abs(x.H_MC_MOTHER_ID) == truth_match.Ksp_id)

    Jpsi2ll = Jpsi & Cut(
        lambda x: (abs(x.L1_MC_MOTHER_ID) == truth_match.Jpsi_id) & (abs(x.L2_MC_MOTHER_ID) == truth_match.Jpsi_id)
    )
    Jpsi2ee = Jpsi2ll & ee
    Jpsi2mm = Jpsi2ll & mm

    psi2S2ll = psi2S & Cut(
        lambda x: (abs(x.L1_MC_MOTHER_ID) == truth_match.psi2S_id) & (abs(x.L2_MC_MOTHER_ID) == truth_match.psi2S_id)
    )
    psi2S2ee = psi2S2ll & ee
    psi2S2mm = psi2S2ll & mm

    Jpsi_K_mother = Cut(
        lambda x: (abs(x.Jpsi_MC_MOTHER_ID) == truth_match.Bu_id) & (abs(x.H_MC_MOTHER_ID) == truth_match.Bu_id)
    )

    ctrl_ee = Bu & Jpsi2ee & Kp & Jpsi_K_mother
    ctrl_mm = Bu & Jpsi2mm & Kp & Jpsi_K_mother
    psi2_ee = Bu & psi2S2ee & Kp & Jpsi_K_mother
    psi2_mm = Bu & psi2S2mm & Kp & Jpsi_K_mother

    # inclusive
    inclusive_ll_mother = Jpsi2ll | psi2S2ll
    inclusive_ee_total = inclusive_ll_mother & ee
    inclusive_mm_total = inclusive_ll_mother & mm
    inclusive_failed = Cut(
        lambda x: (abs(x.B_TRUEID) == 0)
        | (abs(x.Jpsi_TRUEID) == 0)
        | (abs(x.Jpsi_MC_MOTHER_ID) == 0)
        | (abs(x.L1_TRUEID) == 0)
        | (abs(x.L2_TRUEID) == 0)
        | (abs(x.L1_MC_MOTHER_ID) == 0)
        | (abs(x.L2_MC_MOTHER_ID) == 0)
        | (abs(x.H_TRUEID) == 0)
        | (abs(x.H_MC_MOTHER_ID) == 0)
    )
    inclusive_Bu_psi2S_mother = (Cut(lambda x: abs(x.Jpsi_MC_MOTHER_ID) == truth_match.Bu_id) & psi2S) | ~psi2S
    inclusive_Bd_psi2S_mother = (Cut(lambda x: abs(x.Jpsi_MC_MOTHER_ID) == truth_match.Bd_id) & psi2S) | ~psi2S
    inclusive_Bs_psi2S_mother = (Cut(lambda x: abs(x.Jpsi_MC_MOTHER_ID) == truth_match.Bs_id) & psi2S) | ~psi2S

    bp_x_ee = ~inclusive_failed & inclusive_ee_total & inclusive_Bu_psi2S_mother & Bu & ~ctrl_ee & ~psi2_ee
    bd_x_ee = ~inclusive_failed & inclusive_ee_total & inclusive_Bd_psi2S_mother & Bd
    bs_x_ee = ~inclusive_failed & inclusive_ee_total & inclusive_Bs_psi2S_mother & Bs

    bp_x_mm = ~inclusive_failed & inclusive_mm_total & inclusive_Bu_psi2S_mother & Bu & ~ctrl_mm & ~psi2_mm
    bd_x_mm = ~inclusive_failed & inclusive_mm_total & inclusive_Bd_psi2S_mother & Bd
    bs_x_mm = ~inclusive_failed & inclusive_mm_total & inclusive_Bs_psi2S_mother & Bs

    @classmethod
    def _get_ee_truth(cls, kind):
        if kind in ["data", "cmb"]:
            truth_cut = Cut(lambda x: True)
        elif kind == "sign":
            truth_cut = (
                cls.Bu
                & cls.ee
                & cls.Kp
                & Cut(
                    lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.L2_MC_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.H_MC_MOTHER_ID) == cls.Bu_id)
                )
            )
        elif kind == "ctrl":
            truth_cut = cls.ctrl_ee
        elif kind == "psi2":
            truth_cut = cls.psi2_ee
        elif kind == "bpks":
            truth_cut = (
                cls.Bu
                & cls.Kp
                & cls.ee
                & cls.Ksp
                & Cut(
                    lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.L2_MC_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.H_MC_GD_MOTHER_ID) == cls.Bu_id)
                )
            )
        elif kind == "bdks":
            truth_cut = (
                cls.Bd
                & cls.Kp
                & cls.Ks0
                & cls.ee
                & Cut(
                    lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bd_id)
                    & (abs(x.L2_MC_MOTHER_ID) == cls.Bd_id)
                    & (abs(x.H_MC_GD_MOTHER_ID) == cls.Bd_id)
                )
            )
        elif kind == "bdkpi":
            truth_cut = (
                cls.Bd
                & cls.Kp
                & cls.ee
                & Cut(
                    lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bd_id)
                    & (abs(x.L2_MC_MOTHER_ID) == cls.Bd_id)
                    & (abs(x.H_MC_MOTHER_ID) == cls.Bd_id)
                )
            )
        elif kind == "bp_x":
            truth_cut = cls.bp_x_ee
        elif kind == "bd_x":
            truth_cut = cls.bd_x_ee
        elif kind == "bs_x":
            truth_cut = cls.bs_x_ee
        elif kind == "12153430":
            # B+ -> psi2S K*+
            truth_cut = (
                cls.Bu
                & cls.psi2S2ee
                & cls.Kp
                & cls.Ksp
                & Cut(lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bu_id) & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bu_id))
            )
        elif kind in ["11154011", "psi2Kstr"]:
            # B0 -> psi2S K*0
            truth_cut = (
                cls.Bd
                & cls.psi2S2ee
                & cls.Kp
                & cls.Ks0
                & Cut(lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bd_id) & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bd_id))
            )
        elif kind == "12155010":
            # B+ -> psi2S K+ pi+ pi-
            truth_cut = (
                cls.Bu
                & cls.psi2S2ee
                & cls.Kp
                & Cut(
                    lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.H_MC_MOTHER_ID) == cls.K1p_id)
                    & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bu_id)
                )
            )
        elif kind in ["13124006", "bsphi"]:
            # Bs -> phi(-> KK) ee
            truth_cut = (
                cls.Bs
                & cls.ee
                & Cut(lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bs_id) & (abs(x.L2_MC_MOTHER_ID) == cls.Bs_id))
                & cls.Kp
                & Cut(lambda x: (abs(x.H_MC_MOTHER_ID) == cls.phi_id))
            )
        elif kind in ["12425000", "bpk1"]:
            # B+ -> K1_1270(-> K+ pi+ pi-) ee
            truth_cut = (
                cls.Bu
                & cls.ee
                & Cut(lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bu_id) & (abs(x.L2_MC_MOTHER_ID) == cls.Bu_id))
                & (cls.Kp | Cut(lambda x: (abs(x.H_TRUEID) == cls.pip_id)))
                & (
                    Cut(lambda x: (abs(x.H_MC_MOTHER_ID) == cls.K1p_id))  # K1
                    | Cut(lambda x: abs(x.H_MC_MOTHER_ID) == 113)  # rho0
                    | Cut(lambda x: abs(x.H_MC_MOTHER_ID) == 223)  # omega
                    | Cut(lambda x: abs(x.H_MC_MOTHER_ID) == 313)  # Ks0
                )
            )
        elif kind in ["12425011", "bpk2"]:
            # B+ -> K2st_1430(-> K+ pi+ pi-) ee
            truth_cut = (
                cls.Bu
                & cls.ee
                & Cut(lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bu_id) & (abs(x.L2_MC_MOTHER_ID) == cls.Bu_id))
                & (cls.Kp | Cut(lambda x: (abs(x.H_TRUEID) == cls.pip_id)))
                & (
                    Cut(lambda x: (abs(x.H_MC_MOTHER_ID) == 325))  # K2
                    | Cut(lambda x: abs(x.H_MC_MOTHER_ID) == 113)  # rho0
                    | Cut(lambda x: abs(x.H_MC_MOTHER_ID) == 223)  # omega
                    | Cut(lambda x: abs(x.H_MC_MOTHER_ID) == 313)  # Ks0
                )
            )
        else:
            raise ValueError(f"Unknown kind: {kind} for ee")
        return truth_cut

    @classmethod
    def _get_mm_truth(cls, kind):
        if kind in ["data", "cmb"]:
            truth_cut = Cut(lambda x: True)
        elif kind == "sign":
            truth_cut = (
                cls.Bu
                & cls.mm
                & cls.Kp
                & Cut(
                    lambda x: (abs(x.L1_MC_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.L2_MC_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.H_MC_MOTHER_ID) == cls.Bu_id)
                )
            )
        elif kind == "ctrl":
            truth_cut = cls.ctrl_mm
        elif kind == "psi2":
            truth_cut = cls.psi2_mm
        elif kind == "bp_x":
            truth_cut = cls.bp_x_mm
        elif kind == "bd_x":
            truth_cut = cls.bd_x_mm
        elif kind == "bs_x":
            truth_cut = cls.bs_x_mm
        elif kind == "11144011":
            # B0 -> psi2S K*0
            truth_cut = (
                cls.Bd
                & cls.psi2S2mm
                & cls.Kp
                & cls.Ks0
                & Cut(lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bd_id) & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bd_id))
            )
        elif kind == "11144001":
            # B0 -> Jpsi K*0
            truth_cut = (
                cls.Bd
                & cls.Jpsi2mm
                & cls.Kp
                & cls.Ks0
                & Cut(lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bd_id) & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bd_id))
            )
        elif kind == "12143401":
            # B+ -> Jpsi K*+
            truth_cut = (
                cls.Bu
                & cls.Jpsi2mm
                & cls.Kp
                & cls.Ksp
                & Cut(lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bu_id) & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bu_id))
            )
        elif kind == "12143440":
            # B+ -> Jpsi K(1270)+ (-> K*+ (-> K+ pi0) pi0)
            truth_cut = (
                cls.Bu
                & cls.Jpsi2mm
                & cls.Kp
                & cls.Ksp
                & Cut(
                    lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.K1p_id)
                    & (abs(x.H_MC_GD_GD_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bu_id)
                )
            )
        elif kind == "12145410":
            # B+ -> Jpsi K(1270)+ (-> K+ w (-> pi+ pi- pi0))
            truth_cut = (
                cls.Bu
                & cls.Jpsi2mm
                & cls.Kp
                & Cut(
                    lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.H_MC_MOTHER_ID) == cls.K1p_id)
                    & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bu_id)
                )
            )

        elif kind == "12145090":
            # B+ -> Jpsi K(1270)+ (-> K+ pi+ pi-)
            truth_cut = (
                cls.Bu
                & cls.Jpsi2mm
                & cls.Kp
                & Cut(
                    lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.H_MC_MOTHER_ID) == cls.K1p_id)
                    & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bu_id)
                )
            )

        elif kind == "12145072":
            # B+ -> psi(2S) K(1270)+ (-> K+ pi+ pi-)
            truth_cut = (
                cls.Bu
                & cls.psi2S2mm
                & cls.Kp
                & Cut(
                    lambda x: (abs(x.H_MC_GD_MOTHER_ID) == cls.Bu_id)
                    & (abs(x.H_MC_MOTHER_ID) == cls.K1p_id)
                    & (abs(x.Jpsi_MC_MOTHER_ID) == cls.Bu_id)
                )
            )
        else:
            raise ValueError(f"Unknown kind: {kind} for mm")

        return truth_cut

    @classmethod
    def get_truth(cls, kind, is_e):
        if is_e:
            return cls._get_ee_truth(kind)
        else:
            return cls._get_mm_truth(kind)
