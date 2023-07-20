#!/bin/bash

#set -x

date=$1
infoname=$2
#infos=`ls -1 textdata/global_${infoname}.txt.[12]* | sort -rn`
infos=`ls -1 textdata/global_${infoname}.txt.[12]* | sort -rn`

for info in $infos
do
  infotest=`basename $info`
  datex=`echo $infotest | cut -f3 -d"."`
  echo "date: $date, datex: $datex"
  if  [ $date -ge $datex ]; then
    info_use=$info
    break
  fi
done

echo "info_use: $info_use"

