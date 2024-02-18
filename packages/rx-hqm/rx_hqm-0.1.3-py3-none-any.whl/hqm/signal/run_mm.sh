for year in "all" "r1" "r2p1" 2011 2012 2015 2016 2017 2018; do
    echo "Running python fit_Bu2Kmm_MC.py --year $year"
    python fit_Bu2Kmm_MC.py --year $year
done
