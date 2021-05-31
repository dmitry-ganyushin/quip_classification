#!/bin/bash
THREAD=$1 
NTHREADS=$2
GPU_THREAD=$3
GPU_NTHREADS=$4


set -x 
cd ../
source ./conf/variables.sh

cd prediction
bash start.sh ${THREAD}  ${NTHREADS} ${GPU_THREAD}  ${GPU_NTHREADS}
cd ..

#wait;
#
#cd heatmap_gen
#nohup bash start.sh &
#cd ..
#
#wait;
set +x 
exit 0
