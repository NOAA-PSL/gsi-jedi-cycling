#!/bin/sh
##SBATCH -q urgent
#SBATCH -t 00:10:00
#SBATCH -A gsienkf
#SBATCH -N 3 
#SBATCH --ntasks-per-node=40
##SBATCH -p bigmem
#SBATCH -p orion
#SBATCH -J mpi4py
#SBATCH -e mpi4py.%J.err
#SBATCH -o mpi4py.%J.out

 MYHOST=`hostname -s`
 MYRANK=$PMI_RANK           # this variable may depend on your execution environment

 export STD_OUT=stdout.$MYHOST.$MYRANK
 export STD_ERR=stderr.$MYHOST.$MYRANK

 source ~/visenv
 module load slurm py-netcdf4/1.5.3

 datapath=/work2/noaa/da/weihuang/cycling/gdas-cycling
 yyyymmddhh=2020010200

#input file fir.
 rundir=${datapath}/${yyyymmddhh}
 cd ${rundir}

 enkfscripts=/work2/noaa/da/weihuang/cycling/scripts/gdas-cycling
 echo "concatenate observer"
 time_start=$(date +%s)
 obstype=sondes
 number_members=81

 time srun -n ${number_members} \
      python ${enkfscripts}/python_scripts/pympi-concanate-observer.py \
      --rundir=${rundir} \
      --datestr=${yyyymmddhh} \
      --nmem=${number_members} \
      --obstype=${obstype}

 exit 0

#for obstype in sfc_ps sfcship_ps sondes_ps
#for obstype in sfc_ps sfcship_ps sondes_ps sondes amsua_n19
 for obstype in sondes amsua_n19 iasi_metop-b
 do
   time python ${enkfscripts}/python_scripts/concanate-observer.py \
        --rundir=${rundir} \
        --datestr=${yyyymmddhh} \
        --nmem=${number_members} \
        --obstype=${obstype} &
 done

 wait

time_end=$(date +%s)
echo "concanate-observer.py elapsed Time: $(($time_end-$time_start)) seconds"

