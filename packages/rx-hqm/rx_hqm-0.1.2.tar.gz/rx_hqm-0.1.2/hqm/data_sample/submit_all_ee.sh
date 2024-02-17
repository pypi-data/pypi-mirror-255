#!/usr/bin/env bash


# ETOS

OUTPUT_DIR="root_sample"
WAIT_TIME="mid"
JOB_SEL_SCRIPT="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/data_sample/job_sel"

for year in 2011 2012 2015 2016 2017 2018; do
    for trigger in "ETOS" "GTIS"; do
        $JOB_SEL_SCRIPT -p data_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt-pid -f $OUTPUT_DIR -b 1 -n 10 -w $WAIT_TIME

        $JOB_SEL_SCRIPT -p sign_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 10 -w $WAIT_TIME
        $JOB_SEL_SCRIPT -p ctrl_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 10 -w $WAIT_TIME
        $JOB_SEL_SCRIPT -p psi2_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 10 -w $WAIT_TIME

        $JOB_SEL_SCRIPT -p bpks_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 10 -w $WAIT_TIME
        $JOB_SEL_SCRIPT -p bdks_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 10 -w $WAIT_TIME
        $JOB_SEL_SCRIPT -p bdkpi_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 10 -w $WAIT_TIME

        $JOB_SEL_SCRIPT -p bpk1_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 2 -w $WAIT_TIME
        $JOB_SEL_SCRIPT -p bpk2_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 2 -w $WAIT_TIME
        $JOB_SEL_SCRIPT -p bsphi_ee -v v10.21p2 -d $year -t $trigger -q high -r q2-mass-truth-bdt -f $OUTPUT_DIR -b 1 -n 5 -w $WAIT_TIME
    done
done
