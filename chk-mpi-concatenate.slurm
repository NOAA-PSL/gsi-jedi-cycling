#!/bin/sh
#SBATCH -t 00:15:00
#SBATCH -A gsienkf
#SBATCH -N 1
#SBATCH --ntasks-per-node=40
#SBATCH -p bigmem
##SBATCH -p orion
#SBATCH -J mpi4py
#SBATCH -e mpi4py.%J.err
#SBATCH -o mpi4py.%J.out

#ulimit -n 131072

#Wei's default env is "gdasenv".

#module purge
#source ~/intelenv
#source ~/gdasenv

 source /home/weihuang/parioenv

 module load intel/2020.2 impi/2020.2

 libdir=/work/noaa/gsienkf/weihuang/lib
 export LD_LIBRARY_PATH=${libdir}/lib:$LD_LIBRARY_PATH

 datapath=/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling
 yyyymmddhh=2022011900

#input file fir.
 rundir=${datapath}/${yyyymmddhh}
 cd ${rundir}
 rm -f logdir/*

 enkfscripts=/work2/noaa/da/weihuang/EMC_cycling/scripts/jedi-cycling

#Jeff Whitaker
#2:21 PM
#I was able to finally get it to work by doing
#conda install -c conda-forge mpich
#conda install -c conda-forge  hdf5=*=*mpich*
#conda install -c conda-forge  libnetcdf=*=*mpich*
#conda install -c conda-forge  netcdf4=*=*mpich*
#
#2:22
#to be safe, run 'conda update -c conda-forge conda' first

#https://mpi4py.readthedocs.io/en/stable/install.html

#python -m pip install mpi4py

#env MPICC=/path/to/mpicc python -m pip install mpi4py

#pip keeps previouly built wheel files on its cache for future reuse.
#If you want to reinstall the mpi4py package using a different or
#updated MPI implementation, you have to either first remove the cached wheel file with:

# python -m pip cache remove mpi4py

#or ask pip to disable the cache:
# python -m pip install --no-cache-dir mpi4py


#obstype=sondes
 obstype=amsua_n19

 number_cores=40
 number_members=80

 time srun -N 1 -n ${number_cores} \
      python ${enkfscripts}/python_scripts/pympi-concanate-observer.py \
      --rundir=${datapath} \
      --datestr=${yyyymmddhh} \
      --nmem=${number_members} \
      --obstype=${obstype}

 exit 0

