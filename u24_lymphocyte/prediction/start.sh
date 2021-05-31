#!/bin/bash
THREAD=$1
NTHREADS=$2
GPU_THREAD=$3
GPU_NTHREADS=$4

set -x 
source ../conf/variables.sh

echo $PATCH_PATH 
echo $LYM_CNN_PRED_DEVICE

cd lymphocyte
bash pred_thread_lym.sh \
    ${PATCH_PATH} ${THREAD} ${NTHREADS} ${GPU_THREAD} ${GPU_NTHREADS} ${LYM_CNN_PRED_DEVICE} \
    > ${LOG_OUTPUT_FOLDER}/log.pred_thread_lym_"${THREAD}"_"${GPU_THREAD}".txt 2>&1
cd ..

#cd necrosis
#nohup bash pred_thread_nec.sh \
#    ${PATCH_PATH} 0 1 ${NEC_CNN_PRED_DEVICE} \
#    &> ${LOG_OUTPUT_FOLDER}/log.pred_thread_nec_0.txt &
#cd ..
#
#cd color
#nohup bash color_stats.sh ${PATCH_PATH} 0 2 \
#    &> ${LOG_OUTPUT_FOLDER}/log.color_stats_0.txt &
#nohup bash color_stats.sh ${PATCH_PATH} 1 2 \
#    &> ${LOG_OUTPUT_FOLDER}/log.color_stats_1.txt &
#cd ..

#wait
set +x 
exit 0
