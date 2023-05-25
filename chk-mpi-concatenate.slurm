#!/bin/sh
##SBATCH -q urgent
#SBATCH -t 00:30:00
#SBATCH -A gsienkf
#SBATCH -N 1  
#SBATCH --ntasks-per-node=40
#SBATCH -p bigmem
#SBATCH -J mpi4py
#SBATCH -e mpi4py.%J.err
#SBATCH -o mpi4py.%J.out

#source ~/visenv
#module load slurm py-netcdf4/1.5.3

datapath=/work2/noaa/da/weihuang/cycling/gdas-cycling
analdate=2020010200

export year=`echo $analdate |cut -c 1-4`
export month=`echo $analdate |cut -c 5-6`
export day=`echo $analdate |cut -c 7-8`
export hour=`echo $analdate |cut -c 9-10`
yyyymmddhh=${year}${month}${day}${hour}

#input file fir.
run_dir=${datapath}/${analdate}

source ~/gdasenv

 echo "concanate observer"
 time_start=$(date +%s)
 cd ${run_dir}
 obstype=ps

 number_members=81
#for obstype in sfc_ps sfcship_ps sondes_ps
#for obstype in sfc_ps sfcship_ps sondes_ps sondes amsua_n19
 for obstype in sondes amsua_n19 iasi_metop-b
 do
   time python ${enkfscripts}/python_scripts/concanate-observer.py \
        --run_dir=${run_dir} \
        --datestr=${yyyymmddhh} \
        --nmem=${number_members} \
        --obstype=${obstype} &
 done

 wait

time_end=$(date +%s)
echo "concanate-observer.py elapsed Time: $(($time_end-$time_start)) seconds"

