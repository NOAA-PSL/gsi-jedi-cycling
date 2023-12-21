#!/bin/sh

enkfscripts=/work2/noaa/da/weihuang/EMC_cycling/scripts/dev.jedi-cycling
datapath=/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling
analdate=2020010100

# yr,mon,day,hr at middle of assim window (analysis time)
export year=`echo $analdate |cut -c 1-4`
export month=`echo $analdate |cut -c 5-6`
export day=`echo $analdate |cut -c 7-8`
export hour=`echo $analdate |cut -c 9-10`
yyyymmddhh=${year}${month}${day}${hour}

run_dir=${datapath}/${analdate}

#source ~/gdasenv
source ${enkfscripts}/gdasenv
ulimit -s unlimited

echo "run Jedi starting at `date`"

mkdir -p ${run_dir}
cd ${run_dir}

#--------------------------------------------------------------------------------------------
 cp ${enkfscripts}/genyaml/config.template .
 cp ${enkfscripts}/genyaml/halo.distribution .
 cp ${enkfscripts}/genyaml/rr.distribution .
 cp ${enkfscripts}/genyaml/sondes.yaml .
 cp ${enkfscripts}/genyaml/amsua_n15.yaml .
 cp ${enkfscripts}/genyaml/amsua_n18.yaml .
 cp ${enkfscripts}/genyaml/amsua_n19.yaml .

 export observer_layout_x=3
 export observer_layout_y=4
 export solver_layout_x=12
 export solver_layout_y=22
 export NMEM_ENKF=80

 python ${enkfscripts}/genyaml/gen-mts-config.py \
   --template=config.template \
   --year=${year} \
   --month=${month} \
   --day=${day} \
   --hour=${hour} \
   --intv=3

 exit 0

#--------------------------------------------------------------------------------------------
 python ${enkfscripts}/genyaml/genyaml.py \
   --config=config.yaml \
   --observer=${enkfscripts}/genyaml/getkf.yaml.template.rr.observer.mts \
   --solver=${enkfscripts}/genyaml/getkf.yaml.template.solver.mts \
   --numensmem=${NMEM_ENKF} \
   --obsdir=observer

