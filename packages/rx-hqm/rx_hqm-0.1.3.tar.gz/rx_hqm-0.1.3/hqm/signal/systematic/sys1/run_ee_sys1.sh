#!/usr/bin/env bash

year=$1
trigger=$2
category=$3

source $HOME/.bashrc
mamba activate work

python_script="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/signal/systematic/sys1/fit_Bu2Kee_MC_sys1.py"
echo "Running python $python_script --year $year --trigger $trigger --category $category"
python $python_script --year $year --trigger $trigger --category $category
