#!/usr/bin/env python3

import uproot
import awkward as ak
from logzero import logger
from hqm.tools.utility import get_project_root
import os
import argparse
from hqm.tools.Cut import Cut
from hqm.data_sample.truth_match import truth_match


class selector:
    def __init__(self, q2, mass, kind, year, version, trigger, target_dir, input_dir):
        self._q2 = q2
        self._mass = mass
        self._kind = kind
        self._year = year
        self._version = version
        self._trigger = trigger
        self._data_dir = f"/afs/ihep.ac.cn/users/q/qi/tmp/cache/tools/apply_selection/root_sample/{input_dir}"
        self._project_root = get_project_root()
        self._output_dir = (
            f"{self._project_root}/root_sample/{target_dir}/{self._kind}/{self._version}/{self._year}_{self._trigger}/"
        )
        self._output_file = f"{self._output_dir}/{self._q2}_{self._mass}.root"
        self._data_array = None

    def _get_q2(self):
        # get q2 cut
        if self._trigger in ["ETOS", "GTIS"]:
            if self._q2 == "high":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 15500000.0) & (x.Jpsi_M**2 < 22000000.0))
            elif self._q2 == "central":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 1100000.0) & (x.Jpsi_M**2 < 6000000.0))
            elif self._q2 == "psi2":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 9920000.0) & (x.Jpsi_M**2 < 16400000.0))
            elif self._q2 == "jpsi":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 6000000.0) & (x.Jpsi_M**2 < 12960000.0))
            elif self._q2 == "noq2":
                q2_cut = Cut(lambda x: True)
            else:
                logger.error(f"Invalid q2 value: {self._q2}")
                raise
        elif self._trigger == "MTOS":
            if self._q2 == "high":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 15500000.0) & (x.Jpsi_M**2 < 22000000.0))
            elif self._q2 == "central":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 1100000.0) & (x.Jpsi_M**2 < 6000000.0))
            elif self._q2 == "jpsi":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 8680000.0) & (x.Jpsi_M**2 < 10090000.0))
            elif self._q2 == "psi2":
                q2_cut = Cut(lambda x: (x.Jpsi_M**2 > 12500000.0) & (x.Jpsi_M**2 < 14200000.0))
            elif self._q2 == "noq2":
                q2_cut = Cut(lambda x: True)
            else:
                logger.error(f"Invalid q2 value: {self._q2}")
                raise
        else:
            logger.error(f"Invalid trigger value: {self._trigger}")
            raise

        return q2_cut

    def _get_mass(self):
        # get mass cut
        if self._mass == "normal":
            mass_cut = Cut(lambda x: (x.B_M > 4500.0) & (x.B_M < 6000.0))
        elif self._mass == "psicons":
            mass_cut = Cut(lambda x: (x.B_M_Psi > 4500.0) & (x.B_M_Psi < 6000.0))
        elif self._mass == "jpsicons":
            mass_cut = Cut(lambda x: (x.B_M_Jpsi > 4500.0) & (x.B_M_Jpsi < 6000.0))
        elif self._mass == "nomass":
            mass_cut = Cut(lambda x: True)
        else:
            logger.error(f"Invalid mass value: {self._mass}")
            raise

        return mass_cut

    def _get_truth(self):
        # get truth match cut

        # truth match for muon is already applied
        if self._trigger in ["MTOS"]:
            truth_cut = truth_match.get_truth(self._kind, is_e=False)
        elif self._trigger in ["ETOS", "GTIS"]:
            truth_cut = truth_match.get_truth(self._kind, is_e=True)
        else:
            raise ValueError(f"Invalid trigger value: {self._trigger}")

        return truth_cut

    def _get_cut(self):
        # get total cut
        q2_cut = self._get_q2()
        mass_cut = self._get_mass()
        truth_cut = self._get_truth()

        total_cut = q2_cut & mass_cut & truth_cut
        return total_cut

    def _get_data(self):
        # get data array

        input_dir = f"{self._data_dir}/{self._kind}/{self._version}/{self._year}_{self._trigger}/"
        # check if the file exists
        if not os.path.exists(input_dir):
            logger.info(f"{input_dir} doesn't exist, skip")
            return

        tot_data_array = uproot.concatenate(f"{input_dir}*.root:{self._trigger}")
        tot_data_array["B_M_Jpsi"] = tot_data_array["B_const_mass_M"][:, 0]
        tot_data_array["B_M_Psi"] = tot_data_array["B_const_mass_psi2S_M"][:, 0]
        return tot_data_array

    def _apply_cut(self):
        # apply cut to data array
        tot_data_array = self._get_data()
        if tot_data_array is None:
            return
        cut = self._get_cut()
        self._data_array = cut.apply(tot_data_array)

    def _save(self):
        # save data array
        if self._data_array is None:
            logger.warning("Can't get data, skip")
            return

        if len(self._data_array) == 0:
            logger.warning("0 event here, skip")
            return

        logger.info(f"Saving to {self._output_file} with {len(self._data_array)} events")
        os.makedirs(self._output_dir, exist_ok=True)
        with uproot.recreate(self._output_file) as f:
            f[self._trigger] = {k: self._data_array[k] for k in self._data_array.fields}

    def save(self):
        # save data array

        # check if target root file exists
        if os.path.isfile(self._output_file):
            logger.info(f"{self._output_file} exists, skip")
            return
        self._apply_cut()
        self._save()


def main(kind, version, year, target_dir, input_dir):
    all_q2 = ["psi2", "jpsi", "noq2", "high"]
    all_mass = [
        # "psicons",
        # "jpsicons",
        "nomass",
        "normal",
    ]
    all_trigger = [
        "ETOS",
        "GTIS",
        "MTOS",
    ]
    for q2 in all_q2:
        for mass in all_mass:
            for trigger in all_trigger:
                logger.info(f"Processing {kind} {q2} {mass} {year} {version} {trigger}")
                s = selector(q2, mass, kind, year, version, trigger, target_dir, input_dir)
                s.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", type=str)
    parser.add_argument("--version", type=str)
    parser.add_argument("--year", type=str)
    parser.add_argument("--target-dir", type=str, default="latest")
    parser.add_argument("--input-dir", type=str, default="latest")
    args = parser.parse_args()
    main(args.kind, args.version, args.year, args.target_dir, args.input_dir)
