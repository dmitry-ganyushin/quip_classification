#!/bin/bash
THREAD=$1 
NTHREADS=$2

set -x 
cd ../
source ./conf/variables.sh

cd prediction
bash start.sh ${THREAD}  ${NTHREADS}
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
