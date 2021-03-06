#!/usr/bin/env bash

# based on P-WL/experiments/iterations_mutag.sh
# Starts an experiment about the number of iterations on the MUTAG data
# set. The performance of the *original* Weisfeiler Lehman features is plotted against the
# performance of the *topological* features.

name=Synth_P3

for dataset in ../../WWL/${name}/*; do
  GRAPHS=${dataset}/*.gml
  LABELS=${dataset}/Labels.txt
  SCRIPT=../src/main.py

  echo
  echo $dataset
  echo "h acc_topological sdev_topological acc_original sdev_original"

  for h in `seq 0 5`; do
    ACCURACY_TOP=`$SCRIPT -p 1 -n $h $GRAPHS -l $LABELS 2>&1 | grep Accuracy  | cut -f 2,4 -d " "`
    ACCURACY_ORG=`$SCRIPT   -u -n $h $GRAPHS -l $LABELS 2>&1 | grep Accuracy  | cut -f 2,4 -d " "`
    echo $h $ACCURACY_TOP $ACCURACY_ORG
  done
done | tee ${name}.results

# clean up the mess
mkdir ${name}.logs
mv None*.log ${name}.logs
