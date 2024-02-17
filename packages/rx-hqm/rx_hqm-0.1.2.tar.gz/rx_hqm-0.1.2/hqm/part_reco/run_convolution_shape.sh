for kind in "psi2S_high" "psi2S_psi2S" "psi2S_Jpsi" "Jpsi_psi2S" "Jpsi_Jpsi" ; do
    for year in 2011 2012 2015 2016 2017 2018; do
        for trigger in "ETOS" "GTIS"; do
            echo "Running python convolution_shape.py --kind $kind --year $year --trigger $trigger"
            python convolution_shape.py --kind $kind --year $year --trigger $trigger
        done
    done
done
