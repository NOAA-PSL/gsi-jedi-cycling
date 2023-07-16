#!/bin/sh

 current_dir=`pwd`
# cold start script
 datestr=2022010312
 dateend=2022011812

 run_dir=/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling
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

 exit 0

 cd ${cold_start_dir}

 num_member=80
 n=1
 while [ $n -le ${num_member} ]
 do
   if [ $n -lt 10 ]
   then
     member_str=00${n}
   elif [ $n -lt 100 ]
   then
     member_str=0${n}
   else
     member_str=${n}
   fi

   dirname=mem${member_str}
   mkdir -p analysis/increment/${dirname}/INPUT

   n=$(( $n + 1 ))
 done

