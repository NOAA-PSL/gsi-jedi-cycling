#!/bin/sh

set -x

enkfscripts=/work2/noaa/da/weihuang/EMC_cycling/scripts/jedi-cycling
datapath=/work2/noaa/da/weihuang/EMC_cycling/sts.gsi-cycling
analdate=2022010500

# yr,mon,day,hr at middle of assim window (analysis time)
export year=`echo $analdate |cut -c 1-4`
export month=`echo $analdate |cut -c 5-6`
export day=`echo $analdate |cut -c 7-8`
export hour=`echo $analdate |cut -c 9-10`
yyyymmddhh=${year}${month}${day}${hour}

run_dir=${datapath}/${analdate}

source ${enkfscripts}/gdasenv
ulimit -s unlimited

echo "run Jedi starting at `date`"
time_start=$(date +%s)

cd ${run_dir}
rm -rf ioda_v2_data diag
mkdir -p ioda_v2_data diag

for type in amsua_n19 conv_q conv_t conv_uv
do
  cp diag_${type}_ges.${yyyymmddhh}_ensmean.nc4 diag/.
done

python ${jediblddir}/bin/proc_gsi_ncdiag.py \
       -o ioda_v2_data diag

time_end=$(date +%s)
echo "proc_gsi_ncdiag.py elapsed Time: $(($time_end-$time_start)) seconds"

cd ioda_v2_data

flst="sondes_tsen_obs_${yyyymmddhh}.nc4 sondes_tv_obs_${yyyymmddhh}.nc4 sondes_uv_obs_${yyyymmddhh}.nc4 sondes_q_obs_${yyyymmddhh}.nc4"
python ${jediblddir}/bin/combine_obsspace.py \
  -i sondes_tsen_obs_${yyyymmddhh}.nc4 \
     sondes_tv_obs_${yyyymmddhh}.nc4 \
     sondes_uv_obs_${yyyymmddhh}.nc4 \
     sondes_q_obs_${yyyymmddhh}.nc4 \
  -o sondes_obs_${yyyymmddhh}.nc4

time_end=$(date +%s)
echo "combine_obsspace.py elapsed Time: $(($time_end-$time_start)) seconds"

