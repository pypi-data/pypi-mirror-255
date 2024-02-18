#!/usr/bin/env bash

for q2 in "jpsi" "psi2"; do
    for year in 2011 2012 2015 2016 2017 2018; do
        mass_variable="B_M"

        echo "Running: python comb_shape_mm.py --q2 $q2 --year $year --mass-variable $mass_variable"
        python comb_shape_mm.py --q2 $q2 --year $year --mass-variable $mass_variable
    done
done
