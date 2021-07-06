#!/bin/bash
source ../conf/variables.sh

set -x
COD_PARA=$1
MAX_PARA=$2
IN_FOLDER=${SVS_INPUT_PATH}
OUT_FOLDER=${PATCH_PATH}
BATCH_FOLDER=${BATCH_PATH}
echo $COD_PARA
echo $MAX_PARA
echo $IN_FOLDER
echo $OUT_FOLDER


LINE_N=0
for files in ${IN_FOLDER}/*.*; do
    LINE_N=$((LINE_N+1))
    if [ $((LINE_N % MAX_PARA)) -ne ${COD_PARA} ]; then continue; fi

    SVS=`echo ${files} | awk -F'/' '{print $NF}'`
    python save_svs_to_tiles.py $SVS $IN_FOLDER $OUT_FOLDER
    if [ $? -ne 0 ]; then
        echo "failed extracting patches for " ${SVS}.bp
        rm -rf ${OUT_FOLDER}/${SVS}.bp
    fi
    python make_batches.py ${OUT_FOLDER}/${SVS}.bp ${BATCH_FOLDER}/${SVS}.bp
    if [ $? -ne 0 ]; then
        echo "failed making patches for " ${SVS}.bp
        rm -rf ${BATCH_FOLDER}/${SVS}.bp
    fi
done
set +x
exit 0;


