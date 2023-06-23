#!/bin/bash
# sh submit_job.sh <machine>
if [ "$#" -eq  "0" ]
then
  machine=orion
else
  machine=$1
fi

#echo "machine: ${machine}"

cat preamble/${machine}-obs-only config/${machine}-obs-only > obs-only-job.sh

sbatch obs-only-job.sh
