for year in "all" "r1" "r2p1" 2011 2012 2015 2016 2017 2018; do
    for trigger in "ETOS" "GTIS"; do
        for category in 0 1 2; do
            echo "Running python fit_Bu2Kee_MC.py --year $year --trigger $trigger --category $category"
            python fit_Bu2Kee_MC.py --year $year --trigger $trigger --category $category
        done
    done
done
