#!/bin/bash

machine=orion
runtype=jedi

function show_usage () {
    printf "Usage: $0 [options [parameters]]\n"
    printf "\n"
    printf "Options:\n"
    printf " -m|--machine, which machine run on [orion | ]\n"
    printf " -r|--runtype, runtype must be of [gsi, jedi]\n"
    printf " -h|--help, Print help\n"

return 0
}

while [ ! -z "$1" ]
do
  case $1 in
    --machine|-m)
      shift
      machine=$1
     #echo "select run machine: $machine"
      shift
      ;;
    --runtype|-r)
      shift
      runtype=$1
     #echo "select runtype as: $runtype"
      shift
      ;;
   #--help|-h)
    *)
      show_usage
      ;;
  esac
done

export exptname=${runtype}-cycling

cat > config/runtype << EOF
export runtype=$runtype
export exptname=$exptname
EOF

export machine=$machine
export runtype=$runtype

if [ ! -d logs ]
then
  mkdir -p logs
fi

cold-start.sh $runtype

cyclename=${runtype}cycl
sed -e "s/CYCLENAME/${cyclename}/g" \
    -e "s/MACHINE/${machine}/g" \
       preamble/template > preamble/${machine}

cat preamble/${machine} config/${machine} > job.sh

sbatch job.sh

