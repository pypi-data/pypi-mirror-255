import argparse
import importlib
from rk.mva import mva_man
from hqm.tools.utility import load_json
import ROOT
import numpy as np
from logzero import logger
import os
from hqm.data_sample.truth_match import truth_match


class apply_preselection:
    def __init__(self, kind, year, version, trigger, portion, q2, tree_name=None, skip_cut=None):
        self._kind = kind
        self._year = year
        self._version = version
        self._trigger = trigger
        self._ipart, self._npart = portion
        self._q2 = q2
        self._skip_cut = skip_cut if skip_cut is not None else []

        if tree_name is not None:
            self._tree_name = tree_name
        else:
            if self._kind == "cmb_ee":
                self._tree_name = "KSS"
            elif self._kind == "cmb_mm":
                self._tree_name = "KSS_mm"
            else:
                if self._trigger in ["ETOS", "GTIS"]:
                    self._tree_name = "KEE"
                elif "MTOS":
                    self._tree_name = "KMM"
                else:
                    raise ValueError(f"Unknown trigger: {trigger}")

        self._preselection_package = importlib.resources.files("selection_data")

        self._all_cuts = None

        self._data_dir = "/publicfs/lhcb/user/campoverde/Data/RK/"

        MVADIR = "/publicfs/ucas/user/campoverde/Data/RK/MVA/"
        self._bdt_dir_cmb = f"{MVADIR}/electron/bdt_v10.11tf.a0v2ss"
        self._bdt_dir_prc = f"{MVADIR}/electron/bdt_v10.18is.prec"

    def _get_cut(self):
        # get all cuts except the bdt
        cut_json_file = self._preselection_package.joinpath("selection_v5.json")
        all_cuts = load_json(cut_json_file)
        all_cuts = all_cuts["ee"] if self._trigger in ["ETOS", "GTIS"] else all_cuts["mm"]

        self._all_cuts = all_cuts
        if self._trigger in ["ETOS", "GTIS"]:
            cut_kinds = [
                "truth",
                "K_IPCHI2",
                "nspd",
                self._trigger.lower(),
                "hlt1",
                "hlt2",
                "q2",
                "kinematics",
                "cascade",
                "ghost",
                "calo_rich",
                "pid",
                "xyecal",
                "bdt_cmb",
                "bdt_prc",
                "mass",
            ]
        elif self._trigger == "MTOS":
            cut_kinds = [
                "truth",
                "K_IPCHI2",
                "nspd",
                "L0",
                "Hlt1",
                "Hlt2",
                "q2",
                "kinematics",
                "cascade",
                "ghost",
                "rich",
                "acceptance",
                "jpsi_misid",
                "pid",
                "bdt_cmb",
                "bdt_prc",
                "mass",
            ]
        else:
            raise ValueError(f"Unknown trigger: {self._trigger}")

        if "bdt" in self._skip_cut:
            self._skip_cut += ["bdt_cmb", "bdt_prc"]
        logger.info(f"skip cut: {self._skip_cut}")

        total_cut = "(1)"
        K_IPCHI2 = "H_IPCHI2_OWNPV > 4"

        for cut_kind in cut_kinds:
            if cut_kind not in self._skip_cut:
                if cut_kind == "truth":
                    cut = truth_match.get_truth(
                        self._kind.removesuffix("_ee").removesuffix("_mm"), is_e=self._trigger in ["ETOS", "GTIS"]
                    )
                elif cut_kind == "K_IPCHI2":
                    cut = K_IPCHI2
                else:
                    cut = all_cuts[cut_kind]
                    if cut_kind in ["hlt1", "hlt2", "Hlt1", "Hlt2"]:
                        cut = cut[self._year]
                    elif cut_kind in ["q2", "mass"]:
                        cut = cut[self._q2]
                    elif cut_kind in ["bdt", "bdt_cmb", "bdt_prc"]:
                        cut = cut[self._trigger]
                print(f"{cut_kind}: {cut}")
                total_cut = f"(({total_cut}) && ({cut}))"
        return total_cut

    def _get_rdf(self):
        input_file = f"{self._data_dir}{self._kind}/{self._version}/{self._year}.root"
        logger.info(f"reading {input_file}")
        rdf = ROOT.RDataFrame(self._tree_name, input_file)
        total_entries = rdf.Count().GetValue()

        index = np.array_split(np.arange(0, total_entries), self._npart)[self._ipart]
        start = int(index[0])
        end = int(index[-1]) + 1

        rdf = rdf.Range(start, end)

        return rdf

    def _add_cut(self, rdf):
        cut = self._get_cut()
        rdf = rdf.Filter(cut)
        return rdf

    def _add_bdt_branch(self, rdf, kind):
        if kind == "cmb":
            mva_cmb = mva_man(rdf, self._bdt_dir_cmb, self._trigger)
            rdf = mva_cmb.add_scores("BDT_cmb")
        elif kind == "prc":
            branchs = list(rdf.GetColumnNames())
            if "B_L1_CC_SPT" in branchs:
                # some old version sample can't add prc BDT
                rdf = rdf.Redefine("yearLabbel", "2018")
                mva_prc = mva_man(rdf, self._bdt_dir_prc, self._trigger)
                rdf = mva_prc.add_scores("BDT_prc")
            else:
                logger.info("BDT_prc not added")

        return rdf

    def _add_bdt_cut(self, rdf):
        rdf = self._add_bdt_branch(rdf, "cmb")
        rdf = self._add_bdt_branch(rdf, "prc")

        bdt_cut = self._all_cuts["bdt"][self._trigger]
        if "bdt" not in self._skip_cut:
            print(f"bdt: {bdt_cut}")
            rdf = rdf.Filter(bdt_cut)
        return rdf

    def save(self, output_dir):
        cache_dir = "/publicfs/ucas/user/qi/tmp/cache/"
        output_file = f"{cache_dir}tools/apply_selection/{output_dir}/latest/{self._kind.removesuffix('_ee').removesuffix('_mm')}/{self._version}/{self._year}_{self._trigger}/{self._ipart}_{self._npart}.root"
        if os.path.exists(output_file):
            logger.info(f"Target root file exists: {output_file}, skip")
            return

        rdf = self._get_rdf()
        rdf = self._add_cut(rdf)
        rdf = self._add_bdt_cut(rdf)
        logger.info(f"Saving to {output_file}")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        rdf.Snapshot(self._trigger, output_file)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--kind", type=str, required=True)
    parser.add_argument("-y", "--year", type=str, required=True)
    parser.add_argument("-v", "--version", type=str, required=True)
    parser.add_argument("-t", "--trigger", type=str, required=True)
    parser.add_argument("-p", "--portion", type=int, nargs=2, required=True)
    parser.add_argument("-q", "--q2", type=str, required=True)
    parser.add_argument("-s", "--skip-cut", type=str, nargs="*", default=None)
    parser.add_argument("-o", "--output-dir", type=str, required=True)
    parser.add_argument("-n", "--tree-name", type=str, default=None)
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    ap = apply_preselection(
        args.kind,
        args.year,
        args.version,
        args.trigger,
        args.portion,
        args.q2,
        tree_name=args.tree_name,
        skip_cut=args.skip_cut,
    )
    ap.save(args.output_dir)


if __name__ == "__main__":
    main()
