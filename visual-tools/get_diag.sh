#!/bin/bash

#set -x

 sdate=2022010500
 edate=2022010618
#------------------------------------------------------------------------------
#firstdirs=(/work2/noaa/da/weihuang/EMC_cycling/gsi-cycling)
#seconddirs=(/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling)
#firstlbls=(GSI_SondesAmsuaN19)
#secondlbls=(JEDI_SondesAmsuaN19)

 firstdirs=(/work2/noaa/da/weihuang/EMC_cycling/sts.jedi-cycling)
 seconddirs=(/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling)
 firstlbls=(STS)
 secondlbls=(MTS)

 tar cvf ~/jg.tar plot-jedi-gsi-diag.py get_diag.sh

#------------------------------------------------------------------------------
 incdate () {
   if [ $# != 2 ]; then
     echo "usage: incdate YYYYMMDDHH hrs"
     echo "where YYYYMMDDHH is a 10 character date string (e.g. 2002050312)"
     echo "and hrs is integer number of hours to increment YYYMMDDHH"
     exit 1
   fi

   ndate=`date -u -d "${1:0:4}-${1:4:2}-${1:6:2} ${1:8:2}:00:00 UTC $2 hour" +%Y%m%d%H`
 }

#------------------------------------------------------------------------------
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
     --lbl1=${lbl1} --lbl2=${lbl2} > obs_count_${flag}.csv

   python plot-jedi-gsi-diag.py --lbl1=${lbl1} --lbl2=${lbl2} \
	--output=1 >> obs_count_${flag}.csv

   dirname=${lbl2}-${lbl1}.${flag}
   rm -rf ${dirname}
   mkdir -p ${dirname}
   mv -f obs_count_${flag}.csv ${dirname}/.
   for fl in diag_omf_rmshumid diag_omf_rmstemp diag_omf_rmswind humidity_rms temp_rms wind_rms
   do
     mv -f ${fl}.png ${dirname}/${fl}_${flag}.png
   done
   for case in ${lbl1} ${lbl2}
   do
     mv -f stats_${case} ${dirname}/${case}_${flag}_stats
     mv -f stats_${case}.nc ${dirname}/${case}_${flag}_stats.nc
   done
   mv -f *stats* ${dirname}/.
   mv -f *.csv ${dirname}/.
   mv -f *.png ${dirname}/.

   tar uvf ~/jg.tar ${dirname}
 }

#------------------------------------------------------------------------------
 incdate $sdate 6

 for j in ${!firstdirs[@]}
 do
   frtdir=${firstdirs[$j]}
   scddir=${seconddirs[$j]}
   echo "frtdir: ${frtdir}, scddir: ${scddir}"

   plot_stats ${sdate} ${edate} 6  all    ${frtdir} ${scddir} ${firstlbls[$j]} ${secondlbls[$j]}
   plot_stats ${ndate} ${edate} 12 at_12h ${frtdir} ${scddir} ${firstlbls[$j]} ${secondlbls[$j]}
   plot_stats ${sdate} ${edate} 12 at_6h  ${frtdir} ${scddir} ${firstlbls[$j]} ${secondlbls[$j]}
 done

 exit 0

