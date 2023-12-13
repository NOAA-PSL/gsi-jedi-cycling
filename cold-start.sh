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
 dateend=2022010400
#datestr=2022012000
#dateend=2022012100

 run_dir=/work2/noaa/da/weihuang/EMC_cycling/${runtype}-cycling
 cold_start_dir=${run_dir}/${datestr}

 if [ ! -L ${cold_start_dir} ]
 then
   mkdir -p ${run_dir}
   cd ${run_dir}
   ln -sf ../${datestr} .

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

   cd ${run_dir}
   if [ ! -L ${datestr} ]
   then
     ln -sf ../${datestr} .
   fi
 fi

 exit 0

