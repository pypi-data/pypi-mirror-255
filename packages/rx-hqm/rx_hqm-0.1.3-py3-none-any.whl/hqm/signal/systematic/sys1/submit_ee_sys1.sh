all_trigger=("ETOS" "GTIS")
all_year=("all" "r1" "r2p1" "2011" "2012" "2015" "2016" "2017" "2018")
all_category=(0 1 2)

SUMBIT_SCRIPT="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/signal/systematic/sys1/run_ee_sys1.sh"

JOBDIR="$HOME/tmp/Jobs/ee_sys1"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
JOBDIR="$JOBDIR/$DATE"

mkdir -p $JOBDIR
rm    -f $JOBDIR/*.out
rm    -f $JOBDIR/*.err

for year in ${all_year[@]}; do
    for trigger in ${all_trigger[@]}; do
        for category in ${all_category[@]}; do

            OUTPUT_FILE="$JOBDIR/ee_sys1_%{ClusterId}"
            echo "year: $year, trigger: $trigger, category: $category"
            hep_sub -g lhcb -e "$OUTPUT_FILE.err" -o "$OUTPUT_FILE.out" -argu $year $trigger $category -mem 8000 -wt mid -np 4 $SUMBIT_SCRIPT
        done
    done
done
