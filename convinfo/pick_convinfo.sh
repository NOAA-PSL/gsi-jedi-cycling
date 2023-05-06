#!/bin/bash

 python gen-convinfo.py \
	--convdir=/work2/noaa/da/weihuang/cycling/scripts/gsi-cycling/convinfo \
	--datestr=2020010106 \
        --otype=uv \
        --otype=t \
        --otype=q \
        --type=120 \
        --type=210 \
        --type=220

