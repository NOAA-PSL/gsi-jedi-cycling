#!/bin/bash

#set -x

datetime=2022010312
textdir=/work2/noaa/da/weihuang/EMC_cycling/scripts/jedi-cycling

function show_usage () {
  printf "Usage: $0 [options [parameters]]\n"
  printf "\n"
  printf "Options:\n"
  printf " -d|--datetime, which datetime run on\n"
  printf " -t|--textdir, top dir of text file\n"
  printf " -h|--help, Print help\n"
  exit 0
}

while [ ! -z "$1" ]
do
  case $1 in
    --datetime|-d)
      shift
      datetime=$1
     #echo "select datetime: $datetime"
      shift
      ;;
    --textdir|-t)
      shift
      textdir=$1
     #echo "select textdir: $textdir"
      shift
      ;;
   #--help|-h)
    *)
      show_usage
      ;;
  esac
done

for field in convinfo ozinfo satinfo
do
  infos=`ls -1 ${textdir}/textdata/${field}/global_${field}.txt.* | sort -rn`
  for info in $infos
  do
    infotest=`basename $info`
    txt_datetime=`echo $infotest | cut -f3 -d"."`

    if  [ $datetime -ge $txt_datetime ]
    then
     #echo "Choose $info"
      break
    fi
  done

  if [ -f $info ]
  then
    echo "cp $info ${textdir}/textdata/global_${field}.txt"
  fi
done

