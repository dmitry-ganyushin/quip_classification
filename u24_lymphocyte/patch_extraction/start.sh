#!/bin/bash
set -x
source ../conf/variables.sh

bash save_svs_to_tiles.sh 0 1  > ${LOG_OUTPUT_FOLDER}/log.save_svs_to_tiles.thread_0.txt 2>&1
#bash save_svs_to_tiles.sh 0 6  > ${LOG_OUTPUT_FOLDER}/log.save_svs_to_tiles.thread_0.txt 2>&1
#bash save_svs_to_tiles.sh 1 6  > ${LOG_OUTPUT_FOLDER}/log.save_svs_to_tiles.thread_1.txt 2>&1
#bash save_svs_to_tiles.sh 2 6  > ${LOG_OUTPUT_FOLDER}/log.save_svs_to_tiles.thread_2.txt 2>&1
#bash save_svs_to_tiles.sh 3 6  > ${LOG_OUTPUT_FOLDER}/log.save_svs_to_tiles.thread_3.txt 2>&1
#bash save_svs_to_tiles.sh 4 6  > ${LOG_OUTPUT_FOLDER}/log.save_svs_to_tiles.thread_3.txt 2>&1
#bash save_svs_to_tiles.sh 5 6  > ${LOG_OUTPUT_FOLDER}/log.save_svs_to_tiles.thread_3.txt 2>&1
#wait
set +x 
exit 0
