#!/bin/bash
set -x
source ../../conf/variables.sh

FOLDER=$1
# PARAL = [0, MAX_PARAL-1]
PARAL=$2      # a number of this particular process
MAX_PARAL=$3  # tital number of processes
GPU_THREAD=$4
GPU_NTHREADS=$5

DEVICE=$6

echo "Device=$DEVICE"
DATA_FILE="patch-level-lym.txt_${GPU_THREAD}"
DONE_FILE=extraction_done.txt

if [ ${EXTERNAL_LYM_MODEL} -eq 0 ]; then
    EXEC_FILE=pred.py
else
    EXEC_FILE=pred_by_external_model.py
fi

PRE_FILE_NUM=0
while [ 1 ]; do
    LINE_N=0
    FILE_NUM=0
    EXTRACTING=0
    FILE_LIST=`du -s ${FOLDER}/*/ | sort -r |  awk '{ print $2 }'`
    for files in ${FILE_LIST}; do
        FILE_NUM=$((FILE_NUM+1))
        #if [ ! -f ${files}/${DONE_FILE} ]; then EXTRACTING=1; fi

        LINE_N=$((LINE_N+1))
        if [ $((LINE_N % MAX_PARAL)) -ne ${PARAL} ]; then continue; fi

        #if [ -f ${files}/${DONE_FILE} ]; then
            if [ ! -f ${files}/${DATA_FILE} ]; then
                echo ${files}/${DATA_FILE} generating
                THEANO_FLAGS="device=${DEVICE}" python -u ${EXEC_FILE} \
                    ${files} ${LYM_NECRO_CNN_MODEL_PATH} ${DATA_FILE} ${LYM_PREDICTION_BATCH_SIZE} ${GPU_THREAD} ${GPU_NTHREADS} ${DEVICE}
            fi
        #fi
    done

    if [ ${EXTRACTING} -eq 0 ] && [ ${PRE_FILE_NUM} -eq ${FILE_NUM} ]; then break; fi
    PRE_FILE_NUM=${FILE_NUM}
done
set +x
exit 0
