#BSUB -P CSC303
#BSUB -W 0:30
#BSUB -nnodes 1
#BSUB -q debug
#BSUB -J mldl_test_job
#BSUB -o mldl%J.out
#BSUB -e mldl%J.err

module load  ibm-wml-ce/1.6.2-1
module load hdf5
export PYTHONPATH=/gpfs/alpine/world-shared/csc143/ganyushin/quip-app/ADIOS2-Python-fast/build/lib/python3.6/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=/gpfs/alpine/world-shared/csc143/ganyushin/quip-app/openslide/:$LD_LIBRARY_PATH

NODES=$(cat ${LSB_DJOB_HOSTFILE} | sort | uniq | grep -v login | grep -v batch | wc -l)

cd ./u24_lymphocyte/scripts/

# N SLIDES processed in parallel
NPROC=1
# every slide is processed by
GPU_NTHREADS=6

for n in $(seq 0 $((NPROC-1))); do
   jsrun -n1 -a1 -c7 -g1  --bind=proportional-packed:7 --launch_distribution=packed bash  ./prediction.sh $n $NPROC 0 $GPU_NTHREADS &
   jsrun -n1 -a1 -c7 -g1  --bind=proportional-packed:7 --launch_distribution=packed bash  ./prediction.sh $n $NPROC 1 $GPU_NTHREADS &
   jsrun -n1 -a1 -c7 -g1  --bind=proportional-packed:7 --launch_distribution=packed bash  ./prediction.sh $n $NPROC 2 $GPU_NTHREADS &
   jsrun -n1 -a1 -c7 -g1  --bind=proportional-packed:7 --launch_distribution=packed bash  ./prediction.sh $n $NPROC 3 $GPU_NTHREADS &
   jsrun -n1 -a1 -c7 -g1  --bind=proportional-packed:7 --launch_distribution=packed bash  ./prediction.sh $n $NPROC 4 $GPU_NTHREADS &
   jsrun -n1 -a1 -c7 -g1  --bind=proportional-packed:7 --launch_distribution=packed bash  ./prediction.sh $n $NPROC 5 $GPU_NTHREADS &
done
wait   

