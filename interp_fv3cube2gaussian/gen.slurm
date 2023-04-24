#!/bin/sh
##SBATCH -q urgent
#SBATCH -t 05:50:00
#SBATCH -A gsienkf
#SBATCH -N 1  
#SBATCH --ntasks-per-node=40
#SBATCH -p orion
#SBATCH -J genwgt
#SBATCH -e genwgt.%J.err
#SBATCH -o genwgt.%J.out

 source ~/gdasenv

 cd /work2/noaa/da/weihuang/cycling/scripts/gdas-cycling/interp_fv3cube2gaussian

 rm -f gaussianC192weights.nc4

 time gen_weights.exe

