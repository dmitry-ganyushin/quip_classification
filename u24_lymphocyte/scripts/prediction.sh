#!/bin/bash
cd ../
source ./conf/variables.sh

cd prediction
bash start.sh
cd ..

wait;
#
#cd heatmap_gen
#nohup bash start.sh &
#cd ..
#
#wait;

exit 0
