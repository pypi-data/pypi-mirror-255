#!/usr/bin/env bash

all_kind=("data" "sign" "ctrl" "psi2" "bpks" "bdks" "bdkpi" "bpk1" "bpk2" "bsphi")
all_version=("v10.21p2")
all_year=("2011" "2012" "2015" "2016" "2017" "2018")

SUMBIT_SCRIPT="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/data_sample/add_selection_script.sh"


for kind in ${all_kind[@]}; do
    for year in ${all_year[@]}; do
        for version in ${all_version[@]}; do
            JOBDIR="$HOME/tmp/Jobs/add_selection"
            DATE=$(date +%Y-%m-%d_%H-%M-%S)
            JOBDIR="$JOBDIR/$DATE"

            mkdir -p $JOBDIR
            rm    -f $JOBDIR/*.out
            rm    -f $JOBDIR/*.err

            OUTPUT_FILE="$JOBDIR/add_selection_%{ClusterId}"

            echo "kind: $kind, version: $version, year: $year"
            hep_sub -g lhcb -e "$OUTPUT_FILE.err" -o "$OUTPUT_FILE.out" -argu $kind $version $year -mem 8000 -wt mid $SUMBIT_SCRIPT
        done
    done
done
