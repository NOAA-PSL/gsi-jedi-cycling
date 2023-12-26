#!/bin/sh

#set -x

 module load cdo/1.9.10

#----------------------------------------------------------------------------------
 if [ $# != 2 ]; then
   echo "usage: $0 toprundir YYYYMMDDHH"
   echo "where toprundir is the run dir above each datetime"
   echo "YYYYMMDDHH is a 10 character date string (e.g. 2002050312)"
   exit -1
 fi

#----------------------------------------------------------------------------------
 advance_ymdh() {
   if [ $# != 2 ]; then
     echo "usage: incdate YYYYMMDDHH hrs"
     echo "where YYYYMMDDHH is a 10 character date string (e.g. 2002050312)"
     echo "and hrs is integer number of hours to increment YYYMMDDHH"
     exit -1
   fi
   echo `date -u -d "${1:0:4}-${1:4:2}-${1:6:2} ${1:8:2}:00:00 UTC $2 hour" +%Y%m%d%H`
 }

#----------------------------------------------------------------------------------
 toprundir=$1
 ymdh=$2

 indir=${toprundir}/${ymdh}
 outdir=${toprundir}/${ymdh}/mem000/INPUT
 rm -rf ${outdir}
 mkdir -p ${outdir}

#----------------------------------------------------------------------------------
#typelist=(fv_core.res fv_srf_wnd.res fv_tracer.res oro_data phy_data sfc_data)
 typelist=(fv_core.res fv_srf_wnd.res fv_tracer.res phy_data sfc_data)

 if [ ! -f ${outdir}/coupler.res ]
 then
   for fl in coupler.res grid_spec.nc atm_stoch.res.nc
   do
     if [ -f ${indir}/mem001/INPUT/$fl ]
     then
       cp ${indir}/mem001/INPUT/$fl ${outdir}/.
     fi
   done

   if [ -f ${indir}/mem001/INPUT/C96_grid.tile1.nc ]
   then
     cp ${indir}/mem001/INPUT/C96_grid.tile*.nc ${outdir}/.
   fi
 fi

 for i in ${!typelist[@]}
 do
  #echo "element $i is ${typelist[$i]}"
   type=${typelist[$i]}
  #echo "Working on type: $type"

   tile=0
   while [ $tile -lt 6 ]
   do
     tile=$(( $tile + 1 ))
    #echo "\tWorking on tile: $tile"

     ofile=${outdir}/${type}.tile${tile}.nc
     rm -f $ofile

     ifiles=`ls ${indir}/mem*/INPUT/${type}.tile${tile}.nc`
     cdo ensmean $ifiles $ofile &
   done
   wait
 done

#----------------------------------------------------------------------------------
 ymdhm6=`advance_ymdh $ymdh -6`

 indir=${toprundir}/${ymdhm6}
 outdir=${toprundir}/${ymdhm6}/mem000/RESTART
 mkdir -p ${outdir}
 
#----------------------------------------------------------------------------------
 for hh in 3 9
 do
   ymdhfcst=`advance_ymdh $ymdhm6 $hh`
   year=`echo $ymdhfcst |cut -c 1-4`
   month=`echo $ymdhfcst |cut -c 5-6`
   day=`echo $ymdhfcst |cut -c 7-8`
   hour=`echo $ymdhfcst |cut -c 9-10`
   yyyymmdd=${year}${month}${day}

   echo "ymdhm6=$ymdhm6, hh=$hh"
   echo "ymdhfcst=$ymdhfcst, hour=$hour"
   echo "yyyymmdd=$yyyymmdd"

   dtstr=${yyyymmdd}.${hour}0000

   echo "dtstr=$dtstr"
   
   if [ ! -f ${outdir}/${dtstr}.coupler.res ]
   then
     for fl in coupler.res grid_spec.nc atm_stoch.res.nc
     do
       if [ -f ${indir}/mem001/RESTART/${dtstr}.$fl ]
       then
         cp ${indir}/mem001/RESTART/${dtstr}.$fl ${outdir}/.
       fi
     done

     if [ -f ${indir}/mem001/RESTART/C96_grid.tile1.nc ]
     then
       cp ${indir}/mem001/RESTART/C96_grid.tile*.nc ${outdir}/.
     fi
   fi

   for i in ${!typelist[@]}
   do
    #echo "element $i is ${typelist[$i]}"
     type=${typelist[$i]}
    #echo "Working on type: $type"

     tile=0
     while [ $tile -lt 6 ]
     do
       tile=$(( $tile + 1 ))
      #echo "\tWorking on tile: $tile"

       ofile=${outdir}/${dtstr}.${type}.tile${tile}.nc
       rm -f $ofile

       ifiles=`ls ${indir}/mem*/RESTART/${dtstr}.${type}.tile${tile}.nc`
       cdo ensmean $ifiles $ofile &
     done
     wait
   done
 done

