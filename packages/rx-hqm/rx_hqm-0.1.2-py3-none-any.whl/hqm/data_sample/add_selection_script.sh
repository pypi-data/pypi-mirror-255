#!/usr/bin/env bash

kind=$1
version=$2
year=$3

source $HOME/.bashrc
mamba activate work

target_dir=v6
input_dir=latest

python_script="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/data_sample/add_selection.py"
echo "python $python_script --kind $kind --version $version --year $year --trigger $trigger --target-dir $target_dir --input-dir $input_dir"
python $python_script --kind $kind --version $version --year $year --target-dir $target_dir --input-dir $input_dir
