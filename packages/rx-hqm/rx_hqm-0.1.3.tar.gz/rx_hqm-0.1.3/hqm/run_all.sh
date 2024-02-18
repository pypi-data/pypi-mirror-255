#!/usr/bin/env bash

# run this script in the directory where it is located
script_path=$(pwd)

# update signal
cd $script_path/signal
./run_ee.sh
./run_mm.sh

# update part_reco
cd $script_path/part_reco
./run_fit.sh
./run_convolution_shape.sh
