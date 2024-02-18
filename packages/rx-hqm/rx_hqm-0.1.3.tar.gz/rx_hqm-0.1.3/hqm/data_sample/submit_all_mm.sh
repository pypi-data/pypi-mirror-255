#!/usr/bin/env bash


OUTPUT_DIR="root_sample"
WAIT_TIME="mid"
JOB_SEL_SCRIPT="/afs/ihep.ac.cn/users/q/qi/work/projects/RK/high_q2_model/hqm/data_sample/job_sel"

# 2018
for year in 2011 2012 2015 2016 2017 2018; do
    $JOB_SEL_SCRIPT -p data_mm -v v10.21p2 -d $year -t MTOS -q high -r truth-q2-mass-bdt-jpsi_misid -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME -c 0

    $JOB_SEL_SCRIPT -p sign_mm -v v10.21p2 -d $year -t MTOS -q high -r truth-q2-mass-bdt-jpsi_misid -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
    $JOB_SEL_SCRIPT -p ctrl_mm -v v10.21p2 -d $year -t MTOS -q high -r truth-q2-mass-bdt-jpsi_misid -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
    $JOB_SEL_SCRIPT -p psi2_mm -v v10.21p2 -d $year -t MTOS -q high -r truth-q2-mass-bdt-jpsi_misid -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME -c 0
done

# $JOB_SEL_SCRIPT -p bp_x -v v10.17 -d 2016 -t MTOS -q high -r q2-mass-bdt -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# $JOB_SEL_SCRIPT -p bd_x -v v10.17 -d 2016 -t MTOS -q high -r q2-mass-bdt -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# $JOB_SEL_SCRIPT -p bs_x -v v10.17 -d 2016 -t MTOS -q high -r q2-mass-bdt -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME

# $JOB_SEL_SCRIPT -p bpks -v v10.18is -d 2018 -t MTOS -q high -r q2-mass -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# $JOB_SEL_SCRIPT -p bdks -v v10.18is -d 2018 -t MTOS -q high -r q2-mass-bdt -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME -c 0
# $JOB_SEL_SCRIPT -p bdkpi -v v10.18is -d 2018 -t MTOS -q high -r q2-mass -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME


# 2016
# $JOB_SEL_SCRIPT -p data -v v10.11tf -d 2016 -t MTOS -q high -r q2-mass-bdt -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME

# $JOB_SEL_SCRIPT -p sign -v v10.10tf -d 2016 -t MTOS -q high -r q2-mass-bdt -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# $JOB_SEL_SCRIPT -p ctrl_mm -v v10.14 -d 2016 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# $JOB_SEL_SCRIPT -p psi2 -v v10.14 -d 2016 -t MTOS -q high -r q2-mass-bdt -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME


# # mm Jpsi
# # B0 -> Jpsi Ks0
# $JOB_SEL_SCRIPT -p 11144001 -v v10.20 -d 2018 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# # B+ -> Jpsi Ks+
# $JOB_SEL_SCRIPT -p 12143401 -v v10.20 -d 2018 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# # B+ -> Jpsi K1 (-> Ks+ pi0)
# $JOB_SEL_SCRIPT -p 12143440 -v v10.20 -d 2016 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# # B+ -> Jpsi K1 (-> K+ w)
# $JOB_SEL_SCRIPT -p 12145410 -v v10.20 -d 2016 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# # B+ -> Jpsi K1 (inclusive)
# # $JOB_SEL_SCRIPT -p 12245000 -v v10.20 -d 2018 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME
# # B+ -> Jpsi K+ pi+ pi-
# $JOB_SEL_SCRIPT -p 12145090 -v v10.20 -d 2018 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME

# mm psi2S
# B0 -> psi2S Ks0
# $JOB_SEL_SCRIPT -p 11144011 -v v10.20 -d 2018 -t MTOS -q high -r truth-q2-mass-bdt-jpsi_misid -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME -c 0
# # B+ -> psi2S K+ pi+ pi-
# $JOB_SEL_SCRIPT -p 12145072 -v v10.20 -d 2018 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME


# mm cmb
# B+ -> K+ mu- mu-
# $JOB_SEL_SCRIPT -p cmb_mm -v v10.18dc -d 2018 -t MTOS -q high -r q2-mass-bdt-truth -f $OUTPUT_DIR -b 0 -n 10 -w $WAIT_TIME -c 0
