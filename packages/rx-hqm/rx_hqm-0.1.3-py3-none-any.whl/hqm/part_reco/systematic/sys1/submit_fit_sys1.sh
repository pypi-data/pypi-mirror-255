all_trigger=("ETOS" "GTIS")
all_year=("2011" "2012" "2015" "2016" "2017" "2018")
all_kind=("psi2S_high" "psi2S_psi2S" "psi2S_Jpsi" "Jpsi_psi2S" "Jpsi_Jpsi")

SUMBIT_SCRIPT="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/part_reco/systematic/sys1/run_fit_sys1.sh"

JOBDIR="$HOME/tmp/Jobs/fit_convolution_sys1"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
JOBDIR="$JOBDIR/$DATE"

mkdir -p $JOBDIR
rm    -f $JOBDIR/*.out
rm    -f $JOBDIR/*.err

for year in ${all_year[@]}; do
    for trigger in ${all_trigger[@]}; do
        for kind in ${all_kind[@]}; do

            OUTPUT_FILE="$JOBDIR/fit_convolution_sys1_%{ClusterId}"
            echo "year: $year, trigger: $trigger, kind: $kind"
            hep_sub -g lhcb -e "$OUTPUT_FILE.err" -o "$OUTPUT_FILE.out" -argu $year $trigger $kind -mem 8000 -wt mid -np 4 $SUMBIT_SCRIPT
        done
    done
done
