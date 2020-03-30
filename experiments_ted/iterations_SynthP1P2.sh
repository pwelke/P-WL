#!/usr/bin/env bash

# Starts an experiment about the number of iterations on the MUTAG data
# set. The performance of the *original* features is plotted against the
# performance of the *topological* features.


for dataset in s60to80 s80to100 s160to180 s200to220 s200to250 s240to260; do
  GRAPHS=../../WWL/data/${dataset}/*.gml
  LABELS=../../WWL/data/${dataset}/Labels.txt
  SCRIPT=../src/main.py

  echo
  echo $dataset
  echo "h acc_topological sdev_topological acc_original sdev_original"

  for h in `seq 0 10`; do
    ACCURACY_TOP=`$SCRIPT -p 1 -n $h $GRAPHS -l $LABELS 2>&1 | grep Accuracy  | cut -f 2,4 -d " "`
    ACCURACY_ORG=`$SCRIPT   -u -n $h $GRAPHS -l $LABELS 2>&1 | grep Accuracy  | cut -f 2,4 -d " "`
    echo $h $ACCURACY_TOP $ACCURACY_ORG
  done
done | tee egonets.results
