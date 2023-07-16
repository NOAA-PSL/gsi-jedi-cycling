#!/bin/sh
#cold start script

 if [ "$#" -eq  "0" ]
 then
   runtype=jedi
 else
   runtype=$1
 fi

 current_dir=`pwd`
 datestr=2022010312
 dateend=2022011812

 run_dir=/work2/noaa/da/weihuang/EMC_cycling/${runtype}-cycling

 if [ ! -L ${run_dir}/${datestr} ]
 then
   mkdir -p ${run_dir}
   cd ${run_dir}
   ln -sf ../${datestr} .

   cold_start_dir=${run_dir}/${datestr}

   touch ${cold_start_dir}/cold_start_bias

   cd ${current_dir}

   cp textdata/gdas1.t00z.abias ${cold_start_dir}/.
   cp textdata/abias_pc ${cold_start_dir}/.

cat > ${run_dir}/analdate.sh << EOF1
export analdate=${datestr}
export analdate_end=${dateend}
EOF1

cat > ${run_dir}/fg_only.sh << EOF2
export fg_only=true
export cold_start=true
EOF2

 fi

 exit 0

