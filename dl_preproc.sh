#BSUB -P CSC303
#BSUB -W 0:30
#BSUB -nnodes 1
#BSUB -q debug
#BSUB -J mldl_test_job
#BSUB -o mldl%J.out
#BSUB -e mldl%J.err

module load  ibm-wml-ce/1.6.2-1
#conda activate ibm-wml-ce-1.6.2-1-dg
conda activate ibm-wml-ce-1.6.2-1
module load hdf5
#ADIOS2
export PYTHONPATH=/gpfs/alpine/world-shared/csc143/ganyushin/quip_app/ADIOS2-Python-fast/build/lib/python3.6/site-packages:$PYTHONPATH
#Openslide-python
export PYTHONPATH=/gpfs/alpine/world-shared/csc143/ganyushin/quip_app/openslide-python-1.1.2/build/lib.linux-ppc64le-3.6:$PYTHONPATH
#openslide - so
export LD_LIBRARY_PATH=/gpfs/alpine/world-shared/csc143/ganyushin/quip_app/openslide-rpm/usr/lib64/:$LD_LIBRARY_PATH
#openjpeg
export LD_LIBRARY_PATH=/gpfs/alpine/world-shared/csc143/ganyushin/quip_app/libopenjpeg1-rpm/usr/lib64:$LD_LIBRARY_PATH

NODES=$(cat ${LSB_DJOB_HOSTFILE} | sort | uniq | grep -v login | grep -v batch | wc -l)

cd ./u24_lymphocyte/scripts/

NPROC=6

for n in $(seq 0 $((NPROC-1))); do
   jsrun -n1 -a1 -c1  ./preproc.sh $n $NPROC &
done
wait

