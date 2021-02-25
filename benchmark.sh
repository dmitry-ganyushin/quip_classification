#BSUB -P CSC143
#BSUB -W 0:30
#BSUB -nnodes 1
#BSUB -q debug
#BSUB -J mldl_test_job
#BSUB -o mldl%J.out
#BSUB -e mldl%J.err

module load  ibm-wml-ce/1.6.2-1

NODES=$(cat ${LSB_DJOB_HOSTFILE} | sort | uniq | grep -v login | grep -v batch | wc -l)

cd ./u24_lymphocyte/scripts/

jsrun -n$((NODES*6)) -a1 -c7 -g1 -r6 --bind=proportional-packed:7 --launch_distribution=packed bash  ./prediction.sh