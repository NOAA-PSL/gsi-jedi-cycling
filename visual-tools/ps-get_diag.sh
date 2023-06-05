#!/bin/bash

 set -x

 sdate=2020010112
 edate=2020011400
#edate=2020012112

 plot_stats () {
   argnum=$#
   if [ $argnum -lt 4 ]
   then
     echo "Usage: $0 sdate edate interval, for example: $0 2020010112 2020010812 12 all"
     exit -1
   fi

   sdate=$1
   edate=$2
   interval=$3
   flag=$4
   dir1=$5
   dir2=$6
   lbl1=$7
   lbl2=$8

  #argnum=0
  #echo "@ gives:"
  #for arg in "$@"
  #do
  #  argnum=$(( argnum + 1 ))
  #  echo "Arg $argnum: <$arg>"
  #done

   python diag.py --sdate=$sdate --edate=$edate \
     --dir1=${dir1} --dir2=${dir2} --interval=$interval \
     --lbl1=${lbl1} --lbl2=${lbl2} \
     --datadir=/work2/noaa/da/weihuang/cycling > obs_count_${flag}.csv

   python plot-jedi-gsi-diag.py --lbl1=${lbl1} --lbl2=${lbl2} \
	--output=1 >> obs_count_${flag}.csv

   dirname=${lbl2}-${lbl1}.$flag
   rm -rf ${dirname}
   mkdir -p ${dirname}
   mv -f obs_count_${flag}.csv ${dirname}/.
   for fl in diag_omf_rmshumid diag_omf_rmstemp diag_omf_rmswind humidity_rms temp_rms wind_rms
   do
     mv -f ${fl}.png ${dirname}/${fl}_${flag}.png
   done
   for case in ${dir1} ${dir2}
   do
     mv -f stats_${case} ${dirname}/${case}_${flag}_stats
     mv -f stats_${case}.nc ${dirname}/${case}_${flag}_stats.nc
   done
   mv -f *stats* ${dirname}/.
   mv -f *.csv ${dirname}/.
   mv -f *.png ${dirname}/.
 }

 tar cvf ~/jg.tar plot-jedi-gsi-diag.py get_diag.sh
#------------------------------------------------------------------------------
#firstlist=(gsi-cycling)
#secondlist=(gdas-cycling)
#firstlbls=(GSI_sai)
#secondlbls=(JEDI_sai)

#firstlist=(sondes-rerun.gsi-cycling)
#secondlist=(sondes-rerun.gdas-cycling)
#firstlbls=(sondes-rerun.GSI)
#secondlbls=(sondes-rerun.JEDI)

#firstlist=(sondes.gsi_C96_lgetkf_sondesonly)
#secondlist=(sondes.gdas-cycling)
#firstlbls=(sondes.GSI)
#secondlbls=(sondes.JEDI)

 firstlist=(gsi_C96_lgetkf_psonly)
 secondlist=(sfc-station-only.gdas-cycling)
 firstlbls=(GSI)
 secondlbls=(JEDI)

 deltlist=(0 6 0)
 hourlist=(6 12 12)
 caselist=(all at_12h at_6h)
 for j in ${!firstlist[@]}
 do
   first=${firstlist[$j]}
   second=${secondlist[$j]}
   echo "first: ${first}, second: ${second}"

   for n in ${!hourlist[@]}
   do
     hour=${hourlist[$n]}
     case=${caselist[$n]}
     stime=$(( $sdate + ${deltlist[$n]} ))
     plot_stats ${stime} ${edate} ${hour} ${case} ${first} ${second} ${firstlbls[$j]} ${secondlbls[$j]}
   done
   tar uvf ~/jg.tar ${secondlbls[$j]}-${firstlbls[$j]}.*
 done

 exit 0

