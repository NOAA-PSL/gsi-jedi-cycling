#!/bin/sh

#set -x

main_start=$(date +%s)

# main driver script
# gsi gain or gsi covariance GSI EnKF (based on ensemble mean background)
# optional high-res control fcst replayed to ens mean analysis

# allow this script to submit other scripts with LSF
unset LSB_SUB_RES_REQ 

echo "nodes = $NODES"

export startupenv="${datapath}/obs_date.sh"
source $startupenv
# substringing to get yr, mon, day, hr info
export yr=`echo $obs_date | cut -c1-4`
export mon=`echo $obs_date | cut -c5-6`
export day=`echo $obs_date | cut -c7-8`
export hr=`echo $obs_date | cut -c9-10`
# previous analysis time.
export FHOFFSET=`expr $ANALINC \/ 2`
export obs_datem1=`${incdate} $obs_date -$ANALINC`
# next analysis time.
export obs_datep1=`${incdate} $obs_date $ANALINC`
# beginning of current assimilation window
export obs_datem3=`${incdate} $obs_date -$FHOFFSET`
# beginning of next assimilation window
export obs_datep1m3=`${incdate} $obs_date $FHOFFSET`
export hrp1=`echo $obs_datep1 | cut -c9-10`
export hrm1=`echo $obs_datem1 | cut -c9-10`

export analdate=$obs_date

#Set CONVINFO
export CONVINFO=${enkfscripts}/textdata/global_convinfo.txt

#Set OZINFO
export OZINFO=${enkfscripts}/textdata/global_ozinfo.txt

#Set SATINFO
export SATINFO=${enkfscripts}/satinfo/global_satinfo.txt

if [ ! -z $HYBENSINFO ]; then
   /bin/cp -f ${HYBENSINFO} ${datapath}/${obs_date}/hybens_info
fi
if [ ! -z $HYBENSMOOTHINFO ];  then
   /bin/cp -f ${HYBENSMOOTHINFO} $datapath2/${obs_date}/hybens_smoothinfo
fi

#------------------------------------------------------------------------
# Main Program

#env
echo "starting the cycle (${idate_job} out of ${ndates_job})"

export datapath2="${datapath}/${obs_date}/"

# setup node parameters used in blendinc.sh and compute_ensmean_fcst.sh
export mpitaskspernode=`python -c "from __future__ import print_function; import math; print(int(math.ceil(float(${nanals})/float(${NODES}))))"`
if [ $mpitaskspernode -lt 1 ]; then
  export mpitaskspernode 1
fi
export OMP_NUM_THREADS=`expr $corespernode \/ $mpitaskspernode`
echo "mpitaskspernode = $mpitaskspernode threads = $OMP_NUM_THREADS"
export nprocs=$nanals

export CDATE=$obs_date

date
echo "obs_date minus 1: $obs_datem1"
echo "obs_date: $obs_date"
echo "obs_date plus 1: $obs_datep1"

# make log dir for obs_date
export current_logdir="${datapath2}/logs"
echo "Current LogDir: ${current_logdir}"
mkdir -p ${current_logdir}

export PREINP="${RUN}.t${hr}z."
export PREINP1="${RUN}.t${hrp1}z."
export PREINPm1="${RUN}.t${hrm1}z."

   export charnanal='ensmean' 
   export charnanal2='ensmean' 
   export lobsdiag_forenkf='.true.'
   export skipcat="false"
  #Create diag files.
   gsiobserver_start=$(date +%s)
   echo "$obs_date run gsi observer with `printenv | grep charnanal` `date`"
   sh ${enkfscripts}/run_gsiobserver.sh > ${current_logdir}/run_gsi_observer.out 2>&1
   # once observer has completed, check log files.
   gsi_done=`cat ${current_logdir}/run_gsi_observer.log`
   if [ $gsi_done == 'yes' ]; then
     echo "$obs_date gsi observer completed successfully `date`"
   else
     echo "$obs_date gsi observer did not complete successfully, exiting `date`"
     exit 1
   fi
   gsiobserver_end=$(date +%s)
   echo "run_gsiobserver.sh elapsed Time: $(($gsiobserver_end-$gsiobserver_start)) seconds"

# next obs_date: increment by $ANALINC
export obs_date=`${incdate} $obs_date $ANALINC`

echo "export obs_date=${obs_date}" > $startupenv
echo "export obs_date_end=${obs_date_end}" >> $startupenv

echo "current time is $obs_date"
export obs_date=`${incdate} $obs_date $ANALINC`
if [ $obs_date -le $obs_date_end ]; then
   echo "resubmit script"
   echo "machine = $machine"
   submit-obs-only-job.sh $machine
fi

main_end=$(date +%s)
echo "main-obs-obly.sh elapsed Time: $(($main_end-$main_start)) seconds"

exit 0

