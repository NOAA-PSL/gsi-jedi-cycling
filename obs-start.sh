#!/bin/sh

#obs start script

 run_dir=/work2/noaa/da/weihuang/cycling/gdas-cycling
 datestr=2020010112
 obs_start_dir=${run_dir}/${datestr}

 if [ -d ${obs_start_dir} ]
 then

cat > ${run_dir}/obs_date.sh << EOF1
export obs_date=${datestr}
export obs_date_end=2020020100
EOF1

 fi


