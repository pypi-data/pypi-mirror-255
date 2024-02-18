#!/usr/bin/env bash

year=$1
trigger=$2
kind=$3

source $HOME/.bashrc
mamba activate work

python_script="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/part_reco/systematic/sys1/fit_convolution_sys1.py"
echo "Running python fit_convolution_sys1.py --kind $kind --year $year --trigger $trigger"
python $python_script --kind $kind --year $year --trigger $trigger

python_script="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/part_reco/systematic/sys1/convolution_shape_sys1.py"
echo "Running python convolution_shape_sys1.py --kind $kind --year $year --trigger $trigger"
python $python_script --kind $kind --year $year --trigger $trigger
