#!/bin/sh

cd ${datapath2}

iaufhrs2=`echo $iaufhrs | sed 's/,/ /g'`

echo "compute ensemble mean analyses..."

for nhr_anal in $iaufhrs2; do

charfhr="fhr"`printf %02i $nhr_anal`
charfhr2=`printf %02i $nhr_anal`

if [ $cleanup_ensmean_enkf == 'true' ] || ([ $cleanup_ensmean_enkf == 'false' ] && [ ! -s ${datapath}/${analdate}/incr_${analdate}_${charfhr}_ensmean ]); then
   /bin/rm -f incr_${analdate}_${charfhr}_ensmean
   export PGM="${execdir}/getsigensmeanp_smooth.x ${datapath2}/ incr_${analdate}_${charfhr}_ensmean incr_${analdate}_${charfhr} ${nanals}"
   ${enkfscripts}/runmpi
fi

done
ls -l ${datapath2}/incr_${analdate}*ensmean
